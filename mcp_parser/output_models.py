
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SambaFinding(BaseModel):
    source: str
    line_number: Optional[int] = None
    finding: Optional[str] = None
    error: Optional[str] = None
    severity: str
    component: str

class MCPReport(BaseModel):
    source: str
    timestamp: str
    payload: Dict[str, Any]
    samba_findings: List[SambaFinding]
