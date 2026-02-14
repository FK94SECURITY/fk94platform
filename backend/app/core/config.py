"""
FK94 Security Platform - Configuration
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FK94 Security Platform"
    DEBUG: bool = False

    # AI API (Moonshot Kimi K2.5)
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://api.moonshot.ai"
    AI_MODEL: str = "kimi-k2.5"

    # DeepSeek API (legacy fallback)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Supabase admin (backend side)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Email provider (optional, for lead notifications)
    RESEND_API_KEY: str = ""
    CONTACT_EMAIL_TO: str = "contact@fk94security.com"

    # OpenClaw (optional, required for managed orchestration)
    OPENCLAW_API_URL: str = ""
    OPENCLAW_API_KEY: str = ""
    OPENCLAW_PROJECT_ID: str = ""

    # OSINT APIs
    HIBP_API_KEY: str = ""  # Have I Been Pwned - set via HIBP_API_KEY env var
    DEHASHED_API_KEY: str = ""
    DEHASHED_EMAIL: str = ""
    HUNTER_API_KEY: str = ""
    WHOISXML_API_KEY: str = ""
    INTELLIGENCE_X_API_KEY: str = ""

    # Etherscan (optional, free tier: 5 req/s with key, 1 req/5s without)
    ETHERSCAN_API_KEY: str = ""

    # Truecaller (método directo - opcional)
    TRUECALLER_TOKEN: str = ""

    # Telegram (para Truecaller via bot - GRATIS)
    TELEGRAM_API_ID: Optional[int] = None
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_SESSION: str = ""  # Se genera una vez con el script de setup

    # Rate limiting
    FREE_CHECKS_PER_DAY: int = 50

    # Job worker / automation
    JOB_DB_PATH: str = "jobs.sqlite3"
    JOB_WORKER_POLL_SECONDS: int = 5
    ENABLE_JOB_WORKER: bool = True
    EVENT_DB_PATH: str = "events.sqlite3"

    # CORS
    CORS_ORIGINS: list = [
        "https://fk94platform.vercel.app",
        "https://fk94security.com",
        "https://www.fk94security.com",
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
