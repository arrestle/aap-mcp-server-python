from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from json_rpc import JsonRpc
import tempfile
import shutil

from parse_sos_report import parse_sos_report

app = FastAPI()
rpc = JsonRpc()

@rpc.method()
async def predict(file: UploadFile) -> dict:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tar_path = tmp.name

    try:
        payload = parse_sos_report(tar_path)
        return payload
    except Exception as e:
        return {"error": str(e)}

app.mount("/rpc", rpc)
