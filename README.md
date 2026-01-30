# FK94 Security Platform

Plataforma de auditoría de seguridad personal con AI.

## Arquitectura

```
fk94_platform/
├── backend/           # FastAPI Python
│   ├── app/
│   │   ├── api/       # Endpoints
│   │   ├── core/      # Config
│   │   ├── models/    # Schemas
│   │   └── services/  # Business logic
│   └── .env           # API keys
│
└── frontend/          # Next.js + Tailwind
    └── src/
        ├── app/       # Pages
        ├── components/
        └── lib/       # API client
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar .env con las API keys
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## APIs Requeridas

| API | Uso | URL |
|-----|-----|-----|
| DeepSeek | AI Analysis | https://platform.deepseek.com |
| HIBP | Breach check | https://haveibeenpwned.com/API |
| Dehashed | Credentials | https://dehashed.com |
| Hunter.io | Email OSINT | https://hunter.io |

## Endpoints

- `POST /api/v1/check/email` - Quick breach check
- `POST /api/v1/audit/full` - Full security audit
- `POST /api/v1/score` - Get security score
- `POST /api/v1/ai/analyze` - AI analysis
- `POST /api/v1/report/pdf` - Generate PDF report
- `GET /api/v1/health` - Health check
- `GET /api/v1/status/apis` - Check API status

## Env Variables

### Backend (.env)
```
AI_API_KEY=sk-xxx
AI_BASE_URL=https://api.moonshot.ai
AI_MODEL=kimi-k2.5
DEEPSEEK_API_KEY=sk-xxx
HIBP_API_KEY=xxx
DEHASHED_API_KEY=xxx
DEHASHED_EMAIL=xxx
HUNTER_API_KEY=xxx
JOB_DB_PATH=jobs.sqlite3
JOB_WORKER_POLL_SECONDS=5
ENABLE_JOB_WORKER=true
```

## Automation (Async Jobs)

Endpoints:
- `POST /api/v1/automation/audit/full` - Enqueue full audit
- `POST /api/v1/automation/audit/multi` - Enqueue multi audit
- `GET /api/v1/automation/jobs/{job_id}` - Check job status/result

Example payload:
```json
{
  "email": "you@example.com",
  "check_breaches": true,
  "check_osint": true,
  "run_at": "2026-01-29T15:00:00Z"
}
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```
