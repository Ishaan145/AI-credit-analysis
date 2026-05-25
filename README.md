# Credit AI Backend
AI-powered Credit Improvement & Financial Readiness App. This application helps users to Upload credit reports; Analyze financial health using AI; Track credit improvement goals; Receive AI-powered recommendations; Monitor reminders and score insights.

AI-powered credit improvement & financial readiness backend
Phase 1 MVP — FastAPI + PostgreSQL(Neondb) + OpenAI/Gemini/Groq

| **Ishaan** | AI Coach | `reco_engine`, `chat_service`, `prompts`, `chat.py`, `recommendations.py` |
| Shared | Auth, DB, schemas, deploy | `core/*`, `models/*`, `schemas/*`, `main.py` |

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env       # fill OPENAI_API_KEY, DATABASE_URL, JWT_SECRET
# JWT
python -c "import secrets; print(secrets.token_urlsafe(48))"
# Verify DB before running alembic
python -c "from app.core.config import settings; print(settings.database_url[:50], '...')"
# DB (local docker)
docker run -d --name creditai-pg -e POSTGRES_USER=creditai \
  -e POSTGRES_PASSWORD=creditai -e POSTGRES_DB=creditai -p 5432:5432 postgres:16
# run
uvicorn app.main:app --reload
# open http://localhost:8000/docs

```

## Quick test

```bash
curl http://localhost:8000/health

# 1. signup
curl.exe -X POST http://localhost:8000/auth/signup `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@test.com\",\"password\":\"pass1234\",\"name\":\"Ishaan\"}'
# → {"access_token":"eyJ..."}

# 2. create chat session
TOKEN="eyJ..."
curl -X POST localhost:8000/chat/sessions
  -H "Authorization: Bearer $TOKEN"
  -H 'Content-Type: application/json'
  -d '{"title":"first chat"}'

# 3. send message
curl -X POST localhost:8000/chat/sessions/1/message
  -H "Authorization: Bearer $TOKEN"
  -H 'Content-Type: application/json'
  -d '{"content":"How can I improve my score?"}'
```
OR

```bash
# 1. Login → fresh token
$token = (Invoke-RestMethod -Uri http://localhost:8000/auth/login `
  -Method Post -ContentType "application/json" `
  -Body (@{email="test@test.com"; password="pass1234"} | ConvertTo-Json)).access_token

$headers = @{ Authorization = "Bearer $token" }

# 2. Check token populated
Write-Host "Token starts with: $($token.Substring(0,20))..."

# 3. List existing sessions (already created earlier as id=1)
$sessions = Invoke-RestMethod -Uri http://localhost:8000/chat/sessions -Headers $headers
$sessions

# 4. Use first session id
$sid = $sessions[0].id
Write-Host "Using session: $sid"

# 5. Send msg, save full response
$reply = Invoke-RestMethod -Uri "http://localhost:8000/chat/sessions/$sid/message" `
  -Method Post -Headers $headers -ContentType "application/json" `
  -Body (@{content="How can I improve my credit score?"} | ConvertTo-Json)

# 6. Show readable output
Write-Host "`n=== ASSISTANT REPLY ===" -ForegroundColor Cyan
$reply.assistant_message.content
Write-Host "`n=== QUICK ACTIONS ===" -ForegroundColor Cyan
$reply.suggested_actions
```

## Folder layout
```bash
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── reports.py        # A
│   │   │   ├── ocr.py            # A
│   │   │   ├── analysis.py       # A
│   │   │   ├── chat.py           # I
│   │   │   └── recommendations.py # I
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── db.py
│   ├── models/                   # SQLAlchemy
│   ├── schemas/                  # Pydantic
│   ├── services/
│   │   ├── ocr_parser.py         # A
│   │   ├── risk_engine.py        # A
│   │   ├── score_predictor.py    # A
│   │   ├── chat_service.py       # I
│   │   └── reco_engine.py        # I
│   └── main.py
├── tests/
│   ├── __init__
│   └── test_chat_and_recos
├── alembic/
│   ├── env.py 
│   ├── script.py.mako
│   └── versions/.gitkeep
├── alembic.ini 
├── requirements.txt
├── .env.example
└── README.md
```

## FICO weights (memorize)

| Factor | Weight |
|---|---|
| Payment History | 35% |
| Credit Utilization | 30% |
| Credit Age | 15% |
| Credit Mix | 10% |
| New Credit / Inquiries | 10% |


## Testing

```bash
pytest -v
```

## API Contract (locked)

| Method | Path | Owner |
|---|---|---|
| POST | `/auth/signup` | Shared |
| POST | `/auth/login` | Shared |
| GET | `/users/me` | Shared |
| POST | `/reports/upload` | Anshul |
| GET | `/reports/{id}` | Anshul |
| GET | `/reports/{id}/factors` | Anshul |
| GET | `/reports/{id}/risk` | Anshul |
| POST | `/chat/sessions` | Ishaan |
| GET | `/chat/sessions` | Ishaan |
| GET | `/chat/sessions/{id}` | Ishaan |
| POST | `/chat/sessions/{id}/message` | Ishaan |
| GET | `/recommendations/{report_id}` | Ishaan |
| POST | `/plan/generate` | Ishaan |
| POST | `/predict` | Anshul + Ishaan |
