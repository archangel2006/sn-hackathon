"""
Staff-facing routes: GET/PATCH /staff/cases
"""
from fastapi import APIRouter, Header, HTTPException, Path
from typing import Optional
from ..services.servicenow import servicenow_client, ROLE_DOMAIN_ACCESS
from ..services.audit_service import audit_service
from ..models.schemas import CaseStateUpdate

router = APIRouter(prefix="/staff", tags=["staff"])

VALID_STAFF_ROLES = {"counsellor", "finaid", "advisor", "admin"}


def _get_staff_role(x_role: Optional[str]) -> str:
    role = (x_role or "counsellor").lower()
    if role not in VALID_STAFF_ROLES:
        raise HTTPException(status_code=403, detail=f"Unknown staff role: {role}")
    return role


@router.get("/cases")
async def list_cases(
    x_user_id: Optional[str] = Header("staff_user", alias="X-User-Id"),
    x_role: Optional[str] = Header("counsellor", alias="X-Role"),
):
    role = _get_staff_role(x_role)
    cases = servicenow_client.get_cases_for_staff(role)
    return [c.model_dump() for c in cases]


@router.get("/cases/{case_id}")
async def get_case_detail(
    case_id: str = Path(..., description="Case number e.g. WEL0000124"),
    x_user_id: Optional[str] = Header("staff_user", alias="X-User-Id"),
    x_role: Optional[str] = Header("counsellor", alias="X-Role"),
):
    role = _get_staff_role(x_role)
    case = servicenow_client.get_case_by_no(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # Enforce data minimisation – staff see only their domain's data
    allowed_domains = ROLE_DOMAIN_ACCESS.get(role, [])
    if case.domain not in allowed_domains:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: {role} cannot view {case.domain} cases.",
        )
    return case.model_dump()


@router.patch("/cases/{case_id}")
async def update_case_state(
    body: CaseStateUpdate,
    case_id: str = Path(..., description="Case number"),
    x_user_id: Optional[str] = Header("staff_user", alias="X-User-Id"),
    x_role: Optional[str] = Header("counsellor", alias="X-Role"),
):
    role = _get_staff_role(x_role)
    case = servicenow_client.get_case_by_no(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    allowed_domains = ROLE_DOMAIN_ACCESS.get(role, [])
    if case.domain not in allowed_domains:
        raise HTTPException(status_code=403, detail="Access denied: role domain mismatch")

    valid_states = {"New", "In Progress", "Waiting for Student", "Resolved"}
    if body.state not in valid_states:
        raise HTTPException(
            status_code=400, detail=f"Invalid state. Use one of: {valid_states}"
        )

    updated = servicenow_client.update_case_state(case_id, body.state)
    audit_service.log_interaction(
        trace_id=f"T-PATCH-{case_id}",
        actor=x_user_id or "staff",
        role=role,
        tools_called=["update_case_state"],
    )
    return updated.model_dump()
