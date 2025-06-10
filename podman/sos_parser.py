import logging
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

import uvicorn
from tools import samba_tool, job_lifecycle_tool, dispatcher_tool, receptor_tool
from structured_agent import StructuredAgent, AnalysisResult
import requests
import re
import sys


class MCPRequest(BaseModel):
    prompt: str  # Required user input/question
    tool: Optional[str] = None  # Optional tool specification


# Set up root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Ensures logs go to stdout
    ]
)

log = logging.getLogger(__name__)


app = FastAPI()
router = APIRouter()
agent = StructuredAgent("models/qwen3-1.7b-q4_0.gguf")

@router.post("/analyze-sos", response_model=AnalysisResult)
async def analyze_sos_endpoint(payload: dict):
    """Endpoint for SOS report analysis"""
    try:
        return agent.analyze_sos(payload.get("sos_text", ""))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Welcome to Ansible IQ MCP Server"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "MCP Server", "uptime": "N/A"}

@app.post("/mcp/all-tools")
async def get_all_tools_output(req: MCPRequest):
    """Endpoint to execute all registered tools and return aggregated outputs"""
    all_outputs = []
    
    for tool_name, tool_func in STRUCTURED_REGISTRY.items():
        try:
            tool_output = tool_func()
            all_outputs.append({
                "tool": tool_name,
                "output": tool_output,
                "status": "success"
            })
            log.info(f"Successfully executed {tool_name}")
        except Exception as e:
            all_outputs.append({
                "tool": tool_name,
                "error": str(e),
                "status": "failed"
            })
            log.error(f"Tool {tool_name} failed: {str(e)}")

    return {"tools": all_outputs}
    

# === Configuration ===
#OLLAMA_ENDPOINT = "http://127.0.0.1:11434/api/generate" # outside of container
OLLAMA_ENDPOINT = "http://host.containers.internal:11434/api/generate"

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
    "analyze_receptor": receptor_tool.run_tool,
}

STRUCTURED_REGISTRY = {
    "analyze_samba": samba_tool.run_tool_structured,
    "analyze_jobs": job_lifecycle_tool.run_tool_structured,
    "analyze_dispatcher": dispatcher_tool.run_tool_structured,
    "analyze_receptor": receptor_tool.run_tool_structured,
}   


# === Tool Routing Logic ===
def route_prompt(prompt: str) -> str:
    prompt = prompt.lower().strip()

    if re.search(r"\b(samba|cifs|smb|network|firewall|iptables|policy|nt_status)\b", prompt):
        return "analyze_samba"
    
    elif re.search(r"\b(job|task|playbook|ansible|awx)\b", prompt):
        return "analyze_jobs"

    elif re.search(r"\b(dispatcher|scheduler|schedule|periodic)\b", prompt):
        return "analyze_dispatcher"

    elif re.search(r"\b(receptor|mesh|socket|node id|node identity)\b", prompt):
        return "analyze_receptor"

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
    
    log.info(f"Routing prompt to tool: {tool} for prompt: {req.prompt}")

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
    
    
if __name__ == "__main__":
    uvicorn.run(
        "sos_report:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        reload_includes=["*.py", "*.json"]  # Explicit reload targets
    )
