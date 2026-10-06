"""
Student-facing routes: /me/overview, /chat, /cases, /me/cases
"""
from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Optional
from ..university_api.mock_pipeline import get_student
from ..risk.judge import risk_engine
from ..agent.support_agent import run_agent
from ..services.servicenow import servicenow_client
from ..services.audit_service import audit_service
from ..models.schemas import (
    StudentOverview,
    DomainStatus,
    ChatRequest,
    ChatResponse,
    CaseCreateRequest,
    CaseRecord,
)

router = APIRouter(prefix="/me", tags=["student"])

AREA_LABEL = {
    "academic": "Studies",
    "engagement": "Attendance",
    "financial": "Money",
    "wellbeing": "Wellbeing",
}
AREA_NOTE = {
    "academic": "Marks have dipped over the last three assessments.",
    "engagement": "Steady at 91% this term.",
    "financial": "Tuition fees are 18 days overdue.",
    "wellbeing": "Your check-ins have been lower this week.",
}
AREA_ASK = {
    "academic": "Can I get help with my studies? What support exists?",
    "engagement": "Check my attendance",
    "financial": "Help with fees",
    "wellbeing": "I've been feeling stressed lately",
}
STUDENT_LEVEL = {
    "HIGH": "Could use support",
    "MEDIUM": "Worth watching",
    "LOW": "Doing well",
}
ICON = {"HIGH": "heart", "MEDIUM": "eye", "LOW": "check"}


def _require_student(x_role: Optional[str] = Header(None, alias="X-Role")) -> str:
    if x_role and x_role not in ("student", None):
        raise HTTPException(status_code=403, detail="Forbidden: student role required")
    return x_role or "student"


@router.get("/overview", response_model=StudentOverview)
async def get_overview(
    x_user_id: Optional[str] = Header("S001", alias="X-User-Id"),
    _role: str = Depends(_require_student),
):
    student_id = x_user_id or "S001"
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    # Run risk assessment
    result = risk_engine.judge_student(student)
    domains = result["domains"]
    alerts = result["alerts"]
    overall = result["overall"]

    areas = []
    for key in ["academic", "engagement", "financial", "wellbeing"]:
        a = domains.get(key)
        if a:
            areas.append(
                DomainStatus(
                    key=key,
                    title=AREA_LABEL[key],
                    score=a.score,
                    level=a.level,
                    student_level=STUDENT_LEVEL.get(a.level, "Doing well"),
                    icon=ICON.get(a.level, "check"),
                    note=AREA_NOTE.get(key, ""),
                    ask=AREA_ASK.get(key, ""),
                )
            )

    return StudentOverview(
        student_id=student_id,
        name=student["name"],
        course=student["course"],
        areas=areas,
        alerts=alerts,
        active_cases_count=len(servicenow_client.get_cases_for_student(student_id)),
    )


@router.get("/cases")
async def get_my_cases(
    x_user_id: Optional[str] = Header("S001", alias="X-User-Id"),
    _role: str = Depends(_require_student),
):
    student_id = x_user_id or "S001"
    cases = servicenow_client.get_cases_for_student(student_id)
    return [c.model_dump() for c in cases]
