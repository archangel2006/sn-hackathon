from typing import Dict, Any, List
from ..models.schemas import RiskAssessment, StudentAlert
from datetime import datetime

DEPT_ROUTING = {
    "academic": "Academic Advising",
    "engagement": "Academic Advising",
    "financial": "Scholarships & Financial Aid",
    "wellbeing": "Counselling Service"
}

def evaluate_academic(data: Dict[str, Any], student_id: str) -> RiskAssessment:
    marks = data.get("recent_marks", [70, 70, 70])
    missed = data.get("missed_assignments", 0)
    
    # Calculate score
    score = 25
    evidence = []
    
    if len(marks) >= 2 and (marks[0] - marks[-1]) >= 10:
        score += 20
        evidence.append(f"Marks: {', '.join(map(str, marks))} across recent assessments showing downward trend")
    
    if missed > 0:
        score += missed * 12
        evidence.append(f"{missed} assignments missed this month")
        
    score = min(100, max(0, score))
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    
    rationale = "Declining marks and missed coursework suggest difficulty keeping pace." if score >= 40 else "Academic progress is stable."
    action = "Offer an academic advising session to review workload and deadlines" if score >= 40 else "Continue routine study schedule"
    
    return RiskAssessment(
        student_id=student_id,
        domain="academic",
        score=score,
        level=level,
        confidence=0.88,
        evidence=evidence or ["Marks are consistent with coursework expectations"],
        rationale=rationale,
        suggested_action=action,
        suggested_department=DEPT_ROUTING["academic"],
        source="rules_baseline"
    )

def evaluate_engagement(data: Dict[str, Any], student_id: str) -> RiskAssessment:
    att = data.get("attendance_pct", 90)
    logins = data.get("lms_logins_per_week", 5)
    
    score = 20
    evidence = []
    
    if att < 75:
        score = 80
        evidence.append(f"Attendance has fallen to {att}%")
    elif att < 85:
        score = 55
        evidence.append(f"Attendance is {att}% (below 85% guideline)")
    else:
        evidence.append(f"Attendance is steady at {att}% this term")
        
    if logins < 2:
        score += 20
        evidence.append(f"LMS logins below normal ({logins}/week)")
        
    score = min(100, max(0, score))
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    
    return RiskAssessment(
        student_id=student_id,
        domain="engagement",
        score=score,
        level=level,
        confidence=0.92,
        evidence=evidence,
        rationale="Attendance and platform activity remain consistent." if score < 40 else "Lower engagement observed.",
        suggested_action="Routine check-in" if score < 40 else "Schedule attendance check-in",
        suggested_department=DEPT_ROUTING["engagement"],
        source="rules_baseline"
    )

def evaluate_financial(data: Dict[str, Any], student_id: str) -> RiskAssessment:
    days = data.get("days_overdue", 0)
    due = data.get("fees_due", 0)
    grant_eligible = data.get("eligible_for_grant", False)
    
    score = 15
    evidence = []
    
    if days > 14:
        score = 74
        evidence.append(f"Tuition fees are {days} days overdue")
        evidence.append("Available funds are below monthly need")
    elif days > 0:
        score = 45
        evidence.append(f"Tuition fees are {days} days overdue")
    else:
        evidence.append("Tuition account is up to date")
        
    if grant_eligible:
        evidence.append("May qualify for the Merit Support Grant")
        
    score = min(100, max(0, score))
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    
    rationale = "Overdue fees and tight funds; eligible for hardship grant." if score >= 70 else "Finances in good standing."
    action = "Connect with Scholarships and Financial Aid for payment options and grant review" if score >= 40 else "No action required"
    
    return RiskAssessment(
        student_id=student_id,
        domain="financial",
        score=score,
        level=level,
        confidence=0.95,
        evidence=evidence,
        rationale=rationale,
        suggested_action=action,
        suggested_department=DEPT_ROUTING["financial"],
        source="rules_baseline"
    )

def evaluate_wellbeing(data: Dict[str, Any], student_id: str) -> RiskAssessment:
    mood = data.get("avg_mood_7d", 3.5)
    stress_days = data.get("high_stress_days_7d", 1)
    
    score = 20
    evidence = []
    
    if mood <= 2.2:
        score = 63
        evidence.append(f"Mood check-ins averaged {mood} out of 5 over 7 days")
    elif mood <= 3.0:
        score = 45
        evidence.append(f"Mood check-ins averaged {mood}/5")
    else:
        evidence.append(f"Mood check-ins stable (avg {mood}/5)")
        
    if stress_days >= 4:
        score = max(score, 63)
        evidence.append(f"Stress rated 4 or 5 on {stress_days} of the last 7 days")
        
    # Check if student is slipping in coursework alongside mood
    score = min(100, max(0, score))
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    
    rationale = "Sustained low mood alongside stress signals; may benefit from supportive check-in." if score >= 40 else "Wellbeing signals are within healthy baseline."
    action = "Offer an introductory conversation with the Counselling Service" if score >= 40 else "General wellbeing check-in"
    
    return RiskAssessment(
        student_id=student_id,
        domain="wellbeing",
        score=score,
        level=level,
        confidence=0.85,
        evidence=evidence,
        rationale=rationale,
        suggested_action=action,
        suggested_department=DEPT_ROUTING["wellbeing"],
        source="rules_baseline"
    )

def evaluate_student_all_domains(student: Dict[str, Any]) -> Dict[str, RiskAssessment]:
    s_id = student.get("student_id", "S001")
    return {
        "academic": evaluate_academic(student.get("academic", {}), s_id),
        "engagement": evaluate_engagement(student.get("engagement", {}), s_id),
        "financial": evaluate_financial(student.get("financial", {}), s_id),
        "wellbeing": evaluate_wellbeing(student.get("wellbeing", {}), s_id)
    }

def calculate_overall_risk(assessments: Dict[str, RiskAssessment]) -> Dict[str, Any]:
    scores = [a.score for a in assessments.values()]
    highest = max(scores) if scores else 0
    med_or_high_count = sum(1 for a in assessments.values() if a.level in ("MEDIUM", "HIGH"))
    
    compound_addition = 10 if med_or_high_count >= 2 else 0
    overall = min(100, highest + compound_addition)
    
    level = "HIGH" if overall >= 70 else "MEDIUM" if overall >= 40 else "LOW"
    return {
        "overall_score": overall,
        "overall_level": level,
        "compound_risk": compound_addition > 0
    }
