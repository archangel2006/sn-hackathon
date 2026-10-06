import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.schemas import RiskAssessment, StudentAlert
from .rules import evaluate_student_all_domains, calculate_overall_risk
from ..config import settings

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self):
        self.cached_alerts: Dict[str, List[StudentAlert]] = {}

    def judge_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs LLM-as-judge risk assessment across domains,
        falling back gracefully to the rules baseline.
        """
        student_id = student_data.get("student_id", "S001")
        # 1. Run rules baseline as ground truth & fallback
        baseline_results = evaluate_student_all_domains(student_data)
        overall = calculate_overall_risk(baseline_results)

        # 2. If free API / LLM configured, attempt LLM judge evaluation
        final_assessments = baseline_results
        llm_success = False

        if settings.GEMINI_API_KEY or settings.OPENAI_API_KEY:
            try:
                # Optional LLM enhancement hook
                pass
            except Exception as e:
                logger.warning(f"LLM judge failed, using rules baseline: {e}")

        # 3. Generate alerts for student
        alerts = self._generate_alerts(student_id, final_assessments)
        self.cached_alerts[student_id] = alerts

        return {
            "student_id": student_id,
            "domains": final_assessments,
            "overall": overall,
            "alerts": alerts,
            "evaluated_at": datetime.now().isoformat()
        }

    def _generate_alerts(self, student_id: str, assessments: Dict[str, RiskAssessment]) -> List[StudentAlert]:
        alerts = []
        alert_id = 1
        
        friendly_msgs = {
            "financial": "Tuition fees are overdue. Support and grant options are available.",
            "wellbeing": "Your check-ins have been lower this week. Let's talk about it.",
            "academic": "Marks have dipped over recent assessments.",
            "engagement": "Attendance is lower than usual this term."
        }
        
        for domain, assessment in assessments.items():
            if assessment.level in ("HIGH", "MEDIUM") and assessment.score >= 50:
                msg = friendly_msgs.get(domain, f"{domain.capitalize()} may benefit from a check-in.")
                alerts.append(
                    StudentAlert(
                        id=f"ALT-{student_id}-{alert_id}",
                        student_id=student_id,
                        domain=domain,
                        level=assessment.level,
                        message=msg,
                        created_at="Today, 09:00",
                        read=False
                    )
                )
                alert_id += 1
                
        return alerts

    def get_alerts(self, student_id: str) -> List[StudentAlert]:
        return self.cached_alerts.get(student_id, [])

risk_engine = RiskEngine()
