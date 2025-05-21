### For all projects here:
```bash
cd ansible-iq
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

ollama pull qwen3:0.6b
ollama serve # servers all available models (may already be running)

pip install -r requirements.txt # insall dependencies
uvicorn main:app --reload # start the mcp server

curl http://127.0.0.1:8000/mcp/qwen3 # mcp server available here

sudo  mkdir /var/mcp
sudo cp <your sos report> /var/mcp/sosreport # hardcoded for now.

python sos_chat_tui.py /var/mcp/sosreport