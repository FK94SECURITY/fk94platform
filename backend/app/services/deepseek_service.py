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
        # Build ordered list of AI providers for fallback
        self.providers = []
        if settings.AI_API_KEY:
            self.providers.append({
                "name": "Moonshot",
                "api_key": settings.AI_API_KEY,
                "base_url": settings.AI_BASE_URL,
                "model": settings.AI_MODEL,
            })
        if settings.DEEPSEEK_API_KEY:
            self.providers.append({
                "name": "DeepSeek",
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": settings.DEEPSEEK_BASE_URL,
                "model": settings.DEEPSEEK_MODEL,
            })

    async def _call_provider(self, provider: dict, messages: list) -> str:
        """Call a single AI provider and return the response text."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{provider['base_url']}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": provider["model"],
                    "messages": messages,
                    "temperature": 1,
                    "max_tokens": 600
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def analyze(self, prompt: str, context: Optional[dict] = None) -> str:
        """Send a prompt to AI and get analysis, with automatic provider fallback."""
        import logging
        logger = logging.getLogger(__name__)

        if not self.providers:
            return "Error: AI API key not configured (AI_API_KEY o DEEPSEEK_API_KEY)"

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

        last_error = None
        for provider in self.providers:
            try:
                result = await self._call_provider(provider, messages)
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"AI provider {provider['name']} failed: {e}, trying next...")

        logger.error(f"All AI providers failed. Last error: {last_error}")
        return self._static_fallback(context)

    def _static_fallback(self, context: Optional[dict] = None) -> str:
        """Generate a static fallback response when all AI providers are unavailable."""
        if not context:
            return (
                "⚠️ El análisis AI no está disponible temporalmente.\n\n"
                "Tus resultados de auditoría siguen siendo válidos. "
                "Revisá las recomendaciones y el puntaje de seguridad para entender tu nivel de riesgo."
            )

        parts = ["⚠️ El análisis AI no está disponible temporalmente.\n"]

        score = context.get("security_score", {})
        score_val = score.get("score", 0)
        risk = score.get("risk_level", "unknown")

        if score_val >= 80:
            parts.append("🟢 **Estado:** Tu puntaje de seguridad es bueno.")
        elif score_val >= 50:
            parts.append("🟡 **Estado:** Tu puntaje indica riesgo medio. Revisá las recomendaciones.")
        else:
            parts.append("🔴 **Estado:** Tu puntaje indica riesgo alto. Tomá acción inmediata.")

        breach = context.get("breach_check")
        if breach and breach.get("breached"):
            count = breach.get("breach_count", 0)
            parts.append(f"\n⚠️ Se encontraron {count} filtraciones. Cambiá tus contraseñas afectadas.")

        parts.append(
            "\n**Qué hacer:**\n"
            "1. Revisá las recomendaciones detalladas arriba\n"
            "2. Cambiá contraseñas comprometidas\n"
            "3. Activá 2FA en todas tus cuentas"
        )

        return "\n".join(parts)

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

        if "wallet_result" in data and data["wallet_result"]:
            wr = data["wallet_result"]
            parts.append(f"Tipo de auditoría: WALLET (crypto)")
            parts.append(f"Wallet: {wr.get('address', 'N/A')}")
            parts.append(f"Chain: {wr.get('chain', 'N/A')}")
            parts.append(f"Balance: {wr.get('balance', 'N/A')}")
            parts.append(f"Transacciones: {wr.get('transaction_count', 0)}")
            parts.append(f"Traceability Score: {wr.get('traceability_score', 0)}/100")
            parts.append(f"Es rastreable: {'SÍ' if wr.get('is_traceable') else 'NO'}")
            exchanges = wr.get('exchanges_detected', [])
            if exchanges:
                parts.append(f"Exchanges detectados (KYC): {', '.join(exchanges)}")
                parts.append(f"Interacciones con exchanges: {len(wr.get('exchange_interactions', []))}")
            if wr.get('used_mixer'):
                parts.append("⚠️ Usó mixer (Tornado Cash)")
            if wr.get('ofac_sanctioned'):
                parts.append("🚨 DIRECCIÓN SANCIONADA POR OFAC")
            if wr.get('first_tx_date'):
                parts.append(f"Primera TX: {wr['first_tx_date']}")
            if wr.get('last_tx_date'):
                parts.append(f"Última TX: {wr['last_tx_date']}")
            parts.append(f"Contrapartes únicas: {wr.get('unique_counterparties', 0)}")
            details = wr.get('traceability_details', [])
            if details:
                parts.append(f"Detalles: {'; '.join(details)}")

        if "audit_type" in data:
            parts.insert(0, f"Tipo de auditoría: {data['audit_type']}")

        return "\n".join(parts)


# Singleton instance
deepseek_service = DeepSeekService()
