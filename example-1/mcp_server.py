# mcp_server.py
import os
import logging
import yaml
import tarfile
import tempfile
from datetime import datetime, timedelta

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp")

app = FastAPI(title="Ansible SOS MCP Server")

def load_config(yaml_path="config.yaml"):
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)

def parse_sosreport(file_path: str, config_path="config.yaml"):
    config = load_config(config_path)
    result = {
        "mcp_version": config.get("mcp_version", "1.0"),
        "source": "ansible-sosreport",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": {},
        "tags": {}
    }

    with tarfile.open(file_path, "r:*") as tar:
        members = tar.getnames()

        def extract(path_suffix):
            match = next((m for m in tar.getnames() if m.endswith(path_suffix)), None)
            if match:
                try:
                    f = tar.extractfile(match)
                    return f.read().decode() if f else None
                except Exception:
                    return None
            return None

        for entry in config.get("priority_files", []):
            raw = extract(entry["path"])
            key = entry["key"]
            parser = entry.get("parser")

            if parser == "loadavg":
                value = [float(x) for x in raw.split()[:3]] if raw else []
            elif parser == "failed_services":
                value = [line for line in raw.splitlines() if "failed" in line] if raw else []
            elif parser == "single_line":
                value = raw.strip() if raw else ""
            elif parser == "text_preview":
                value = raw.splitlines()[:10] if raw else []
            elif parser == "presence":
                value = bool(raw)
            elif parser == "receptor_yaml":
                try:
                    conf = yaml.safe_load(raw)
                    out = {
                        "node_id": next((entry.get("node", {}).get("id") for entry in conf if "node" in entry), None),
                        "log_level": next((entry.get("log-level") for entry in conf if "log-level" in entry), None),
                        "port": next((entry.get("tcp-listener", {}).get("port") for entry in conf if "tcp-listener" in entry), None),
                        "worktypes": [entry["work-command"]["worktype"] for entry in conf if "work-command" in entry],
                        "control_socket": next((entry.get("control-service", {}).get("filename") for entry in conf if "control-service" in entry), None)
                    }
                    value = out
                except Exception as e:
                    value = {"error": str(e)}
            elif parser == "error_lines":
                value = [line for line in raw.splitlines() if "ERROR" in line.upper()] if raw else []

            elif parser == "samba_errors":
                value = []
                ERROR_KEYWORDS = ["error", "nt_status", "not supported", "denied", "refused", "failure", "failed"]
                samba_members = [m for m in tar.getnames() if "samba" in m.lower() and "old" not in m.lower()]

                logger.info(f"samba members: {samba_members}")

                for member in samba_members:
                    try:
                        f = tar.extractfile(member)
                        if not f:
                            continue
                        lines = f.read().decode(errors="replace").splitlines()

                        # filter for relevant errors only
                        error_lines = [line for line in lines if any(term in line.lower() for term in ERROR_KEYWORDS)]
                        if not error_lines:
                            continue

                        logger.info(f"🗂️ {member}")
                        for preview_line in error_lines[:5]:
                            logger.info(f"   {preview_line.strip()}")

                        value.extend(f"{member}: {line.strip()}" for line in error_lines)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to process {member}: {e}")
                        continue
                value = value[-100:]

            if key == "host_id":
                result["host_id"] = value
            else:
                result["payload"][key] = value

    return result

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
