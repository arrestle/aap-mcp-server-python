import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from parser.sos import parse_sosreport

app = FastAPI(title="Hybrid MCP SOS Server")

@app.post("/parse/")
async def upload_and_parse(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.xz") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        mcp = parse_sosreport(tmp_path)
        return JSONResponse(content=mcp)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        os.remove(tmp_path)