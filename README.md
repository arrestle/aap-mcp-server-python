### For all projects here:
```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-multipart pyyaml mcp json_rpc

ollama pull phi4:14b
ollama pull qwen3:0.6b
ollama serve # servers all available models
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

### Example-3 mcp server from scratch

make sure ollama is running qwen3:0.6b
```
$ ps -aux | grep -i ollama
ollama      1933  0.0  0.0 2223700 29884 ?       Ssl  11:14   0:00 /usr/local/bin/ollama serve
arestlel  389077  0.0  0.0 230348  2196 pts/6    S+   15:27   0:00 grep --color=auto -i ollama
$ sudo ss -ltnp | grep ollama
[sudo] password for arestlel: 
LISTEN 0      4096       127.0.0.1:11434      0.0.0.0:*    users:(("ollama",pid=1933,fd=3))  

curl http://127.0.0.1:11434/api/generate \
  -d '{
    "model": "qwen3:0.6b",
    "prompt": "What model is running?",
    "stream": false
  }'
{"model":"qwen3:0.6b","created_at":"2025-05-21T19:31:32.28532585Z","response":"\u003cthink\u003e\nOkay, ...
```
If that is all running correctly then:

```bash

cd example-3
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# in another terminal
cd mcp_parser


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
