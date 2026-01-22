"""
FK94 Security Platform - Truecaller Service
Phone number lookup using Truecaller API
"""
import httpx
from typing import Optional
from pydantic import BaseModel
from app.core.config import settings


class TruecallerResult(BaseModel):
    found: bool = False
    name: Optional[str] = None
    carrier: Optional[str] = None
    phone_type: Optional[str] = None  # mobile, landline
    location: Optional[str] = None
    spam_score: int = 0
    spam_type: Optional[str] = None  # spam, scam, telemarketer, etc
    tags: list[str] = []
    image_url: Optional[str] = None
    email: Optional[str] = None
    error: Optional[str] = None


class TruecallerService:
    """
    Truecaller API integration for phone lookup.

    To get your installation_id:
    1. Install Truecaller app on your phone
    2. Login with your phone number
    3. Use a packet sniffer or extract from app data
    4. The installation_id looks like: a]xxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

    Alternative: Use truecallerjs (Node.js) to login and get the token
    """

    BASE_URL = "https://search5-noneu.truecaller.com/v2/search"

    def __init__(self):
        self.token = settings.TRUECALLER_TOKEN
        self.is_configured = bool(self.token)

    async def lookup(self, phone: str, country_code: str = "AR") -> TruecallerResult:
        """
        Lookup phone number in Truecaller database.

        Args:
            phone: Phone number (can include country code or not)
            country_code: ISO country code (AR, US, BR, etc)

        Returns:
            TruecallerResult with name, carrier, spam info, etc
        """
        if not self.is_configured:
            return TruecallerResult(
                found=False,
                error="Truecaller not configured. Add TRUECALLER_TOKEN to .env"
            )

        # Clean phone number
        clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")

        # Add country code if not present
        if not clean_phone.startswith("+"):
            country_prefixes = {
                "AR": "54",
                "US": "1",
                "BR": "55",
                "MX": "52",
                "CO": "57",
                "CL": "56",
                "PE": "51",
                "UY": "598",
                "PY": "595",
                "EC": "593",
                "VE": "58",
                "ES": "34",
            }
            prefix = country_prefixes.get(country_code.upper(), "")
            if prefix:
                clean_phone = f"+{prefix}{clean_phone}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Truecaller/13.0.0 (Android;14)",
        }

        params = {
            "q": clean_phone,
            "countryCode": country_code.upper(),
            "type": "4",  # Phone search
            "locAddr": "",
            "encoding": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.BASE_URL,
                    headers=headers,
                    params=params
                )

                if response.status_code == 401:
                    return TruecallerResult(
                        found=False,
                        error="Truecaller token expired or invalid"
                    )

                if response.status_code != 200:
                    return TruecallerResult(
                        found=False,
                        error=f"Truecaller API error: {response.status_code}"
                    )

                data = response.json()
                return self._parse_response(data, clean_phone)

        except httpx.TimeoutException:
            return TruecallerResult(found=False, error="Truecaller timeout")
        except Exception as e:
            return TruecallerResult(found=False, error=str(e))

    def _parse_response(self, data: dict, phone: str) -> TruecallerResult:
        """Parse Truecaller API response"""

        # Check if we got results
        if not data.get("data"):
            return TruecallerResult(found=False)

        results = data["data"]
        if not results:
            return TruecallerResult(found=False)

        # Get first result (best match)
        result = results[0]

        # Extract name
        name = None
        if result.get("name"):
            name = result["name"]
        elif result.get("altName"):
            name = result["altName"]

        # Extract carrier/provider
        carrier = None
        phones = result.get("phones", [])
        if phones:
            phone_info = phones[0]
            carrier = phone_info.get("carrier")
            phone_type = phone_info.get("type", "").lower()
        else:
            phone_type = None

        # Extract location
        location = None
        addresses = result.get("addresses", [])
        if addresses:
            addr = addresses[0]
            parts = []
            if addr.get("city"):
                parts.append(addr["city"])
            if addr.get("state"):
                parts.append(addr["state"])
            if addr.get("countryCode"):
                parts.append(addr["countryCode"])
            location = ", ".join(parts) if parts else None

        # Extract spam info
        spam_score = 0
        spam_type = None
        tags = []

        spam_info = result.get("spamInfo", {})
        if spam_info:
            spam_score = spam_info.get("spamScore", 0)
            spam_type = spam_info.get("spamType")

        # Check badges/tags
        badges = result.get("badges", [])
        for badge in badges:
            tags.append(badge)

        if result.get("isSpam"):
            tags.append("spam")
        if result.get("isBusiness"):
            tags.append("business")

        # Image
        image_url = result.get("image")

        # Email (sometimes available)
        email = None
        internet_addresses = result.get("internetAddresses", [])
        for ia in internet_addresses:
            if ia.get("type") == "email":
                email = ia.get("id")
                break

        return TruecallerResult(
            found=True,
            name=name,
            carrier=carrier,
            phone_type=phone_type,
            location=location,
            spam_score=spam_score,
            spam_type=spam_type,
            tags=tags,
            image_url=image_url,
            email=email
        )


# Singleton instance
truecaller_service = TruecallerService()
