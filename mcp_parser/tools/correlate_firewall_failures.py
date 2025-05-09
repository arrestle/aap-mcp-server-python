def correlate_firewall_failures(payload: dict) -> list:
    """Analyzes samba_findings for FIREWALL_FAILED patterns and adds correlation insights."""
    summary = []

    samba_findings = payload.get("samba_findings", [])
    if not samba_findings:
        return summary

    firewall_failed = [
        f for f in samba_findings
        if "NT_STATUS_AUTHENTICATION_FIREWALL_FAILED" in f.get("finding", "")
    ]
    connection_reset = [
        f for f in samba_findings
        if "NT_STATUS_CONNECTION_RESET" in f.get("finding", "")
    ]

    if firewall_failed:
        summary.append(
            f"{len(firewall_failed)} Samba log entries reported 'NT_STATUS_AUTHENTICATION_FIREWALL_FAILED' — likely caused by firewall policy issues or authentication trust misconfigurations."
        )

    if connection_reset:
        summary.append(
            f"{len(connection_reset)} connection resets (NT_STATUS_CONNECTION_RESET) found — these often follow failed authentication due to network or trust boundary issues."
        )

    if firewall_failed and connection_reset:
        summary.append(
            "Correlation detected: 'FIREWALL_FAILED' errors are followed by 'CONNECTION_RESET' failures — likely indicating downstream trust or firewall handling problems."
        )

    return summary
