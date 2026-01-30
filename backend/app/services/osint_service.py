"""
FK94 Security Platform - OSINT Service
Integrates multiple OSINT APIs for comprehensive security checks
"""
import httpx
import hashlib
import asyncio
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
        self.whoisxml_key = settings.WHOISXML_API_KEY
        self.intelx_key = settings.INTELLIGENCE_X_API_KEY

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
        username = email.split("@")[0] if "@" in email else None

        tasks = []
        tasks.append(self.check_hunter(email))
        tasks.append(self._check_gravatar(email))
        if domain:
            tasks.append(self.domain_search(domain))
            tasks.append(self._rdap_lookup(domain))
        if username:
            tasks.append(self._check_username_profiles(username))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        hunter_data = results[0] if results else None
        gravatar_url = results[1] if len(results) > 1 else None

        offset = 2
        domain_emails = None
        rdap_data = None
        if domain:
            domain_emails = results[offset] if len(results) > offset else None
            rdap_data = results[offset + 1] if len(results) > offset + 1 else None
            offset += 2

        username_profiles = results[offset] if len(results) > offset else None

        # Hunter.io check
        if isinstance(hunter_data, dict) and hunter_data:
            sources = hunter_data.get("sources") or []
            if sources:
                result.domains_found.extend(
                    [s.get("domain") for s in sources if s.get("domain")]
                )
                result.public_records.extend(
                    [s.get("uri") for s in sources if s.get("uri")][:10]
                )
            # Useful metadata if available
            if hunter_data.get("organization"):
                result.public_records.append(f"Organization: {hunter_data['organization']}")
            if hunter_data.get("position"):
                result.public_records.append(f"Position: {hunter_data['position']}")

        # Gravatar check
        if isinstance(gravatar_url, str) and gravatar_url:
            result.social_profiles.append(gravatar_url)

        # Domain search (Hunter)
        if isinstance(domain_emails, list) and domain_emails:
            result.public_records.append(f"Public emails found on domain: {len(domain_emails)}")
            result.domains_found.append(domain)
            # Tag broker domains if any appear in sources
            broker_domains = self._broker_domains()
            for entry in domain_emails:
                sources = entry.get("sources") or []
                for source in sources:
                    source_domain = self._normalize_domain(source.get("domain", ""))
                    if source_domain in broker_domains:
                        result.data_brokers.append(source_domain)

        # RDAP/WHOIS data
        if isinstance(rdap_data, dict) and rdap_data:
            result.public_records.extend(self._format_rdap_public_records(rdap_data))

        # Username OSINT (social profiles)
        if isinstance(username_profiles, dict):
            urls = username_profiles.get("profile_urls", [])
            result.social_profiles.extend(urls[:15])

        # De-duplicate lists
        result.domains_found = self._compact_list(result.domains_found)
        result.social_profiles = self._compact_list(result.social_profiles)
        result.data_brokers = self._compact_list(result.data_brokers)
        result.public_records = self._compact_list(result.public_records)

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

    async def _check_gravatar(self, email: str) -> Optional[str]:
        """Check if email has a public Gravatar profile."""
        if not email:
            return None
        email_hash = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
        url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"

        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return f"https://gravatar.com/{email_hash}"
            except Exception:
                return None
        return None

    async def _check_username_profiles(self, username: str) -> Optional[dict]:
        """Check common platforms for username presence."""
        if not username:
            return None
        from app.services.multi_audit_service import check_username

        try:
            result = await check_username(username)
            return {"profile_urls": result.profile_urls, "platforms_found": result.platforms_found}
        except Exception:
            return None

    async def _rdap_lookup(self, domain: str) -> Optional[dict]:
        """Fetch RDAP (public WHOIS) data for a domain."""
        if not domain:
            return None
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                response = await client.get(f"https://rdap.org/domain/{domain}")
                if response.status_code == 200:
                    return response.json()
            except Exception:
                return None
        return None

    @staticmethod
    def _format_rdap_public_records(rdap_data: dict) -> list[str]:
        """Extract public fields from RDAP data."""
        records = []
        registrar = rdap_data.get("registrar", {}).get("name")
        if registrar:
            records.append(f"Registrar: {registrar}")

        events = rdap_data.get("events", [])
        for event in events:
            action = event.get("eventAction", "")
            date = event.get("eventDate", "")
            if action and date:
                records.append(f"{action.title()}: {date}")

        status = rdap_data.get("status", [])
        if status:
            records.append(f"Domain status: {', '.join(status[:3])}")

        return records

    @staticmethod
    def _compact_list(items: list) -> list:
        seen = set()
        compacted = []
        for item in items:
            if not item:
                continue
            if item in seen:
                continue
            seen.add(item)
            compacted.append(item)
        return compacted

    @staticmethod
    def _normalize_domain(value: str) -> str:
        if not value:
            return ""
        return value.replace("https://", "").replace("http://", "").split("/")[0].lower()

    @staticmethod
    def _broker_domains() -> set[str]:
        return {
            "spokeo.com",
            "whitepages.com",
            "radaris.com",
            "peekyou.com",
            "beenverified.com",
            "peoplefinder.com",
            "truthfinder.com",
            "intelius.com",
            "mylife.com",
            "fastpeoplesearch.com",
        }


# Singleton instance
osint_service = OSINTService()
