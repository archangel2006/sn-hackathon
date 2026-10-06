from typing import List, Dict, Any

KNOWLEDGE_DOCS: List[Dict[str, Any]] = [
    {
        "doc_id": "KB001",
        "title": "Academic Support Guide",
        "audience": "student",
        "category": "academic",
        "content": "Students experiencing academic difficulties can request deadline extensions of up to 7 days for eligible coursework, book 1-on-1 advisor consultations, or access study skills workshops.",
        "keywords": ["academic", "study", "studies", "extension", "deadline", "coursework", "marks", "grade"]
    },
    {
        "doc_id": "KB002",
        "title": "Tutoring FAQ",
        "audience": "student",
        "category": "academic",
        "content": "Free peer tutoring is available weekly in math, programming, writing, and sciences. Drop-in sessions operate Monday through Thursday in the Library Learning Commons.",
        "keywords": ["tutor", "tutoring", "peer", "library", "help", "support", "study"]
    },
    {
        "doc_id": "KB003",
        "title": "Counselling Service intro",
        "audience": "student",
        "category": "wellbeing",
        "content": "The University Counselling Service provides confidential, short-term support and initial check-in consultations. Students can self-refer or be connected through university support agents with explicit consent.",
        "keywords": ["counselling", "counsellor", "wellbeing", "stress", "mental", "anxious", "talk", "feeling", "overwhelmed"]
    },
    {
        "doc_id": "KB004",
        "title": "Scholarships overview",
        "audience": "student",
        "category": "financial",
        "content": "The Scholarships & Financial Aid Office administers emergency hardship grants, tuition relief options, and the Merit Support Grant for second-year students maintaining passing standards.",
        "keywords": ["scholarship", "financial", "grant", "aid", "funds", "money", "afford", "hardship"]
    },
    {
        "doc_id": "KB005",
        "title": "Fee payment support",
        "audience": "student",
        "category": "financial",
        "content": "Tuition fees can be divided into flexible monthly installment plans without penalty interest if arranged prior to formal administrative lockouts. Contact financial services to initiate an agreement.",
        "keywords": ["fee", "fees", "payment", "tuition", "overdue", "installment", "pay", "money"]
    },
    {
        "doc_id": "KB006",
        "title": "Attendance Policy and Support",
        "audience": "student",
        "category": "engagement",
        "content": "Minimum suggested attendance is 80%. When medical or personal hardships arise, submit an extenuating circumstances notification to protect academic standing.",
        "keywords": ["attendance", "class", "absence", "missed", "sick", "hours"]
    },
    {
        "doc_id": "KB007",
        "title": "Internal Staff Triage Guidelines",
        "audience": "staff",
        "category": "internal",
        "content": "RESTRICTED: Internal staff criteria for assigning Case Priority 1 vs 2, caseload distribution rules among senior clinical psychologists, and inter-departmental escalation protocols.",
        "keywords": ["staff", "triage", "internal", "priority", "clinical", "caseload"]
    },
    {
        "doc_id": "KB008",
        "title": "Tier 3 Mental Health Escalation Matrix",
        "audience": "staff",
        "category": "internal",
        "content": "RESTRICTED: Emergency medical intervention criteria, campus security coordination procedures, and involuntary leave protocol guidelines for clinical leads.",
        "keywords": ["escalation", "security", "involuntary", "tier", "clinical lead", "restricted"]
    }
]

def search_kb(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    q_words = set(query.lower().split())
    scored = []
    
    for doc in KNOWLEDGE_DOCS:
        score = 0
        doc_text = (doc["title"] + " " + doc["content"] + " " + " ".join(doc["keywords"])).lower()
        for w in q_words:
            if len(w) > 2 and w in doc_text:
                score += 1
        scored.append((score, doc))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored[:top_k]]
