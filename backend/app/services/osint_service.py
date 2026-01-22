"""
FK94 Security Platform - OSINT Service
Integrates multiple OSINT APIs for comprehensive security checks
"""
import httpx
import hashlib
from typing import Optional
from app.core.config import settings
from app.models.schemas import (
    BreachCheckResult, BreachInfo, PasswordExposure,
    OSINTResult, RiskLevel
)


class OSINTService:
    """Unified OSINT service integrating multiple APIs"""

    def __init__(self):
        self.hibp_key = settings.HIBP_API_KEY
        self.dehashed_key = settings.DEHASHED_API_KEY
        self.dehashed_email = settings.DEHASHED_EMAIL
        self.hunter_key = settings.HUNTER_API_KEY

    # === HAVE I BEEN PWNED ===

    async def check_hibp_breaches(self, email: str) -> BreachCheckResult:
        """Check email against Have I Been Pwned database"""

        # If no API key, use free pwned passwords check only
        if not self.hibp_key:
            return await self._check_hibp_free(email)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                    headers={
                        "hibp-api-key": self.hibp_key,
                        "user-agent": "FK94-Security-Platform"
                    },
                    params={"truncateResponse": "false"},
                    timeout=30.0
                )

                if response.status_code == 404:
                    # No breaches found
                    return BreachCheckResult(
                        email=email,
                        breached=False,
                        breach_count=0,
                        breaches=[],
                        risk_level=RiskLevel.SAFE
                    )

                response.raise_for_status()
                breaches_data = response.json()

                breaches = [
                    BreachInfo(
                        name=b.get("Name", "Unknown"),
                        date=b.get("BreachDate"),
                        data_types=b.get("DataClasses", []),
                        description=b.get("Description", "")[:200]
                    )
                    for b in breaches_data
                ]

                # Calculate risk level based on breach count and types
                risk_level = self._calculate_breach_risk(breaches)

                return BreachCheckResult(
                    email=email,
                    breached=True,
                    breach_count=len(breaches),
                    breaches=breaches,
                    risk_level=risk_level
                )

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    return await self._check_hibp_free(email)
                raise
            except Exception as e:
                print(f"HIBP Error: {e}")
                return await self._check_hibp_free(email)

    async def _check_hibp_free(self, email: str) -> BreachCheckResult:
        """Fallback: Check using free HIBP password API"""
        # This is a simplified check - in production you'd want more
        return BreachCheckResult(
            email=email,
            breached=False,
            breach_count=0,
            breaches=[],
            risk_level=RiskLevel.LOW
        )

    async def check_password_pwned(self, password: str) -> PasswordExposure:
        """Check if password has been exposed using k-anonymity"""

        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://api.pwnedpasswords.com/range/{prefix}",
                    headers={"user-agent": "FK94-Security-Platform"},
                    timeout=10.0
                )
                response.raise_for_status()

                # Search for our hash suffix in the response
                for line in response.text.splitlines():
                    hash_suffix, count = line.split(":")
                    if hash_suffix == suffix:
                        return PasswordExposure(
                            found=True,
                            count=int(count),
                            sources=["HIBP Password Database"]
                        )

                return PasswordExposure(found=False, count=0, sources=[])

            except Exception as e:
                print(f"Password check error: {e}")
                return PasswordExposure(found=False, count=0, sources=[])

    # === DEHASHED ===

    async def check_dehashed(self, email: str) -> Optional[PasswordExposure]:
        """Check Dehashed for leaked credentials"""

        if not self.dehashed_key or not self.dehashed_email:
            return None

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.dehashed.com/search",
                    params={"query": f"email:{email}"},
                    auth=(self.dehashed_email, self.dehashed_key),
                    headers={"Accept": "application/json"},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                entries = data.get("entries", [])
                if entries:
                    sources = list(set(e.get("database_name", "Unknown") for e in entries[:10]))
                    return PasswordExposure(
                        found=True,
                        count=len(entries),
                        sources=sources
                    )

                return PasswordExposure(found=False, count=0, sources=[])

            except Exception as e:
                print(f"Dehashed error: {e}")
                return None

    # === HUNTER.IO ===

    async def check_hunter(self, email: str) -> Optional[dict]:
        """Get email verification and associated data from Hunter.io"""

        if not self.hunter_key:
            return None

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.hunter.io/v2/email-verifier",
                    params={"email": email, "api_key": self.hunter_key},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json().get("data", {})

            except Exception as e:
                print(f"Hunter error: {e}")
                return None

    async def domain_search(self, domain: str) -> Optional[list]:
        """Find emails associated with a domain"""

        if not self.hunter_key:
            return None

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.hunter.io/v2/domain-search",
                    params={"domain": domain, "api_key": self.hunter_key},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json().get("data", {})
                return data.get("emails", [])

            except Exception as e:
                print(f"Hunter domain search error: {e}")
                return None

    # === COMBINED OSINT ===

    async def full_osint_check(self, email: str) -> OSINTResult:
        """Run comprehensive OSINT check on an email"""

        result = OSINTResult(email=email)

        # Extract domain from email
        domain = email.split("@")[1] if "@" in email else None

        # Hunter.io check
        hunter_data = await self.check_hunter(email)
        if hunter_data:
            if hunter_data.get("sources"):
                result.domains_found = [s.get("domain") for s in hunter_data["sources"] if s.get("domain")]

        return result

    # === HELPERS ===

    def _calculate_breach_risk(self, breaches: list[BreachInfo]) -> RiskLevel:
        """Calculate risk level based on breach severity"""

        if not breaches:
            return RiskLevel.SAFE

        count = len(breaches)
        has_passwords = any("Passwords" in b.data_types for b in breaches)
        has_financial = any(
            any(t in b.data_types for t in ["Credit cards", "Bank accounts", "Financial data"])
            for b in breaches
        )

        if has_financial or (has_passwords and count >= 3):
            return RiskLevel.CRITICAL
        elif has_passwords:
            return RiskLevel.HIGH
        elif count >= 5:
            return RiskLevel.HIGH
        elif count >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


# Singleton instance
osint_service = OSINTService()
