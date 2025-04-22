import yaml
import tarfile
from datetime import datetime
from parser.extractor import extract_file_from_tar


def parse_sosreport(file_path: str, config_path="config.yaml"):
    with tarfile.open(file_path, "r:*") as tar:
        result = {
            "mcp_version": "1.0",
            "source": "ansible-sosreport",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": {}
        }

        raw = extract_file_from_tar(file_path, "proc/loadavg")
        result["payload"]["load_avg"] = [float(x) for x in raw.split()[:3]] if raw else []

        return result