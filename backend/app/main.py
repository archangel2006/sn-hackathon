"""
FastAPI application entry point.
Run with: uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import student_router, chat_router, staff_router, admin_router
from .university_api.mock_pipeline import get_all_students
from .risk.judge import risk_engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Student Early-Warning & Support Agent – AI risk engine, "
        "consent-gated chat, RAG + firewall, ServiceNow case routing."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(student_router)
app.include_router(chat_router)
app.include_router(staff_router)
app.include_router(admin_router)


@app.get("/health", tags=["meta"])
async def health_check():
    return {"status": "ok", "version": settings.VERSION, "app": settings.PROJECT_NAME}


@app.on_event("startup")
async def startup_event():
    """Seed risk assessments for all mock students at startup."""
    print("[startup] Seeding risk assessments for mock students...")
    for student in get_all_students():
        try:
            risk_engine.judge_student(student)
            print(f"  [ok] Risk scan: {student['student_id']} ({student['name']})")
        except Exception as e:
            print(f"  [err] Failed for {student['student_id']}: {e}")
    print("[ready] Backend ready. Open http://127.0.0.1:8000/docs to explore the API.")
