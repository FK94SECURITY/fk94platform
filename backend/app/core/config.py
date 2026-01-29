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

    # OSINT APIs
    HIBP_API_KEY: str = ""  # Have I Been Pwned
    DEHASHED_API_KEY: str = ""
    DEHASHED_EMAIL: str = ""
    HUNTER_API_KEY: str = ""
    WHOISXML_API_KEY: str = ""
    INTELLIGENCE_X_API_KEY: str = ""

    # Truecaller (método directo - opcional)
    TRUECALLER_TOKEN: str = ""

    # Telegram (para Truecaller via bot - GRATIS)
    TELEGRAM_API_ID: Optional[int] = None
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_SESSION: str = ""  # Se genera una vez con el script de setup

    # Rate limiting
    FREE_CHECKS_PER_DAY: int = 50

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "https://fk94security.com"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
