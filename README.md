```
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-multipart pyyaml

uvicorn mcp_server:app --reload
