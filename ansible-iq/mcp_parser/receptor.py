# mcp_parser/receptor.py

import tarfile
import re

def parse_receptor_logs(tar_path: str, max_lines: int = 50):
    findings = []
    log_patterns = [
        re.compile(r"error", re.IGNORECASE),
        re.compile(r"connection (failed|reset|refused)", re.IGNORECASE),
        re.compile(r"reconnect", re.IGNORECASE),
        re.compile(r"node .*? offline", re.IGNORECASE),
    ]

    try:
        with tarfile.open(tar_path, "r:*") as tar:
            members = [m for m in tar.getnames() if "receptor.log" in m.lower()]
            for member in members:
                try:
                    f = tar.extractfile(member)
                    if not f:
                        continue

                    lines = f.read().decode(errors="replace").splitlines()
                    matched_lines = [line for line in lines if any(p.search(line) for p in log_patterns)]

                    findings.append({
                        "source": member,
                        "entries": matched_lines[:max_lines]
                    })
                except Exception as e:
                    findings.append({
                        "source": member,
                        "error": str(e)
                    })
    except Exception as outer:
        findings.append({
            "source": "parse_receptor_logs",
            "error": str(outer)
        })

    return findings
