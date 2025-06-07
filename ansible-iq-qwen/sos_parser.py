import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from tools import samba_tool, job_lifecycle_tool, dispatcher_tool, firewall_tool, receptor_tool
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Welcome to Ansible IQ MCP Server"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "MCP Server", "uptime": "N/A"}

# === Configuration ===
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

# === Models ===
class MCPRequest(BaseModel):
    prompt: str
    tool: Optional[str] = None

# === Mock Tools (Replace with real ones later) ===
def mock_samba_tool(prompt):
    return "[MOCK] Samba config issue detected."

def mock_job_tool(prompt):
    return "[MOCK] Job failed due to timeout."

TOOL_REGISTRY = {
    "analyze_samba": samba_tool.run_tool,
    "analyze_jobs": job_lifecycle_tool.run_tool,
    "analyze_dispatcher": dispatcher_tool.run_tool,
    "analyze_firewall": firewall_tool.run_tool,
    "analyze_receptor": receptor_tool.run_tool,
}

# === Tool Routing Logic ===
def route_prompt(prompt: str) -> str:
    prompt = prompt.lower()
    if "samba" in prompt:
        return "analyze_samba"
    elif "job" in prompt or "task" in prompt:
        return "analyze_jobs"
    else:
        return ""

# === Streaming Function ===
def generate_ollama_response(final_prompt: str):
    payload = {
        "model": "qwen3:0.6b",
        "prompt": final_prompt,
        "stream": True
    }

    try:
        with requests.post(OLLAMA_ENDPOINT, json=payload, stream=True) as response:
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    yield chunk
    except Exception as e:
        yield f"[ERROR] Failed to get response from Ollama: {str(e)}"

# === Final Prompt Wrapper ===
def build_final_prompt(prompt: str, tool_output: str = ""):
    return f"""
You are an Ansible support engineer at Red Hat.
You are analyzing a parsed Ansible SOS report from an AAP customer environment.

Your task is to:
- Identify patterns in logs provided by tools
- Explain known error messages clearly
- Recommend actionable next steps

Output format:
1. Summary of issue
2. Root cause analysis
3. Recommended actions

Customer Question:
{prompt}

Tool Output:
{tool_output}
"""

# === Main Endpoint ===
@app.post("/mcp/qwen3")
async def handle_request(req: MCPRequest):
    log = logging.getLogger(__name__)
    
    # Step 1: Determine tool
    tool = route_prompt(req.prompt)

    # Step 2: Run tool if found
    tool_output = ""
    if tool and tool in TOOL_REGISTRY:
        tool_output = TOOL_REGISTRY[tool](req.prompt)
        log.info(f"Tool {tool} output: {tool_output}")

    # Step 3: Build final prompt
    final_prompt = build_final_prompt(req.prompt, tool_output)

    # Step 4: Stream response from Ollama
    return StreamingResponse(
        generate_ollama_response(final_prompt),
        media_type="text/event-stream"
    )