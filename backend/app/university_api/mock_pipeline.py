from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Mock University Data Store
STUDENTS_DB: Dict[str, Dict[str, Any]] = {
    "S001": {
        "student_id": "S001",
        "name": "Student 001",
        "course": "Computer Science, year 2",
        "academic": {
            "recent_marks": [68, 61, 54],
            "missed_assignments": 3,
            "upcoming_deadlines": ["Algorithms Assignment 2 in 3 days", "Database Project in 10 days"],
            "notes": "Marks have dipped over the last three assessments."
        },
        "engagement": {
            "attendance_pct": 91,
            "lms_logins_per_week": 3,
            "trend": "steady",
            "notes": "Steady at 91% this term."
        },
        "financial": {
            "fees_due": 2400,
            "days_overdue": 18,
            "funds_status": "tight",
            "eligible_for_grant": True,
            "notes": "Tuition fees are 18 days overdue."
        },
        "wellbeing": {
            "avg_mood_7d": 2.1,
            "high_stress_days_7d": 5,
            "self_reported_concern": "Feeling overwhelmed with deadlines and financial obligations",
            "notes": "Your check-ins have been lower this week."
        }
    },
    "S009": {
        "student_id": "S009",
        "name": "Student 009",
        "course": "Mechanical Engineering, year 3",
        "academic": {
            "recent_marks": [52, 49, 45],
            "missed_assignments": 2,
            "upcoming_deadlines": ["Thermodynamics Lab in 2 days"],
            "notes": "Struggling with advanced core modules."
        },
        "engagement": { "attendance_pct": 82, "lms_logins_per_week": 4, "notes": "Slight attendance drop." },
        "financial": { "fees_due": 0, "days_overdue": 0, "funds_status": "adequate", "eligible_for_grant": False, "notes": "Fees paid." },
        "wellbeing": { "avg_mood_7d": 3.4, "high_stress_days_7d": 2, "notes": "Mild stress before exams." }
    },
    "S014": {
        "student_id": "S014",
        "name": "Student 014",
        "course": "Biomedical Sciences, year 1",
        "academic": { "recent_marks": [72, 70, 68], "missed_assignments": 0, "notes": "Good academic pacing." },
        "engagement": { "attendance_pct": 88, "lms_logins_per_week": 6, "notes": "Active LMS logins." },
        "financial": { "fees_due": 0, "days_overdue": 0, "funds_status": "adequate", "eligible_for_grant": False, "notes": "Up to date." },
        "wellbeing": {
            "avg_mood_7d": 1.9,
            "high_stress_days_7d": 6,
            "self_reported_concern": "Severe homesickness and anxiety",
            "notes": "Continuous low mood logged."
        }
    },
    "S022": {
        "student_id": "S022",
        "name": "Student 022",
        "course": "Law, year 2",
        "academic": { "recent_marks": [64, 60, 58], "missed_assignments": 1, "notes": "Average performance." },
        "engagement": { "attendance_pct": 89, "lms_logins_per_week": 5, "notes": "Normal attendance." },
        "financial": {
            "fees_due": 1800,
            "days_overdue": 12,
            "funds_status": "at_risk",
            "eligible_for_grant": True,
            "notes": "Overdue invoice reminder sent."
        },
        "wellbeing": { "avg_mood_7d": 3.2, "high_stress_days_7d": 3, "notes": "Stable mood." }
    },
    "S031": {
        "student_id": "S031",
        "name": "Student 031",
        "course": "Business Administration, year 2",
        "academic": { "recent_marks": [60, 65, 62], "missed_assignments": 1, "notes": "Consistent marks." },
        "engagement": { "attendance_pct": 92, "lms_logins_per_week": 7, "notes": "Strong attendance." },
        "financial": {
            "fees_due": 3100,
            "days_overdue": 24,
            "funds_status": "critical",
            "eligible_for_grant": True,
            "notes": "Significant fee arrears."
        },
        "wellbeing": { "avg_mood_7d": 3.0, "high_stress_days_7d": 3, "notes": "Manageable stress." }
    },
    "S045": {
        "student_id": "S045",
        "name": "Student 045",
        "course": "Data Science, year 1",
        "academic": { "recent_marks": [85, 88, 91], "missed_assignments": 0, "notes": "High academic honors." },
        "engagement": { "attendance_pct": 97, "lms_logins_per_week": 9, "notes": "Excellent attendance." },
        "financial": { "fees_due": 0, "days_overdue": 0, "funds_status": "adequate", "eligible_for_grant": False, "notes": "No fees due." },
        "wellbeing": { "avg_mood_7d": 4.5, "high_stress_days_7d": 0, "notes": "High self-reported wellbeing." }
    }
}

def get_student(student_id: str) -> Optional[Dict[str, Any]]:
    return STUDENTS_DB.get(student_id)

def get_all_students() -> List[Dict[str, Any]]:
    return list(STUDENTS_DB.values())

def get_student_snapshots(student_id: str, count: int = 14) -> List[Dict[str, Any]]:
    """Generates synthetic snapshot trends over the past 14 days."""
    student = get_student(student_id)
    if not student:
        return []

    snapshots = []
    base_date = datetime.now()
    for i in range(count, 0, -1):
        day_date = (base_date - timedelta(days=i)).strftime("%Y-%m-%d")
        if student_id == "S001":
            # Trending downward over the 14 days
            factor = (count - i) / count
            mood = round(max(1.8, 3.8 - (factor * 1.7)), 1)
            overdue = min(18, max(0, 18 - i))
            snapshots.append({
                "date": day_date,
                "mood": mood,
                "attendance": 91,
                "days_overdue": overdue,
                "missed_tasks": 1 if i > 7 else 3
            })
        else:
            snapshots.append({
                "date": day_date,
                "mood": student.get("wellbeing", {}).get("avg_mood_7d", 3.0),
                "attendance": student.get("engagement", {}).get("attendance_pct", 90),
                "days_overdue": student.get("financial", {}).get("days_overdue", 0),
                "missed_tasks": student.get("academic", {}).get("missed_assignments", 0)
            })
    return snapshots
