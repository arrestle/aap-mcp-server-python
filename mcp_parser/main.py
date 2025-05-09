
import sys
import tarfile
import yaml
import json
from datetime import datetime, timezone
from tools.job_lifecycle import parse_job_lifecycle_logs
from tools.samba_inspector import inspect_samba_logs
from output_models import MCPReport
from parsers import PARSER_MAP
import logging

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
        samba_findings = inspect_samba_logs(tar_path, max_lines=10)

    # Inject job lifecycle findings into payload
    payload["job_lifecycle_logs"] = parse_job_lifecycle_logs(tar_path)

    report = MCPReport(
        source="ansible-sosreport",
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=payload,
        samba_findings=samba_findings
    )
    return report.model_dump()

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) != 2:
        print("Usage: python main.py <sosreport.tar.xz>")
        sys.exit(1)

    result = parse_sos_report(sys.argv[1])
    print(json.dumps(result, indent=2))
