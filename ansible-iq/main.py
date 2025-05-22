import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from mcp_parser import tool as mcp_tool

import requests
from typing import Optional

app = FastAPI()

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
from tools import samba_tool, job_lifecycle_tool, dispatcher_tool, firewall_tool, receptor_tool

TOOL_REGISTRY = {
    "analyze_samba": samba_tool.run_tool,
    "analyze_jobs": job_lifecycle_tool.run_tool,
    "analyze_dispatcher": dispatcher_tool.run_tool,
    "analyze_firewall": firewall_tool.run_tool,
    "analyze_receptor": receptor_tool.run_tool,
}


# --- Pydantic Model ---
class MCPRequest(BaseModel):
    prompt: str
    tool: Optional[str] = None

# --- Routing Logic ---
def route_prompt(prompt: str):
    lower_prompt = prompt.lower()
    if "samba" in lower_prompt:
        return "analyze_samba"
    elif any(word in lower_prompt for word in ["job", "lifecycle", "task", "awx"]):
        return "analyze_jobs"
    elif any(word in lower_prompt for word in ["dispatcher", "periodic", "scheduler"]):
        return "analyze_dispatcher"
    elif any(word in lower_prompt for word in ["firewall", "nt_status_authentication_firewall_failed"]):
        return "analyze_firewall"
    elif any(word in lower_prompt for word in ["receptor", "mesh", "node id", "control socket"]):
        return "analyze_receptor"
    return None


# --- Main Handler ---
@app.post("/mcp/qwen3")
def handle_request(req: MCPRequest):
    
    log = logging.getLogger(__name__)
    
    # Step 1: Determine tool
    tool = route_prompt(req.prompt)


    # Step 2: Ask LLM
    ollama_payload = {
        "model": "qwen3:0.6b",
        "prompt": req.prompt,
        "stream": False
    }
    
    # Step 3: If tool is found, run it and modify the prompt
    if tool and tool in TOOL_REGISTRY:
        tool_output = TOOL_REGISTRY[tool](req.prompt)
        log.info(f"Tool {tool} output: {tool_output}")
        wrapped_prompt = f"""
        You are an Ansible support engineer at Red Hat.

        You are analyzing a parsed Ansible SOS report from an AAP customer environment.

        - If logs are mentioned, extract context from files like `receptor.log`, `dispatcher.log`, `job_lifecycle.log`, or Samba logs.
        - Be concise but technical.
        - Summarize failure causes, recommend diagnostic steps, and suggest next actions.
        - If a known pattern or error message is found, explain it clearly.

        Customer Question:
        {req.prompt}
        """
        ollama_payload["prompt"] = wrapped_prompt
        ollama_payload["tool"] = tool
        ollama_payload["tool_output"] = tool_output
        
    print(f"Request to Ollama: {ollama_payload}")
    
    response = requests.post(OLLAMA_ENDPOINT, json=ollama_payload)
    print(f"Response from Ollama: {response.text}")
    ollama_response = requests.post(OLLAMA_ENDPOINT, json=ollama_payload)

    try:
        result_json = ollama_response.json()
    except Exception as e:
        return {"error": "Invalid JSON from Ollama", "details": str(e)}

    if ollama_response.status_code != 200:
        return {
            "error": "Ollama request failed",
            "status_code": ollama_response.status_code,
            "ollama_response": result_json,
        }

    llm_output = result_json.get("response")  # Use .get to avoid KeyError

    if not llm_output:
        return {
            "error": "Ollama response missing 'response' field",
            "ollama_raw": result_json,
        }
    
    return {"llm_output": llm_output}