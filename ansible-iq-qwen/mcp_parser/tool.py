# ansible-iq/mcp_parser/tool.py

import os

DEFAULT_SOS_PATH = "/var/mcp/sosreport"

def run_tool(llm_output: str) -> str:
    """
    Primary interface for invoking MCP analysis tooling from a FastAPI prompt.
    """

    if not os.path.exists(DEFAULT_SOS_PATH):
        return f"❌ No SOS report found at {DEFAULT_SOS_PATH}"

    # Placeholder logic for now
    return (
        f"MCP tool invoked with LLM context:\n\n"
        f"{llm_output}\n\n"
        f"Would analyze SOS report at: {DEFAULT_SOS_PATH}\n"
    )