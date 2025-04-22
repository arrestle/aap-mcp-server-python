### Example-1 is a single file python program with a config.yaml specifying important files.
This example only implements a fastapi RESTful interface
```
python -m venv .venv
source .venv/bin/activate
cd example-1
pip install fastapi uvicorn python-multipart pyyaml

uvicorn mcp_server:app --reload
```

### Example-2  also implement FastMCP but maintains the FASTAPI endpoints as well.
```
python -m venv .venv
source .venv/bin/activate
cd example-2
pip install fastapi uvicorn python-multipart pyyaml mcp

PYTHONPATH=. python main.py --http

```
# References
* [Claude and MCP](https://github.com/agardnerIT/claude-mcp-server-observability)