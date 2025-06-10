import tarfile
import json
from mcp_parser.output_models  import JobLifecycleEntry

def parse_job_lifecycle_logs(tar_path: str, max_lines: int = 10): 
    results = [] 
    try:
        with tarfile.open(tar_path, "r:*") as tar:
            members = [
                m for m in tar.getnames()
                if m.endswith("/var/log/tower/job_lifecycle.log")
            ]
            for member in members:
                try:
                    f = tar.extractfile(member)
                    if not f:
                        continue
                    lines = f.read().decode(errors="replace").splitlines()[:max_lines]
                    parsed_lines = []
                    for line in lines:
                        try:
                            parsed_line = json.loads(line)
                            job_lifecycle_entry = JobLifecycleEntry(**parsed_line)    
                            parsed_lines.append(job_lifecycle_entry)                   
                        except json.JSONDecodeError:
                            parsed_lines.append({"raw": line, "error": "invalid JSON"})
                    results.append({
                        "source": member,
                        "entries": parsed_lines
                    })
                except Exception as e:
                    results.append({
                        "source": member,
                        "error": str(e)
                    })
    except Exception as outer:
        results.append({
            "source": "parse_job_lifecycle_logs",
            "error": str(outer)
        })
    return results
