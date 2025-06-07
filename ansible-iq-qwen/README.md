### Background

With the rise of automated infrastructure management via Ansible, post-mortem diagnostics and root cause analysis using SOS reports have become essential. These reports are verbose and often require expert interpretation. 

Ansible IQ is a local, intelligent assistant that helps operators analyze Ansible SOS reports using a small, locally-hosted LLM (Qwen via Ollama) without requiring a GPU. The system also includes an MCP server to manage and serve reports, and an AI Agent component to coordinate communication and drive logic-based insights.

This solution is optimized for air-gapped, low-resource environments like field operations or secure enterprise laptops.

### Requirements

*Must Have*
- M: Ability to parse and summarize SOS reports via `parse_sos_report()`
- M: Interactive TUI for querying parsed SOS reports
- M: LLM response streamed incrementally to the TUI (Markdown)
- M: Local AI agent integration via HTTP (`/mcp/qwen3`)
- M: Run on CPU-only laptops (no GPU dependencies)
- M: Markdown rendering of SOS summaries and AI responses

*Should Have*
- S: Asynchronous input/output for UI responsiveness
- S: Error feedback when model or MCP server is unavailable

*Could Have*
- C: Offline LLM inferencing (via Ollama + Qwen)
- C: Keyboard shortcuts for common queries

*Won't Have (for MVP)*
- W: GUI version
- W: Remote file syncing
- W: Cloud-based inference


```bash
cd ansible-iq-qwen
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

ollama list # make sure qwen is running, if not:
ollama pull qwen3:0.6b
ps -aux | grep ollama # make sure it's running, if not:
ollama serve # servers all available models

pip install -r requirements.txt # insall dependencies
uvicorn sos_report:app --reload # start the mcp server

## If ollama is not running locally already:

curl -L https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64.tgz  -o ollama.tgz
tar xvf ollama.tgz
scp ollama localhost:/usr/local/bin/

chmod +x /usr/local/bin/ollama
ollama pull qwen3:0.6b
ollama serve

## If running as a systemd
systemctl status ollama
ollama pull qwen3:0.6b
sudo systemctl restart ollama

podman build -t ansible-iq -f Dockerfile


## To rebuild.
podman container list
podman stop ansible-iq
podman rm ansible-iq
podman rmi ansible-iq
podman build -t ansible-iq -f Dockerfile


## run podman
podman run -d \
  --name ansible-iq \
  -p 8000:8000 \
  -v /var/mcp:/var/mcp \
  --userns=keep-id \
  ansible-iq

# copy in your sos report
podman exec -it ansible-iq mkdir -p /var/mcp
.venvarestlel:ansible-iq-qwen$ podman cp /var/mcp/sosreport ansible-iq:/var/mcp/sosreport
```



