"""
FK94 Security Platform - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📡 DeepSeek API: {'✅ Configured' if settings.DEEPSEEK_API_KEY else '❌ Not configured'}")
    print(f"🔍 HIBP API: {'✅ Configured' if settings.HIBP_API_KEY else '⚠️ Using free tier'}")
    yield
    # Shutdown
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],  # Allow all for dev
    allow_credentials=True,
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
