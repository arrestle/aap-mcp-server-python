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

### DEMO

![Ansible IQ Demo](assets/demo.gif)

```bash
cd podman
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pip install -U "huggingface_hub[cli]"
huggingface-cli login
huggingface-cli download Antigma/Qwen3-1.7B-GGUF --local-dir ./qwen3-1.7b --local-dir-use-symlinks False
huggingface-cli download Antigma/Qwen3-1.7B-GGUF --include "*.gguf" --local-dir ./models
ll models

sudo dnf install cmake gcc-c++ python3-pip
CMAKE_ARGS="-DLLAMA_AVX2=on" pip install --force-reinstall --no-cache-dir llama-cpp-python

# Install llama.cpp from https://github.com/ggml-org/llama.cpp/releases and move the files into the .bin folder
# This did not work for me. I got stack dumps.

git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp

cmake -B build -DCMAKE_BUILD_TYPE=Debug -DLLAMA_CURL=OFF # set up the makefile.
cmake --build build --config Release -j$(nproc) # actually perform the make
mv build/* ../bin

export LD_LIBRARY_PATH=$PWD/bin:$LD_LIBRARY_PATH

./bin/llama-cli -m models/qwen3-1.7b-q4_0.gguf -p "hello"
./bin/llama-cli  -m models/qwen3-1.7b-q4_k_m.gguf --verbose-prompt 2>&1 | grep -E 'model|quant|context'

## disable any unnecessary systemd services
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
# Prometheus Node Exporter
sudo systemctl stop prometheus-node-exporter.service
sudo systemctl disable prometheus-node-exporter.service

# Splunk Forwarder
sudo systemctl stop SplunkForwarder.service
sudo systemctl disable SplunkForwarder.service

# OLLAMA
sudo systemctl stop ollama.service
sudo systemctl disable ollama.service


# start up the mcp server sos_parser
uvicorn sos_parser:app --reload

# check the endpoints
curl http://127.0.0.1:8000/health

curl -X POST "http://127.0.0.1:8000/mcp/all-tools" \
  -H "Content-Type: application/json" \
  -d '{"prompt": ""}'
# -or-
 curl -X POST "http://127.0.0.1:8000/mcp/all-tools"   -H "Content-Type: application/json"   -d '{"prompt": ""}' > podman.json 

 #
 ```

 ## TODO
 1. sos report is currently stringified - needs to be more structured.
 2. connect agent to  mcp server (sos_parser.py)
 3. connect tui to agent
 4. 