
import sys
import tarfile
import yaml
import json
from datetime import datetime, timezone
from tools.correlate_firewall_failures import correlate_firewall_failures
from tools.dispatcher import inspect_dispatcher_log
from tools.job_lifecycle import parse_job_lifecycle_logs
from tools.samba_inspector import inspect_samba_logs
from output_models import MCPReport
from parsers import PARSER_MAP
import logging
from collections import Counter

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def parse_from_config(tar: tarfile.TarFile, config: dict):
    payload = {}
    for entry in config.get("priority_files", []):
        parser_fn = PARSER_MAP.get(entry["parser"])
        if not parser_fn:
            continue
        match = next((m for m in tar.getnames() if m.endswith(entry["path"])), None)
        if not match:
            continue
        try:
            f = tar.extractfile(match)
            raw = f.read().decode(errors="replace") if f else ""
            payload[entry["key"]] = parser_fn(raw)
        except Exception as e:
            payload[entry["key"]] = {"error": str(e)}
    return payload

def parse_sos_report(tar_path):
    with tarfile.open(tar_path, "r:*") as tar:
        config = load_config()
        payload = parse_from_config(tar, config)
        samba_result = inspect_samba_logs(tar_path, max_lines=100)
        payload["samba_findings"] = [f.model_dump() for f in samba_result["entries"]]
        payload["samba_summary"] = samba_result["summary"]

    # Inject job lifecycle findings into payload
    payload["job_lifecycle_logs"] = parse_job_lifecycle_logs(tar_path)

    # Flatten all entries across all log sources
    all_entries = []
    for log in payload["job_lifecycle_logs"]:
        all_entries.extend(log.get("entries", []))

    # Count states
    state_counts = Counter(entry.get("state", "unknown") for entry in all_entries)

    # Inject summary into payload
    payload["job_lifecycle_summary"] = dict(state_counts)

    dispatcher_findings = inspect_dispatcher_log(tar_path)

    payload["dispatcher"] = [f.__dict__ for f in dispatcher_findings]

    summary = []

    # From samba summary
    firewall_issues = samba_result["summary"].get("FIREWALL_FAILED", 0)
    if firewall_issues > 0:
        summary.append(f"Detected {firewall_issues} 'FIREWALL_FAILED' events in Samba logs — possible firewall misconfiguration.")

    # From task_system_logs
    task_logs = payload.get("task_system_logs", {}).get("entries", [])
    unit_errors = [e for e in task_logs if "unknown work unit" in e.get("exception", "").lower()]
    if unit_errors:
        summary.append(f"Detected {len(unit_errors)} 'unknown work unit' errors in Receptor — may indicate job sync/network issues.")

    # From dispatcher drift
    drift_findings = payload.get("dispatcher", [])
    late = [f for f in drift_findings if float(f.get("drift", 0)) > 0.05]
    if late:
        summary.append(f"Scheduler drift over 0.05s found in {len(late)} events — may suggest timing or load issues.")

    # Inject
    payload["summary"] = summary

    payload["summary"] += correlate_firewall_failures(payload)


    report = MCPReport(
        source="ansible-sosreport",
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=payload,
        dispatcher=dispatcher_findings,
        samba_findings=samba_result["entries"],
        samba_summary=samba_result["summary"],
        job_lifecycle_logs=payload["job_lifecycle_logs"],
        job_lifecycle_summary=payload["job_lifecycle_summary"]
    )

    return report.model_dump()

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) != 2:
        print("Usage: python main.py <sosreport.tar.xz>")
        sys.exit(1)

    result = parse_sos_report(sys.argv[1])
    print(json.dumps(result, indent=2))
