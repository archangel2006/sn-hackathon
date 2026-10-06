# Student Early-Warning & Support Agent — sn-hackathon

> AI agent that watches student signals, warns early, and creates consent-gated ServiceNow cases.

## Quick start

### 1 — Backend (FastAPI)

```bash
cd sn-hackathon/backend

# Install deps (already installed globally on this machine)
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --port 8000
```

Open **http://127.0.0.1:8000/docs** to explore and test all endpoints.

### 2 — Frontend (Next.js)

```bash
cd sn-hackathon/frontend

npm install   # first time only
npm run dev
```

Open **http://localhost:3000**

---

## What's built

### Frontend (`frontend/`)
| File | Purpose |
|---|---|
| `src/app/page.js` | Root orchestrator — state, API calls, fallback engine |
| `src/app/globals.css` | Full design system (CSS variables, components, responsive) |
| `src/app/layout.js` | Next.js root layout with Plus Jakarta Sans |
| `src/components/TopBar.jsx` | Header with portal switcher and API status badge |
| `src/components/StudentPortal.jsx` | Student Home, Chat, Support Status, rail |
| `src/components/StaffPortal.jsx` | Staff queue, case detail, trace drawer |
| `src/components/Icons.jsx` | SVG icon system |
| `src/lib/data.js` | Mock data seed, domain mappings, local respond engine |
| `src/lib/api.js` | FastAPI client with 4s timeout and fallback |
| `.env.local` | `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` |

**Works offline** — the local respond engine activates automatically when the backend is unreachable.  
**Goes live** — the top-bar badge switches to "FastAPI Live" when the backend is detected.

### Backend (`backend/`)

```
backend/
└── app/
    ├── main.py              # FastAPI app, CORS, startup seeding
    ├── config.py            # Settings, env vars
    ├── models/schemas.py    # Pydantic models
    ├── university_api/      # Mock student data pipeline
    ├── risk/
    │   ├── rules.py         # Deterministic domain risk scorer
    │   └── judge.py         # RiskEngine (LLM + rules fallback)
    ├── rag/
    │   ├── knowledge.py     # 8-doc knowledge base (student + staff-only)
    │   └── firewall.py      # Role-based pre-LLM document filter
    ├── agent/
    │   └── support_agent.py # Rule-based agent with safety escalation
    ├── services/
    │   ├── servicenow.py    # In-memory case store + live PDI hook
    │   └── audit_service.py # Full interaction trace log
    └── routes/
        ├── student.py       # GET /me/overview, GET /me/cases
        ├── chat.py          # POST /chat, POST /cases
        ├── staff.py         # GET/PATCH /staff/cases
        └── admin.py         # POST /admin/risk-scan, GET /audit
```

## API Endpoints

| Method | Path | Who |
|---|---|---|
| `GET` | `/health` | All |
| `GET` | `/me/overview` | Student |
| `GET` | `/me/cases` | Student |
| `POST` | `/chat` | Student |
| `POST` | `/cases` | Student (requires consent) |
| `GET` | `/staff/cases` | Staff |
| `GET` | `/staff/cases/{id}` | Staff |
| `PATCH` | `/staff/cases/{id}` | Staff |
| `POST` | `/admin/risk-scan/{student_id}` | Demo |
| `GET` | `/audit/{trace_id}` | Both |

Auth: `X-User-Id` and `X-Role` headers (`student`, `counsellor`, `finaid`, `advisor`).

## Environment variables

Copy `.env.example` → `.env`:

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Free key from aistudio.google.com (optional — enables richer responses) |
| `OPENAI_API_KEY` | Alternative LLM (optional) |
| `SERVICENOW_INSTANCE` | PDI URL e.g. `https://dev12345.service-now.com` (optional) |
| `SERVICENOW_USER` | PDI service account |
| `SERVICENOW_PASSWORD` | PDI service account password |

All are optional — everything works with mock data and the rule engine by default.

## Key design decisions

- **No real data** — all student data is synthetic and non-clinical  
- **Consent gate is enforced** — `POST /cases` throws 403 without `consent.given = true`  
- **Firewall is module-level** — staff-only docs are dropped before any LLM call  
- **Data minimisation** — each staff role only sees cases in their domain  
- **Safety escalation** — any message matching crisis patterns returns `type: escalation` immediately  

## Demo logins

| Who | Header values |
|---|---|
| Student | `X-User-Id: S001`, `X-Role: student` |
| Counsellor | `X-User-Id: counsellor_01`, `X-Role: counsellor` |
| Financial Aid | `X-User-Id: finaid_01`, `X-Role: finaid` |
| Academic Advisor | `X-User-Id: advisor_01`, `X-Role: advisor` |
