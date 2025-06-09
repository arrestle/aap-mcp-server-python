import re
import tarfile
from output_models import DispatcherFinding  # Ensure this model includes `timestamp`, `level`, `message`, `component`

DISPATCHER_LOG_PATH = "var/log/tower/dispatcher.log"

# Match lines like:
# 2025-04-11 04:20:25,819 WARNING  [UUID] awx.main.dispatch.periodic PID:1198 Scheduler next run of send_subsystem_metrics is -0.05282139778137207 seconds in the past
LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+"
    r"(?P<level>\w+)\s+\[(?P<uuid>[a-f0-9]+)\]\s+"
    r"(?P<component>[\w\.]+)\s+PID:(?P<pid>\d+)\s+Scheduler next run of "
    r"(?P<task>[\w_]+) is (?P<drift>[-\d\.]+) seconds in the past"
)

def inspect_dispatcher_log(tar_path):
    findings = []

    with tarfile.open(tar_path, "r:*") as tar:
        try:
            member = next(m for m in tar.getnames() if m.endswith(DISPATCHER_LOG_PATH))
        except StopIteration:
            return findings  # Dispatcher log not found

        f = tar.extractfile(member)
        if not f:
            return findings

        for line in f:
            line = line.decode("utf-8", errors="replace").strip()
            match = LOG_PATTERN.match(line)
            if match:
                data = match.groupdict()
                # Compose a readable message field for model compatibility
                data["message"] = (
                    f'Scheduler task "{data["task"]}" ran {data["drift"]} seconds late.'
                )
                findings.append(DispatcherFinding(**data))

    return findings
