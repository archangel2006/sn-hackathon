from typing import Dict, Optional, List
from ..models.schemas import AuditTrace
from datetime import datetime

class AuditService:
    def __init__(self):
        self.traces: Dict[str, AuditTrace] = {}

    def log_interaction(
        self,
        trace_id: str,
        actor: str,
        role: str,
        query: Optional[str] = None,
        tools_called: Optional[List[str]] = None,
        retrieved_count: int = 0,
        authorized_count: int = 0,
        blocked_count: int = 0,
        sent_to_llm_count: int = 0,
        consent_verified: bool = False,
        case_created: Optional[str] = None
    ) -> AuditTrace:
        trace = AuditTrace(
            trace_id=trace_id,
            actor=actor,
            role=role,
            timestamp=datetime.now().isoformat(),
            query=query,
            tools_called=tools_called or [],
            retrieved_count=retrieved_count,
            authorized_count=authorized_count,
            blocked_count=blocked_count,
            sent_to_llm_count=sent_to_llm_count,
            consent_verified=consent_verified,
            case_created=case_created
        )
        self.traces[trace_id] = trace
        return trace

    def get_trace(self, trace_id: str) -> Optional[AuditTrace]:
        return self.traces.get(trace_id)

audit_service = AuditService()
