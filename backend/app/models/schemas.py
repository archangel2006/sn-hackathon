from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class DomainStatus(BaseModel):
    key: str
    title: str
    score: int
    level: str  # LOW, MEDIUM, HIGH
    student_level: str  # "Doing well", "Worth watching", "Could use support"
    icon: str
    note: str
    ask: str

class StudentAlert(BaseModel):
    id: str
    student_id: str
    domain: str
    level: str
    message: str
    created_at: str
    read: bool = False

class StudentOverview(BaseModel):
    student_id: str
    name: str
    course: str
    areas: List[DomainStatus]
    alerts: List[StudentAlert]
    active_cases_count: int

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"

class SourceCitation(BaseModel):
    doc_id: str
    title: str

class ConsentProposal(BaseModel):
    domain: str
    department: str
    shared_summary: str
    shared_fields: List[str]
    not_shared: List[str]

class ChatResponse(BaseModel):
    type: str = Field(..., description="message | consent_request | blocked | escalation | fallback")
    text: str
    sources: List[SourceCitation] = []
    blocked_count: int = 0
    consent_request: Optional[ConsentProposal] = None
    trace_id: str

class ConsentPayload(BaseModel):
    given: bool
    timestamp: str
    scope: str

class CaseCreateRequest(BaseModel):
    student_id: str
    domain: str
    category: Optional[str] = "General"
    priority: Optional[str] = "Medium"
    risk_score: int
    risk_level: str
    evidence: List[str]
    ai_summary: str
    consent: ConsentPayload
    trace_id: Optional[str] = None

class CaseRecord(BaseModel):
    no: str
    student_id: str
    student_name: str
    domain: str
    dept: str
    priority: str = "Medium"
    state: str = "New"
    student_status: str = "Received"
    risk_score: int
    risk_level: str
    evidence: List[str]
    ai_summary: str
    consent_given: bool = True
    consent_time: str
    trace_id: Optional[str] = None
    opened: str
    trace: Optional[Dict[str, Any]] = None

class CaseStateUpdate(BaseModel):
    state: str

class RiskAssessment(BaseModel):
    student_id: str
    domain: str
    score: int
    level: str
    confidence: float
    evidence: List[str]
    rationale: str
    suggested_action: str
    suggested_department: str
    source: str = "rules_baseline"

class AuditTrace(BaseModel):
    trace_id: str
    actor: str
    role: str
    timestamp: str
    query: Optional[str] = None
    tools_called: List[str] = []
    retrieved_count: int = 0
    authorized_count: int = 0
    blocked_count: int = 0
    sent_to_llm_count: int = 0
    consent_verified: bool = False
    case_created: Optional[str] = None
