"""
Admin / demo routes: POST /admin/risk-scan/{student_id}, GET /audit/{trace_id}
"""
from fastapi import APIRouter, HTTPException, Path
from ..university_api.mock_pipeline import get_student, get_all_students
from ..risk.judge import risk_engine
from ..services.audit_service import audit_service

router = APIRouter(tags=["admin", "audit"])


@router.post("/admin/risk-scan/{student_id}")
async def trigger_risk_scan(
    student_id: str = Path(..., description="Student ID e.g. S001"),
):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    result = risk_engine.judge_student(student)
    return {
        "student_id": student_id,
        "overall": result["overall"],
        "domains": {k: v.model_dump() for k, v in result["domains"].items()},
        "alerts": [a.model_dump() for a in result["alerts"]],
        "evaluated_at": result["evaluated_at"],
    }


@router.post("/admin/risk-scan-all")
async def trigger_risk_scan_all():
    results = {}
    for student in get_all_students():
        sid = student["student_id"]
        r = risk_engine.judge_student(student)
        results[sid] = {
            "overall": r["overall"],
            "alerts_count": len(r["alerts"]),
        }
    return results


@router.get("/audit/{trace_id}")
async def get_audit_trace(trace_id: str = Path(...)):
    trace = audit_service.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    return trace.model_dump()
