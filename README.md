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
DEEPSEEK_API_KEY=sk-xxx
HIBP_API_KEY=xxx
DEHASHED_API_KEY=xxx
DEHASHED_EMAIL=xxx
HUNTER_API_KEY=xxx
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```
