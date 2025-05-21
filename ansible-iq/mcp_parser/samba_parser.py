import tarfile
import logging

from collections import Counter

from mcp_parser.output_models import SambaFinding

DEFAULT_SOS_PATH = "/var/mcp/sosreport"

logger = logging.getLogger("samba_inspector")

ERROR_KEYWORDS = ["error", "nt_status", "not supported", "denied", "refused", "failure", "failed"]

def contains_error(line):
    return any(term in line.lower() for term in ERROR_KEYWORDS)

def inspect_samba_logs(tar_path, max_lines=100):
    findings = []
    total_matched = 0
    keyword_counter = Counter()

    with tarfile.open(tar_path, "r:*") as tar:
        members = [m for m in tar.getnames() if "samba" in m.lower() and "old" not in m.lower()]
        for member in members:
            if total_matched >= max_lines:
                break

            try:
                f = tar.extractfile(member)
                if not f:
                    continue

                lines = f.read().decode(errors="replace").splitlines()
                for i, line in enumerate(lines):
                    if contains_error(line):
                        matched_keywords = [term.upper() for term in ERROR_KEYWORDS if term in line.lower()]
                        keyword_counter.update(matched_keywords)

                        findings.append(SambaFinding(
                            source=member,
                            line_number=i + 1,
                            finding=line.strip(),
                            severity="warning",
                            component="samba"
                        ))
                        total_matched += 1
                        if total_matched >= max_lines:
                            break

            except Exception as e:
                findings.append(SambaFinding(
                    source=member,
                    error=str(e),
                    severity="error",
                    component="samba"
                ))

    return {
        "entries": findings,
        "summary": dict(keyword_counter)
    }

