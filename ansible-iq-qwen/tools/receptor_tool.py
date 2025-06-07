# tools/receptor_tool.py
import tarfile
import re
import os

DEFAULT_SOS_PATH = "/var/mcp/sosreport"
RECEPTOR_LOG_PATTERNS = [
    re.compile(r"error", re.IGNORECASE),
    re.compile(r"connection (failed|reset|refused)", re.IGNORECASE),
    re.compile(r"reconnect", re.IGNORECASE),
    re.compile(r"node .*? offline", re.IGNORECASE),
]

def run_tool(llm_output: str) -> str:
    if not os.path.exists(DEFAULT_SOS_PATH):
        return f"❌ SOS report not found at {DEFAULT_SOS_PATH}"

    findings = []
    try:
        with tarfile.open(DEFAULT_SOS_PATH, "r:*") as tar:
            for member in tar.getnames():
                if "receptor.log" in member.lower():
                    f = tar.extractfile(member)
                    if not f:
                        continue
                    lines = f.read().decode(errors="replace").splitlines()
                    for line in lines:
                        if any(p.search(line) for p in RECEPTOR_LOG_PATTERNS):
                            findings.append(line.strip())
    except Exception as e:
        return f"❌ Failed to analyze receptor.log: {e}"

    if not findings:
        return "✅ No issues found in receptor.log."

    return f"🔍 Receptor log findings:\n" + "\n".join(findings[:20])
