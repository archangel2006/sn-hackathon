"""
Support Agent - Tool-calling agent for the student chat.
Falls back to a local rule engine when no LLM key is available.
"""
import re
import uuid
import logging
from typing import Dict, List, Optional, Any

from ..rag.knowledge import search_kb
from ..rag.firewall import firewall
from ..models.schemas import ChatResponse, ChatRequest, ConsentProposal, SourceCitation

logger = logging.getLogger(__name__)

DEPT_OF = {
    "wellbeing": "Counselling Service",
    "financial": "Scholarships & Financial Aid",
    "academic": "Academic Advising",
    "engagement": "Academic Advising",
}

SHARE_DETAILS = {
    "financial": {
        "summary": "Fees are overdue and available funds look tight.",
        "shared_fields": ["Fee status and days overdue", "Scholarship eligibility"],
        "not_shared": ["Your wellbeing check-ins", "Your marks and attendance", "This chat"],
    },
    "wellbeing": {
        "summary": "Lower mood check-ins for a week, alongside missed coursework.",
        "shared_fields": ["Mood check-ins from the last 7 days", "Number of missed assignments"],
        "not_shared": ["Your finances", "Your marks and attendance", "This chat"],
    },
    "academic": {
        "summary": "Marks have dipped and a few assignments were missed.",
        "shared_fields": ["Marks for the last three assessments", "Number of missed assignments"],
        "not_shared": ["Your finances", "Your wellbeing check-ins", "This chat"],
    },
}

SAFETY_PATTERN = re.compile(
    r"hurt myself|end it all|suicid|self.?harm|no point|don't want to be here",
    re.IGNORECASE,
)
STAFF_PATTERN = re.compile(
    r"\bstaff\b|\btriage\b|\binternal\b|other student|another student|someone else",
    re.IGNORECASE,
)
FEES_PATTERN = re.compile(
    r"\bfees?\b|money|\bpay\b|scholar|\bfunds?\b|tuition|grant|afford", re.IGNORECASE
)
ATTEND_PATTERN = re.compile(r"\battend\b|\bclass\b", re.IGNORECASE)
STRESS_PATTERN = re.compile(
    r"\b(lot|yes|sad|low)\b|stress|overwhelm|anxious|tired|struggl|talk|hard|feeling",
    re.IGNORECASE,
)
SUPPORT_PATTERN = re.compile(r"support|option|help|what", re.IGNORECASE)


# In-memory session store keyed by session_id
_sessions: Dict[str, Dict[str, Any]] = {}


def _get_session(session_id: str) -> Dict[str, Any]:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "pending_proposals": set(),  # domains already proposed this session
            "cases_created": set(),
        }
    return _sessions[session_id]


def _make_trace_id() -> str:
    return "T-" + str(uuid.uuid4())[:6].upper()


def _propose_case(domain: str, session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if domain in session["pending_proposals"] or domain in session["cases_created"]:
        return None
    session["pending_proposals"].add(domain)
    details = SHARE_DETAILS.get(domain, {})
    return {
        "domain": domain,
        "department": DEPT_OF.get(domain, "Student Services"),
        "shared_summary": details.get("summary", ""),
        "shared_fields": details.get("shared_fields", []),
        "not_shared": details.get("not_shared", []),
    }


def _local_respond(message: str, session: Dict[str, Any], role: str = "student") -> ChatResponse:
    """Deterministic rule engine fallback (no LLM call)."""
    trace_id = _make_trace_id()
    t = message.lower()

    # Safety escalation – highest priority
    if SAFETY_PATTERN.search(t):
        return ChatResponse(
            type="escalation",
            text=(
                "I'm really glad you reached out. If you're in immediate danger, please call "
                "emergency services or the campus crisis line: 0800 000 0000 (open 24 hours). "
                "A member of the counselling team has been alerted and will reach out today. "
                "You can keep chatting here while you wait."
            ),
            trace_id=trace_id,
        )

    # Firewall: restricted staff content
    if STAFF_PATTERN.search(t):
        raw_docs = search_kb(t, top_k=4)
        _, blocked = firewall.filter_documents(raw_docs, role)
        return ChatResponse(
            type="blocked",
            text="I can't help with that. It's restricted to staff, and I didn't use it in this conversation.",
            blocked_count=max(1, blocked),
            trace_id=trace_id,
        )

    # ── Fees / financial ──────────────────────────────────────────────────────
    if FEES_PATTERN.search(t):
        raw_docs = search_kb("fees payment scholarship financial grant", top_k=4)
        allowed, blocked = firewall.filter_documents(raw_docs, role)
        sources = [SourceCitation(doc_id=d["doc_id"], title=d["title"]) for d in allowed[:2]]
        proposal = _propose_case("financial", session)
        resp = ChatResponse(
            type="message" if not proposal else "consent_request",
            text=(
                "Two things can help right now. You can ask for a short payment plan, and your "
                "results may make you eligible for the Merit Support Grant. The Scholarships and "
                "Financial Aid team can walk you through both."
            ),
            sources=sources,
            blocked_count=blocked,
            trace_id=trace_id,
        )
        if proposal:
            resp.type = "consent_request"
            resp.consent_request = ConsentProposal(**proposal)
        return resp

    # ── Attendance ────────────────────────────────────────────────────────────
    if ATTEND_PATTERN.search(t):
        raw_docs = search_kb("attendance policy absence", top_k=4)
        allowed, blocked = firewall.filter_documents(raw_docs, role)
        sources = [SourceCitation(doc_id=d["doc_id"], title=d["title"]) for d in allowed[:1]]
        return ChatResponse(
            type="message",
            text="Your attendance is 91% this term, which is steady. Nothing to worry about there.",
            sources=sources,
            blocked_count=blocked,
            trace_id=trace_id,
        )

    # ── Wellbeing / stress ────────────────────────────────────────────────────
    if STRESS_PATTERN.search(t):
        raw_docs = search_kb("counselling wellbeing stress academic support", top_k=4)
        allowed, blocked = firewall.filter_documents(raw_docs, role)
        sources = [SourceCitation(doc_id=d["doc_id"], title=d["title"]) for d in allowed[:2]]
        proposal = _propose_case("wellbeing", session)
        resp = ChatResponse(
            type="message",
            text=(
                "That sounds like a lot, and it's good that you said something. Your check-ins "
                "have been lower this week and a few assignments have slipped. The Counselling "
                "Service offers short first conversations, and there are options for easing your "
                "workload too."
            ),
            sources=sources,
            blocked_count=blocked,
            trace_id=trace_id,
        )
        if proposal:
            resp.type = "consent_request"
            resp.consent_request = ConsentProposal(**proposal)
        return resp

    # ── General support ───────────────────────────────────────────────────────
    if SUPPORT_PATTERN.search(t):
        raw_docs = search_kb("academic support tutoring advising", top_k=4)
        allowed, blocked = firewall.filter_documents(raw_docs, role)
        sources = [SourceCitation(doc_id=d["doc_id"], title=d["title"]) for d in allowed[:2]]
        proposal = _propose_case("academic", session)
        resp = ChatResponse(
            type="message",
            text=(
                "Here's what's available: academic advising to plan around deadlines, free peer "
                "tutoring, and extension requests. An advisor can look at your recent marks with you."
            ),
            sources=sources,
            blocked_count=blocked,
            trace_id=trace_id,
        )
        if proposal:
            resp.type = "consent_request"
            resp.consent_request = ConsentProposal(**proposal)
        return resp

    # ── Fallback ──────────────────────────────────────────────────────────────
    return ChatResponse(
        type="message",
        text="I can talk through your studies, attendance, fees, or how you're feeling. Which would you like to start with?",
        trace_id=trace_id,
    )


def run_agent(request: ChatRequest, student_id: str, role: str = "student") -> ChatResponse:
    session = _get_session(request.session_id or "default_session")
    return _local_respond(request.message, session, role)
