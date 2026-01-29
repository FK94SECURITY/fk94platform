"""
FK94 Security Platform - DeepSeek AI Service
"""
import httpx
from typing import Optional
from app.core.config import settings


SYSTEM_PROMPT = """Eres el asistente de FK94 Security. Respondés de forma CORTA y DIRECTA.

REGLAS:
- Máximo 3-4 oraciones por sección
- Sin introducciones largas
- Solo lo esencial
- Usá bullets cortos
- Emojis: 🔴 Crítico 🟠 Alto 🟡 Medio 🟢 Bajo
- Respondé en español"""


class DeepSeekService:
    def __init__(self):
        # Use Moonshot/Kimi K2.5 if available, fallback to DeepSeek
        self.api_key = settings.AI_API_KEY or settings.DEEPSEEK_API_KEY
        self.base_url = settings.AI_BASE_URL if settings.AI_API_KEY else settings.DEEPSEEK_BASE_URL
        self.model = settings.AI_MODEL if settings.AI_API_KEY else settings.DEEPSEEK_MODEL

    async def analyze(self, prompt: str, context: Optional[dict] = None) -> str:
        """Send a prompt to DeepSeek and get analysis"""

        if not self.api_key:
            return "Error: DeepSeek API key not configured"

        # Build context message if audit data provided
        context_msg = ""
        if context:
            context_msg = self._build_context(context)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        if context_msg:
            messages.append({"role": "user", "content": f"Contexto de la auditoría:\n{context_msg}"})
            messages.append({"role": "assistant", "content": "Entendido. Tengo el contexto de la auditoría. ¿Qué necesitas que analice?"})

        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 600
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
                return f"Error conectando con DeepSeek: {str(e)}"
            except Exception as e:
                return f"Error inesperado: {str(e)}"

    async def analyze_audit(self, audit_result: dict) -> str:
        """Analyze full audit result and provide recommendations"""

        prompt = """Analizá esta auditoría. Formato EXACTO:

**Estado:** [🟢 Seguro / 🟡 Riesgo Medio / 🔴 Riesgo Alto] - 1 oración

**Problemas:** (si hay)
• Problema 1
• Problema 2

**Qué hacer:**
1. Acción más urgente
2. Segunda acción
3. Tercera acción

Máximo 150 palabras total."""

        return await self.analyze(prompt, context=audit_result)

    async def chat(self, message: str, history: list = None) -> str:
        """General security chat"""
        return await self.analyze(message)

    def _build_context(self, data: dict) -> str:
        """Build context string from audit data"""
        parts = []

        if "email" in data:
            parts.append(f"Email auditado: {data['email']}")

        if "security_score" in data:
            score = data["security_score"]
            parts.append(f"Security Score: {score.get('score', 'N/A')}/100 ({score.get('risk_level', 'N/A')})")

        if "breach_check" in data and data["breach_check"]:
            bc = data["breach_check"]
            parts.append(f"Breaches encontrados: {bc.get('breach_count', 0)}")
            if bc.get("breaches"):
                breach_names = [b.get("name", "Unknown") for b in bc["breaches"][:5]]
                parts.append(f"Servicios afectados: {', '.join(breach_names)}")

        if "password_exposure" in data and data["password_exposure"]:
            pe = data["password_exposure"]
            if pe.get("found"):
                parts.append(f"⚠️ Contraseñas filtradas encontradas: {pe.get('count', 'algunas')}")

        if "osint_result" in data and data["osint_result"]:
            osint = data["osint_result"]
            if osint.get("social_profiles"):
                parts.append(f"Perfiles sociales expuestos: {len(osint['social_profiles'])}")
            if osint.get("data_brokers"):
                parts.append(f"Data brokers con tus datos: {len(osint['data_brokers'])}")

        return "\n".join(parts)


# Singleton instance
deepseek_service = DeepSeekService()
