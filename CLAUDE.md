# FK94 Security Platform

## Architecture
- **Backend**: FastAPI 0.109 (Python 3.11) in `/backend/app/`
- **Frontend**: Next.js 16 + React 19 + Tailwind v4 in `/frontend/src/`
- **Auth**: Supabase
- **Payments**: Stripe (test mode)
- **AI**: DeepSeek/Kimi K2.5 via OpenAI-compatible API
- **Deploy**: Render (backend) + Vercel (frontend), auto-deploy on git push

## Backend Structure
```
backend/app/
├── main.py                    # FastAPI app, CORS, rate limiting
├── api/routes.py              # All API endpoints (/api/v1/...)
├── core/config.py             # Pydantic settings from .env
├── models/schemas.py          # Request/response models
└── services/
    ├── osint_service.py       # HIBP, Dehashed, Hunter.io
    ├── deepseek_service.py    # AI analysis (Kimi K2.5)
    ├── scoring_service.py     # Security score algorithm
    ├── pdf_service.py         # ReportLab PDF generation
    ├── stripe_service.py      # Stripe checkout + webhooks
    ├── job_worker.py          # Async job queue
    ├── job_store.py           # SQLite job persistence
    ├── audit_runner.py        # Full audit orchestration
    ├── truecaller_service.py  # Phone lookup
    ├── wallet_deep_scan.py    # Crypto wallet analysis
    └── multi_audit_service.py # Individual check functions
```

## Frontend Structure
```
frontend/src/
├── app/          # Next.js App Router (pages)
├── components/   # Reusable React components
├── lib/          # API client, Supabase client
├── contexts/     # React contexts
├── i18n/         # ES/EN translations
└── data/         # Static data (hardening scripts, checklist)
```

## Commands
```bash
# Backend
cd backend && source venv/bin/activate
pip install -r requirements.txt
python -c "import app.main"  # syntax check
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run build    # ALWAYS run after frontend changes
npm run lint

# Tests
cd backend && pytest tests/
cd frontend && npm run lint
```

## Rules
- NEVER commit .env files or secrets
- ALWAYS run `npm run build` after frontend changes
- Keep API backward compatible (don't change existing endpoint signatures)
- All text content in Spanish (ES) and English (EN) via i18n
- Conventional commits: feat:, fix:, security:, refactor:, test:, docs:
