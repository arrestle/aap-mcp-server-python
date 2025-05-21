
from typing import List, Union
import logging

import yaml
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def parse_single_line(raw: str) -> str:
    return raw.strip() if raw else ""

def parse_text_preview(raw: str) -> List[str]:
    return raw.splitlines()[:10] if raw else []

def parse_loadavg(raw: str) -> List[float]:
    return [float(x) for x in raw.split()[:3]] if raw else []

def parse_failed_services(raw: str) -> List[str]:
    return [line for line in raw.splitlines() if "failed" in line] if raw else []

def parse_presence(raw: str) -> bool:
    return bool(raw)

def parse_error_lines(raw: str) -> List[str]:
    return [line for line in raw.splitlines() if "ERROR" in line.upper()] if raw else []

def parse_receptor_yaml(raw: str) -> Union[dict, str]:
    try:
        conf = yaml.safe_load(raw)
        return {
            "node_id": next((entry.get("node", {}).get("id") for entry in conf if "node" in entry), None),
            "log_level": next((entry.get("log-level") for entry in conf if "log-level" in entry), None),
            "port": next((entry.get("tcp-listener", {}).get("port") for entry in conf if "tcp-listener" in entry), None),
            "worktypes": [entry["work-command"]["worktype"] for entry in conf if "work-command" in entry],
            "control_socket": next((entry.get("control-service", {}).get("filename") for entry in conf if "control-service" in entry), None)
        }
    except Exception as e:
        return {"error": str(e)}
        
import codecs
import re

def decode_hex_escapes(s):
    # Replace \xNN with actual characters
    return re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: bytes.fromhex(m.group(1)).decode('utf-8', errors='replace'), s)

def parse_manifest_json(raw: str):
    try:
        data = json.loads(raw)
        files = []
        for section, contents in data:
            for file_entry in contents.get("copied_files", []):
                name = decode_hex_escapes(file_entry.get("name", ""))
                href = decode_hex_escapes(file_entry.get("href", ""))
                files.append({
                    "source": section,
                    "name": name,
                    "href": href,
                })
        return files
    except Exception as e:
        logger.exception("Failed to parse manifest_json")
        return {"error": str(e)}



PARSER_MAP = {
    "single_line": parse_single_line,
    "text_preview": parse_text_preview,
    "loadavg": parse_loadavg,
    "failed_services": parse_failed_services,
    "presence": parse_presence,
    "error_lines": parse_error_lines,
    "receptor_yaml": parse_receptor_yaml,
    "manifest_json": parse_manifest_json,
}

# import sys
# import inspect

# # Collect all functions starting with 'parse_'
# PARSER_MAP = {
#     name.replace("parse_", ""): func
#     for name, func in inspect.getmembers(sys.modules[__name__], inspect.isfunction)
#     if name.startswith("parse_")
# }