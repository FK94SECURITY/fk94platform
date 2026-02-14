"""
FK94 Security Platform - Supabase Admin Service
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseAdminService:
    def __init__(self) -> None:
        self.base_url = settings.SUPABASE_URL.rstrip("/")
        self.service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        self.is_configured = bool(self.base_url and self.service_key)

    def _headers(self) -> dict:
        return {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def update_profile_plan(
        self,
        *,
        user_id: str,
        plan: str,
        audits_remaining: Optional[int] = None,
    ) -> bool:
        if not self.is_configured:
            logger.warning("Supabase admin service not configured; skipping profile update")
            return False

        payload: dict = {"plan": plan}
        if audits_remaining is not None:
            payload["audits_remaining"] = audits_remaining

        url = f"{self.base_url}/rest/v1/profiles?id=eq.{user_id}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.patch(url, headers=self._headers(), json=payload)
                if res.status_code >= 300:
                    logger.error(f"Supabase profile update failed [{res.status_code}]: {res.text[:200]}")
                    return False
            return True
        except Exception as exc:
            logger.error(f"Supabase profile update error: {exc}")
            return False


supabase_admin_service = SupabaseAdminService()
