# tools/firewall_tool.py

from mcp_parser import correlate_firewall_failures
import json

DEFAULT_SOS_JSON = "/var/mcp/parsed_sosreport.json"

def run_tool(llm_output: str) -> str:
    if not os.path.exists(DEFAULT_SOS_JSON):
        return f"❌ Expected parsed SOS report at {DEFAULT_SOS_JSON}"

    try:
        with open(DEFAULT_SOS_JSON) as f:
            payload = json.load(f)
    except Exception as e:
        return f"❌ Failed to load parsed SOS report: {e}"

    insights = correlate_firewall_failures.correlate_firewall_failures(payload)
    return "\n".join(insights) if insights else "✅ No firewall-related failures found."
