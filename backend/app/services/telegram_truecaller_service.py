"""
FK94 Security Platform - Truecaller via Telegram Bot
Free phone lookup using @Truecaller_bot on Telegram
"""
import asyncio
import re
from typing import Optional
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.sessions import StringSession
from app.core.config import settings


class TruecallerResult(BaseModel):
    found: bool = False
    name: Optional[str] = None
    carrier: Optional[str] = None
    phone_type: Optional[str] = None
    location: Optional[str] = None
    spam_score: int = 0
    spam_type: Optional[str] = None
    tags: list[str] = []
    email: Optional[str] = None
    error: Optional[str] = None


class TelegramTruecallerService:
    """
    Uses Telegram bot @Truecaller_bot to lookup phone numbers for free.

    Requires:
    - TELEGRAM_API_ID: From https://my.telegram.org
    - TELEGRAM_API_HASH: From https://my.telegram.org
    - TELEGRAM_SESSION: Session string (generated on first login)
    """

    BOT_USERNAME = "Truecaller_bot"

    def __init__(self):
        self.api_id = settings.TELEGRAM_API_ID
        self.api_hash = settings.TELEGRAM_API_HASH
        self.session = settings.TELEGRAM_SESSION
        self.is_configured = bool(self.api_id and self.api_hash)
        self._client: Optional[TelegramClient] = None

    async def _get_client(self) -> TelegramClient:
        """Get or create Telegram client"""
        if self._client is None or not self._client.is_connected():
            self._client = TelegramClient(
                StringSession(self.session),
                self.api_id,
                self.api_hash
            )
            await self._client.connect()

            if not await self._client.is_user_authorized():
                raise Exception("Telegram session not authorized. Run setup first.")

        return self._client

    async def lookup(self, phone: str, country_code: str = "AR") -> TruecallerResult:
        """
        Lookup phone number using Truecaller Telegram bot.

        Args:
            phone: Phone number
            country_code: ISO country code

        Returns:
            TruecallerResult with parsed data
        """
        if not self.is_configured:
            return TruecallerResult(
                found=False,
                error="Telegram API not configured. Add TELEGRAM_API_ID and TELEGRAM_API_HASH to .env"
            )

        # Clean and format phone number
        clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")

        if not clean_phone.startswith("+"):
            country_prefixes = {
                "AR": "54", "US": "1", "BR": "55", "MX": "52",
                "CO": "57", "CL": "56", "PE": "51", "UY": "598",
                "PY": "595", "EC": "593", "VE": "58", "ES": "34",
            }
            prefix = country_prefixes.get(country_code.upper(), "")
            if prefix:
                clean_phone = f"+{prefix}{clean_phone}"

        try:
            client = await self._get_client()

            # Send phone number to bot
            await client.send_message(self.BOT_USERNAME, clean_phone)

            # Wait for response (bot usually responds in 1-3 seconds)
            await asyncio.sleep(2)

            # Get last message from bot
            messages = await client.get_messages(self.BOT_USERNAME, limit=1)

            if not messages:
                return TruecallerResult(found=False, error="No response from bot")

            response_text = messages[0].text
            return self._parse_bot_response(response_text, clean_phone)

        except Exception as e:
            return TruecallerResult(found=False, error=str(e))

    def _parse_bot_response(self, text: str, phone: str) -> TruecallerResult:
        """Parse the Truecaller bot response"""

        if not text:
            return TruecallerResult(found=False)

        # Check if not found
        if "not found" in text.lower() or "no results" in text.lower():
            return TruecallerResult(found=False)

        result = TruecallerResult(found=True)

        # Parse name (usually first line or after "Name:")
        name_match = re.search(r"(?:Name|Nombre)[:\s]*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if name_match:
            result.name = name_match.group(1).strip()
        else:
            # Try first line if it looks like a name
            lines = text.strip().split("\n")
            if lines and not any(x in lines[0].lower() for x in ["spam", "carrier", "location", "phone"]):
                result.name = lines[0].strip()

        # Parse carrier
        carrier_match = re.search(r"(?:Carrier|Operador|Provider)[:\s]*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if carrier_match:
            result.carrier = carrier_match.group(1).strip()

        # Parse location
        location_match = re.search(r"(?:Location|Ubicación|Country|City)[:\s]*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if location_match:
            result.location = location_match.group(1).strip()

        # Parse spam info
        if "spam" in text.lower():
            result.tags.append("spam")
            spam_match = re.search(r"spam[:\s]*(\d+)", text, re.IGNORECASE)
            if spam_match:
                result.spam_score = int(spam_match.group(1))
            else:
                result.spam_score = 5  # Default if spam mentioned but no score

        if "scam" in text.lower():
            result.tags.append("scam")
            result.spam_score = max(result.spam_score, 8)

        if "telemarketer" in text.lower() or "marketing" in text.lower():
            result.tags.append("telemarketer")

        if "business" in text.lower() or "empresa" in text.lower():
            result.tags.append("business")

        return result

    async def close(self):
        """Close Telegram client"""
        if self._client and self._client.is_connected():
            await self._client.disconnect()


# Singleton
telegram_truecaller_service = TelegramTruecallerService()


async def generate_session_string(api_id: int, api_hash: str, phone: str) -> str:
    """
    Generate a session string for first-time setup.
    Run this once to get the session string, then save it in .env

    Usage:
        python -c "
        import asyncio
        from app.services.telegram_truecaller_service import generate_session_string
        session = asyncio.run(generate_session_string(API_ID, 'API_HASH', '+5491155551234'))
        print(f'TELEGRAM_SESSION={session}')
        "
    """
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        code = input("Ingresá el código que te llegó a Telegram: ")
        await client.sign_in(phone, code)

    session_string = client.session.save()
    await client.disconnect()

    return session_string
