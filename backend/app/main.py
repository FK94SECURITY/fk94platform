"""
FK94 Security Platform - Main Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api.routes import router
from app.services import job_store
from app.services.job_worker import job_worker

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    job_store.init_db(settings.JOB_DB_PATH)
    if settings.ENABLE_JOB_WORKER:
        await job_worker.start()
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"🤖 AI API: {'✅ Configured' if settings.AI_API_KEY else ('📡 DeepSeek' if settings.DEEPSEEK_API_KEY else '❌ Not configured')}")
    print(f"🔍 HIBP API: {'✅ Configured' if settings.HIBP_API_KEY else '⚠️ Not configured'}")
    print(f"🔒 Rate Limiting: ✅ Enabled (60 req/min general, 10 req/min checks, 5 req/min audits)")
    yield
    # Shutdown
    if settings.ENABLE_JOB_WORKER:
        await job_worker.stop()
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
    FK94 Security Platform API

    Servicios de auditoría de seguridad personal:
    - Breach checking (Have I Been Pwned, Dehashed)
    - OSINT analysis
    - AI-powered security recommendations
    - Security scoring
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
cors_origins = ["*"] if settings.DEBUG else settings.CORS_ORIGINS
allow_credentials = False if "*" in cors_origins else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
