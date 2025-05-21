from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DispatcherFinding(BaseModel):
    timestamp: str
    level: str
    message: str
    component: Optional[str] = "dispatcher"

class SambaFinding(BaseModel):
    source: str
    line_number: Optional[int] = None
    finding: Optional[str] = None
    error: Optional[str] = None
    severity: str
    component: Optional[str] = "samba"

class JobLifecycleEntry(BaseModel):
    type: str
    task_id: int
    state: str
    task_name: str
    time: str
    blocked_by: Optional[str] = None
    guid: Optional[str] = None
    work_unit_id: Optional[str] = None

class JobLifecycleLog(BaseModel):
    source: str
    entries: List[JobLifecycleEntry]

class MCPReport(BaseModel):
    source: str
    timestamp: str
    payload: Dict[str, Any]

    dispatcher: Optional[List[DispatcherFinding]] = None
    samba_findings: Optional[List[SambaFinding]] = None
    samba_summary: Optional[Dict[str, int]] = None
    job_lifecycle_logs: Optional[List[JobLifecycleLog]] = None
    job_lifecycle_summary: Optional[Dict[str, int]] = None
