import tarfile
import os
from pathlib import Path

def parse_sos_report(tar_path: str) -> str:
    """
    Quick summary extractor for SOS report content — meant for UI priming.
    """
    if not os.path.exists(tar_path):
        return f"❌ SOS report not found: {tar_path}"

    summary = [f"# 🧾 SOS Report Summary\n\n**Source:** `{tar_path}`"]

    try:
        with tarfile.open(tar_path, "r:*") as tar:
            members = tar.getnames()
            summary.append(f"- Total files: `{len(members)}`")

            log_files = [m for m in members if m.endswith(".log")]
            summary.append(f"- Log files: `{len(log_files)}`")

            interesting = [
                m for m in members
                if any(x in m.lower() for x in ["dispatcher", "samba", "job_lifecycle", "fail", "warn"])
            ]

            if interesting:
                summary.append("\n## 🔍 Notable Matches:")
                for m in interesting[:10]:  # limit output
                    summary.append(f"- `{m}`")

    except Exception as e:
        summary.append(f"\n❌ Error reading archive: {e}")

    return "\n".join(summary)
