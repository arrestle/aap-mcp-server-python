# tools/job_lifecycle_tool.py

from mcp_parser import job_lifecycle

DEFAULT_SOS_PATH = "/var/mcp/sosreport"

def run_tool(llm_output: str) -> str:
    findings = job_lifecycle.parse_job_lifecycle_logs(DEFAULT_SOS_PATH, max_lines=100)
    if not findings:
        return "No job lifecycle logs found or failed to parse."

    summary = [f"Source: {f['source']}\n" + "\n".join(
        f"  - {entry}" for entry in f.get("entries", [])
    ) for f in findings]
    
    findings_and_summary = [f"Source: {f['source']}\n" + "\n".join(
        f"  - {entry}" for entry in f.get("entries", [])
    ) for f in findings]

    return "\n\n".join(findings_and_summary)


def run_tool_structured() -> str:
    findings = job_lifecycle.parse_job_lifecycle_logs(DEFAULT_SOS_PATH, max_lines=100)
    if not findings:
        return "No job lifecycle logs found or failed to parse."

    return findings