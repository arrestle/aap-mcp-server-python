### For all projects here:
```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-multipart pyyaml mcp json_rpc

ollama pull phi4:14b
```
### Example-1 is a single file python program with a config.yaml specifying important files.
This example only implements a fastapi RESTful interface
```
cd example-1
uvicorn mcp_server:app --reload
```

### Example-2  also implement FastMCP but maintains the FASTAPI endpoints as well.
```
cd example-2
PYTHONPATH=. python main.py --http
```

### mcp_parser

Copy your tarball sosreports into the tar folder.

```bash
cd mcp_parser...
python main.py ../tar/sosreport-VA807527-04112973-2025-04-11-frwjgxp.tar.xz > sos.json # create a parsed json file
uvicorn mcp_server:app --reload

 python sos_chat_tui.py ../tar/sosreport-VA807527-04112973-2025-04-11-frwjgxp.tar.xz 

# References
* [Claude and MCP](https://github.com/agardnerIT/claude-mcp-server-observability)
