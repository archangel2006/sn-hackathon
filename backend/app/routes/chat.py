"""
Chat endpoint: POST /chat  – calls the support agent
Cases endpoint: POST /cases – consent-gated ServiceNow case creation
"""
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from ..agent.support_agent import run_agent
from ..services.servicenow import servicenow_client
from ..services.audit_service import audit_service
from ..models.schemas import ChatRequest, ChatResponse, CaseCreateRequest

router = APIRouter(tags=["chat", "cases"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    x_user_id: Optional[str] = Header("S001", alias="X-User-Id"),
    x_role: Optional[str] = Header("student", alias="X-Role"),
):
    student_id = x_user_id or "S001"
    role = x_role or "student"
    response = run_agent(body, student_id, role)

    # Log the interaction
    audit_service.log_interaction(
        trace_id=response.trace_id,
        actor=student_id,
        role=role,
        query=body.message,
        tools_called=["search_support_kb"],
        retrieved_count=len(response.sources) + response.blocked_count,
        authorized_count=len(response.sources),
        blocked_count=response.blocked_count,
        sent_to_llm_count=len(response.sources),
    )
    return response


@router.post("/cases")
async def create_case(
    body: CaseCreateRequest,
    x_user_id: Optional[str] = Header("S001", alias="X-User-Id"),
    x_role: Optional[str] = Header("student", alias="X-Role"),
):
    if not body.consent or not body.consent.given:
        raise HTTPException(
            status_code=403,
            detail="Consent Gate: Cannot create a case without explicit student consent.",
        )
    try:
        new_case = servicenow_client.create_case(body)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    audit_service.log_interaction(
        trace_id=body.trace_id or "T-CASE",
        actor=x_user_id or "S001",
        role=x_role or "student",
        tools_called=["create_case"],
        consent_verified=True,
        case_created=new_case.no,
    )
    return new_case.model_dump()
