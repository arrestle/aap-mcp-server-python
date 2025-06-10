import tarfile
import logging
from collections import Counter
from mcp_parser.output_models import SambaFinding
import os

DEFAULT_SOS_PATH = "/var/mcp/sosreport"
logger = logging.getLogger("samba_inspector")

class SambaFindingCache:
    def __init__(self):
        self.findings = []
        self.total_matched = 0
        self.keyword_counter = Counter()

    def add_finding(self, finding):
        self.findings.append(finding)

    def get_findings(self):
        return self.findings

ERROR_KEYWORDS = ["error", "nt_status", "not supported", "denied", "refused", "failure", "failed"]
FIREWALL_KEYWORDS = ["firewall"]

def contains_error(line):
    line_lower = line.lower()
    return any(term in line_lower for term in ERROR_KEYWORDS)

def contains_firewall_failure(line):
    return "nt_status_authentication_firewall_failed" in line.lower()

def inspect_samba_logs(tar_path, max_lines=100):
    cache = SambaFindingCache()
    
    with tarfile.open(tar_path, "r:*") as tar:
        members = [m for m in tar.getnames() if "samba" in m.lower() and "old" not in m.lower()]
        for member in members:
            if cache.total_matched >= max_lines:
                break

            try:
                f = tar.extractfile(member)
                if not f:
                    continue

                lines = f.read().decode(errors="replace").splitlines()
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    is_error = contains_error(line_lower)
                    is_firewall = contains_firewall_failure(line_lower)

                    if not (is_error or is_firewall):
                        continue

                    # Prioritize firewall failures
                    if is_firewall:
                        component = "firewall"
                        severity = "critical"
                        keywords = FIREWALL_KEYWORDS
                    else:
                        component = "samba" 
                        severity = "warning"
                        keywords = ERROR_KEYWORDS

                    matched_keywords = [term.upper() for term in keywords if term in line_lower]
                    cache.keyword_counter.update(matched_keywords)

                    if cache.total_matched < max_lines or is_firewall:
                        cache.findings.append(SambaFinding(
                            source=member,
                            line_number=i + 1,
                            finding=line.strip(),
                            severity=severity,
                            component=component
                        ))
                        cache.total_matched += 1

            except Exception as e:
                cache.findings.append(SambaFinding(
                    source=member,
                    error=str(e),
                    severity="error",
                    component="samba"
                ))

    return {
        "entries": cache.findings,
        "summary": dict(cache.keyword_counter)
    }

def correlate_firewall_failures(samba_findings: list) -> list:
    """Analyzes findings for firewall-related patterns."""
    firewall_entries = [f for f in samba_findings if f.component == "firewall"]
    
    summary = []
    if firewall_entries:
        summary.append(
            f"🔥 Critical: {len(firewall_entries)} firewall authentication failures detected"
        )
        summary.append("Recommended actions:")
        summary.append("1. Check firewall rules for SMB ports (445/tcp)")
        summary.append("2. Verify domain trust relationships")
        summary.append("3. Review authentication provider configurations")

    return summary

def run_tool(llm_output: str) -> str:
    if not os.path.exists(DEFAULT_SOS_PATH):
        return f"❌ No SOS report found at {DEFAULT_SOS_PATH}"

    result = inspect_samba_logs(DEFAULT_SOS_PATH)
    findings = result["entries"]
    summary = result["summary"]

    # Get firewall insights
    firewall_insights = correlate_firewall_failures(findings)

    # Build output
    output = []
    output.append(f"🔍 Found {len(findings)} samba-related issues:")
    
    for f in findings[:5]:
        output.append(f"- {f.finding} ({f.source}:{f.line_number})")
    
    if firewall_insights:
        output.append("\n🔥 Firewall Analysis:")
        output.extend(firewall_insights)
    
    if summary:
        output.append("\n📊 Keyword summary:")
        for k, v in summary.items():
            output.append(f"  {k}: {v}")

    return "\n".join(output)
