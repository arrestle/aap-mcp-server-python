# tools/job_lifecycle_tool.py
from mcp_parser import job_lifecycle

def run_tool(llm_output: str) -> str:
    sos_path = "/var/mcp/sosreport"
    findings = job_lifecycle.parse_job_lifecycle_logs(DEFAULT_SOS_PATH, max_lines=100)
    
    if not findings:
        return "No job lifecycle logs found or failed to parse."

    # Create a list to hold the findings
    findings_list = []
    
    # Create a summary of findings
    summary = []
    
    for f in findings:
        source_info = f"Source: {f['source']}\n"
        entries = "\n".join(f"  - {entry}" for entry in f.get("entries", []))
        
        # Append the findings for this source
        findings_list.append(source_info + entries)
        
        # Create a summary entry
        summary.append(f"{f['source']} has {len(f.get('entries', []))} entries.")

    # Combine findings and summary
    findings_and_summary = "\n\n".join(findings_list)
    summary_string = "\n".join(summary)

    # Return both findings and summary
    return f"Findings:\n{findings_and_summary}\n\nSummary:\n{summary_string}"



def run_tool_structured() -> str:
    sos_path = "/var/mcp/sosreport"
    findings = job_lifecycle.parse_job_lifecycle_logs(sos_path, max_lines=100)
    return findings
