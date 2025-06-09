# tools/job_lifecycle_tool.py
from mcp_parser import job_lifecycle

def run_tool(llm_output: str) -> str:
    sos_path = "/var/mcp/sosreport"
    findings = job_lifecycle.parse_job_lifecycle_logs(sos_path)
    return f"Job Lifecycle Findings:\n{findings}"
