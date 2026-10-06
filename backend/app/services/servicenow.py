import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.schemas import CaseRecord, CaseCreateRequest
from ..config import settings

logger = logging.getLogger(__name__)

DEPT_ROUTING = {
    "wellbeing": "Counselling Service",
    "financial": "Scholarships & Financial Aid",
    "academic": "Academic Advising",
    "engagement": "Academic Advising"
}

STATE_MAPPING = {
    "New": "Received",
    "In Progress": "In progress",
    "Waiting for Student": "Action needed from you",
    "Resolved": "Resolved"
}

ROLE_DOMAIN_ACCESS = {
    "counsellor": ["wellbeing"],
    "finaid": ["financial"],
    "advisor": ["academic", "engagement"],
    "admin": ["wellbeing", "financial", "academic", "engagement"]
}

class ServiceNowClient:
    def __init__(self):
        self._next_id = 124
        self.cases: Dict[str, CaseRecord] = {}
        self._seed_cases()

    def _seed_cases(self):
        seeds = [
            {
                "no": "WEL0000122",
                "student_id": "S031",
                "student_name": "Student 031",
                "domain": "financial",
                "score": 66,
                "state": "In Progress",
                "opened": "Yesterday, 16:20",
                "evidence": ["Tuition fees 24 days overdue", "Critical available funds status"],
                "summary": "Overdue fees and limited funds, with likely eligibility for hardship support."
            },
            {
                "no": "WEL0000121",
                "student_id": "S014",
                "student_name": "Student 014",
                "domain": "wellbeing",
                "score": 71,
                "state": "New",
                "opened": "Today, 08:40",
                "evidence": ["Mood check-ins averaged 1.9/5", "6 of 7 days logged high stress"],
                "summary": "Sustained low mood alongside severe homesickness; requested supportive consultation."
            },
            {
                "no": "WEL0000119",
                "student_id": "S009",
                "student_name": "Student 009",
                "domain": "academic",
                "score": 47,
                "state": "In Progress",
                "opened": "Yesterday, 11:05",
                "evidence": ["Marks declining: 52, 49, 45", "2 missed core lab tasks"],
                "summary": "Declining marks and missed work over the past month."
            },
            {
                "no": "WEL0000118",
                "student_id": "S022",
                "student_name": "Student 022",
                "domain": "financial",
                "score": 58,
                "state": "New",
                "opened": "Yesterday, 09:32",
                "evidence": ["Fees 12 days overdue", "At risk funds category"],
                "summary": "Overdue fees; eligible for grant assessment."
            }
        ]

        for s in seeds:
            dept = DEPT_ROUTING.get(s["domain"], "Student Services")
            self.cases[s["no"]] = CaseRecord(
                no=s["no"],
                student_id=s["student_id"],
                student_name=s["student_name"],
                domain=s["domain"],
                dept=dept,
                priority="High" if s["score"] >= 70 else "Medium",
                state=s["state"],
                student_status=STATE_MAPPING.get(s["state"], "In progress"),
                risk_score=s["score"],
                risk_level="HIGH" if s["score"] >= 70 else "MEDIUM",
                evidence=s["evidence"],
                ai_summary=s["summary"],
                consent_given=True,
                consent_time=s["opened"],
                trace_id="T-SEED",
                opened=s["opened"],
                trace={
                    "tools": ["get_risk_profile", "search_support_kb", "suggest_case", "create_case"],
                    "retrieved": 4,
                    "authorized": 3,
                    "blocked": 1,
                    "sent": 3
                }
            )

    def create_case(self, req: CaseCreateRequest) -> CaseRecord:
        # Strict Consent Gate check
        if not req.consent or not req.consent.given:
            raise ValueError("Consent Gate Error: Cannot create ServiceNow case without explicit student consent.")

        case_no = f"WEL{str(self._next_id).zfill(7)}"
        self._next_id += 1
        
        dept = DEPT_ROUTING.get(req.domain.lower(), "Student Support")
        opened_str = datetime.now().strftime("Today, %H:%M")
        
        # If ServiceNow PDI credentials are provided, we could post to ServiceNow Table API
        if settings.SERVICENOW_INSTANCE and settings.SERVICENOW_USER:
            try:
                # Optional live Table API call
                pass
            except Exception as e:
                logger.error(f"Live ServiceNow PDI sync error: {e}")

        new_case = CaseRecord(
            no=case_no,
            student_id=req.student_id,
            student_name="Student 001" if req.student_id == "S001" else f"Student {req.student_id.replace('S','')}",
            domain=req.domain.lower(),
            dept=dept,
            priority=req.priority or ("High" if req.risk_score >= 70 else "Medium"),
            state="New",
            student_status=STATE_MAPPING["New"],
            risk_score=req.risk_score,
            risk_level=req.risk_level,
            evidence=req.evidence,
            ai_summary=req.ai_summary,
            consent_given=True,
            consent_time=req.consent.timestamp,
            trace_id=req.trace_id,
            opened=opened_str,
            trace={
                "tools": ["get_risk_profile", "search_support_kb", "suggest_case", "create_case"],
                "retrieved": 4,
                "authorized": 3,
                "blocked": 1,
                "sent": 3
            }
        )

        self.cases[case_no] = new_case
        return new_case

    def get_cases_for_student(self, student_id: str) -> List[CaseRecord]:
        return [c for c in self.cases.values() if c.student_id == student_id]

    def get_cases_for_staff(self, role: str) -> List[CaseRecord]:
        allowed_domains = ROLE_DOMAIN_ACCESS.get(role.lower(), ["wellbeing"])
        return [c for c in self.cases.values() if c.domain in allowed_domains]

    def get_case_by_no(self, case_no: str) -> Optional[CaseRecord]:
        return self.cases.get(case_no)

    def update_case_state(self, case_no: str, new_state: str) -> Optional[CaseRecord]:
        case = self.cases.get(case_no)
        if not case:
            return None

        case.state = new_state
        case.student_status = STATE_MAPPING.get(new_state, "In progress")
        self.cases[case_no] = case
        return case

servicenow_client = ServiceNowClient()
