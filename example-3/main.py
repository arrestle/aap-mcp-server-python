from fastapi import FastAPI, Request
from pydantic import BaseModel
from tools import samba_analyzer
import requests
from typing import Optional

app = FastAPI()

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
TOOL_REGISTRY = {
    "analyze_samba": samba_analyzer.run_tool,
}


# --- Pydantic Model ---
class MCPRequest(BaseModel):
    prompt: str
    tool: Optional[str] = None

# --- Routing Logic ---
def route_prompt(prompt: str):
    if "samba" in prompt.lower():
        return "analyze_samba"
    return None


# --- Main Handler ---
@app.post("/mcp/qwen3")
def handle_request(req: MCPRequest):
    # Step 1: Determine tool
    tool = route_prompt(req.prompt)

    # Step 2: Ask LLM
    ollama_payload = {
        "model": "qwen3:0.6b",
        "prompt": req.prompt,
        "stream": False
    }
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

    # Step 3: Optionally run tool
    if tool and tool in TOOL_REGISTRY:
        tool_result = TOOL_REGISTRY[tool](llm_output)
        return {"llm_output": llm_output, "tool_output": tool_result}
    
    return {"llm_output": llm_output}