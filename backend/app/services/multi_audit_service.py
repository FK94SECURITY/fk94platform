"""
FK94 Security Platform - Multi-Audit Service
Handles audits for username, phone, domain, name, IP
"""
import httpx
import asyncio
import socket
import ssl
import re
from datetime import datetime
from typing import Optional
from app.models.schemas import (
    RiskLevel, UsernameResult, PhoneResult, DomainResult,
    NameResult, IPResult, WalletResult, ExchangeInteraction
)

# Common platforms to check for username
USERNAME_PLATFORMS = [
    {"name": "Twitter/X", "url": "https://twitter.com/{}", "check_type": "status"},
    {"name": "Instagram", "url": "https://instagram.com/{}", "check_type": "status"},
    {"name": "GitHub", "url": "https://github.com/{}", "check_type": "status"},
    {"name": "Reddit", "url": "https://reddit.com/user/{}", "check_type": "status"},
    {"name": "TikTok", "url": "https://tiktok.com/@{}", "check_type": "status"},
    {"name": "LinkedIn", "url": "https://linkedin.com/in/{}", "check_type": "status"},
    {"name": "YouTube", "url": "https://youtube.com/@{}", "check_type": "status"},
    {"name": "Pinterest", "url": "https://pinterest.com/{}", "check_type": "status"},
    {"name": "Twitch", "url": "https://twitch.tv/{}", "check_type": "status"},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}", "check_type": "status"},
    {"name": "Medium", "url": "https://medium.com/@{}", "check_type": "status"},
    {"name": "Telegram", "url": "https://t.me/{}", "check_type": "status"},
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}", "check_type": "status"},
    {"name": "Flickr", "url": "https://flickr.com/people/{}", "check_type": "status"},
    {"name": "Vimeo", "url": "https://vimeo.com/{}", "check_type": "status"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}", "check_type": "status"},
    {"name": "DeviantArt", "url": "https://deviantart.com/{}", "check_type": "status"},
    {"name": "Patreon", "url": "https://patreon.com/{}", "check_type": "status"},
    {"name": "GitLab", "url": "https://gitlab.com/{}", "check_type": "status"},
    {"name": "Bitbucket", "url": "https://bitbucket.org/{}", "check_type": "status"},
]


async def check_username(username: str) -> UsernameResult:
    """Check username across multiple platforms"""
    platforms_found = []
    profile_urls = []

    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
        tasks = []
        for platform in USERNAME_PLATFORMS:
            url = platform["url"].format(username)
            tasks.append(check_platform(client, platform["name"], url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, dict) and result.get("found"):
                platforms_found.append(result["name"])
                profile_urls.append(result["url"])

    # Calculate risk based on exposure
    platforms_count = len(platforms_found)
    if platforms_count >= 10:
        risk_level = RiskLevel.HIGH
    elif platforms_count >= 5:
        risk_level = RiskLevel.MEDIUM
    elif platforms_count >= 1:
        risk_level = RiskLevel.LOW
    else:
        risk_level = RiskLevel.SAFE

    return UsernameResult(
        username=username,
        platforms_found=platforms_found,
        platforms_checked=len(USERNAME_PLATFORMS),
        profile_urls=profile_urls,
        risk_level=risk_level
    )


async def check_platform(client: httpx.AsyncClient, name: str, url: str) -> dict:
    """Check if username exists on a platform"""
    try:
        response = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        # Most platforms return 404 for non-existent users
        if response.status_code == 200:
            return {"found": True, "name": name, "url": url}
    except Exception:
        pass
    return {"found": False, "name": name, "url": url}


async def check_phone(phone: str, country_code: str = "AR") -> PhoneResult:
    """
    Check phone number using Truecaller.
    Tries Telegram bot first (free), then direct API as fallback.
    """
    from app.core.config import settings

    # Clean phone number
    clean_phone = re.sub(r'[^\d+]', '', phone)

    tc_result = None

    # Try Telegram bot first (FREE)
    if settings.TELEGRAM_API_ID is not None and settings.TELEGRAM_API_HASH and settings.TELEGRAM_SESSION:
        try:
            from app.services.telegram_truecaller_service import telegram_truecaller_service
            tc_result = await telegram_truecaller_service.lookup(clean_phone, country_code)
        except Exception as e:
            print(f"Telegram Truecaller error: {e}")

    # Fallback to direct Truecaller API
    if (tc_result is None or not tc_result.found) and settings.TRUECALLER_TOKEN:
        try:
            from app.services.truecaller_service import truecaller_service
            tc_result = await truecaller_service.lookup(clean_phone, country_code)
        except Exception as e:
            print(f"Direct Truecaller error: {e}")

    # Process result
    if tc_result and tc_result.found:
        spam_score = tc_result.spam_score
        if spam_score >= 7 or "scam" in tc_result.tags:
            risk_level = RiskLevel.CRITICAL
        elif spam_score >= 5 or "spam" in tc_result.tags:
            risk_level = RiskLevel.HIGH
        elif spam_score >= 3:
            risk_level = RiskLevel.MEDIUM
        elif spam_score >= 1 or tc_result.tags:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE

        return PhoneResult(
            phone=clean_phone,
            carrier=tc_result.carrier or "Unknown",
            line_type=tc_result.phone_type or "mobile",
            location=tc_result.location or country_code,
            breaches_found=0,
            spam_reports=spam_score,
            risk_level=risk_level,
            owner_name=tc_result.name,
            tags=tc_result.tags,
            email=tc_result.email
        )
    else:
        # No data found
        error_msg = tc_result.error if tc_result else "Truecaller not configured"
        return PhoneResult(
            phone=clean_phone,
            carrier="Unknown",
            line_type="Unknown",
            location=country_code,
            breaches_found=0,
            spam_reports=0,
            risk_level=RiskLevel.LOW,
            error=error_msg
        )


async def check_domain(domain: str) -> DomainResult:
    """Check domain security configuration"""
    import dns.resolver

    ssl_valid = False
    ssl_expiry = None
    dns_records = {}
    spf_configured = False
    dmarc_configured = False
    vulnerabilities = []

    # Check SSL
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                ssl_valid = True
                ssl_expiry = cert.get('notAfter', '')
    except Exception as e:
        vulnerabilities.append(f"SSL Error: {str(e)[:50]}")

    # Check DNS records
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5

        # A records
        try:
            answers = resolver.resolve(domain, 'A')
            dns_records['A'] = [str(r) for r in answers]
        except Exception:
            pass

        # MX records
        try:
            answers = resolver.resolve(domain, 'MX')
            dns_records['MX'] = [str(r) for r in answers]
        except Exception:
            pass

        # TXT records (for SPF/DKIM)
        try:
            answers = resolver.resolve(domain, 'TXT')
            txt_records = [str(r) for r in answers]
            dns_records['TXT'] = txt_records

            for record in txt_records:
                if 'v=spf1' in record:
                    spf_configured = True
        except Exception:
            pass

        # DMARC
        try:
            answers = resolver.resolve(f'_dmarc.{domain}', 'TXT')
            dmarc_configured = True
            dns_records['DMARC'] = [str(r) for r in answers]
        except Exception:
            pass

    except Exception as e:
        vulnerabilities.append(f"DNS Error: {str(e)[:50]}")

    # Calculate risk
    risk_factors = 0
    if not ssl_valid:
        risk_factors += 2
        vulnerabilities.append("No valid SSL certificate")
    if not spf_configured:
        risk_factors += 1
        vulnerabilities.append("SPF not configured - email spoofing risk")
    if not dmarc_configured:
        risk_factors += 1
        vulnerabilities.append("DMARC not configured - email security risk")

    if risk_factors >= 3:
        risk_level = RiskLevel.HIGH
    elif risk_factors >= 2:
        risk_level = RiskLevel.MEDIUM
    elif risk_factors >= 1:
        risk_level = RiskLevel.LOW
    else:
        risk_level = RiskLevel.SAFE

    return DomainResult(
        domain=domain,
        ssl_valid=ssl_valid,
        ssl_expiry=ssl_expiry,
        dns_records=dns_records,
        spf_configured=spf_configured,
        dmarc_configured=dmarc_configured,
        dkim_configured=False,  # Requires more complex check
        open_ports=[],
        vulnerabilities=vulnerabilities,
        risk_level=risk_level
    )


async def check_name(full_name: str, location: Optional[str] = None) -> NameResult:
    """Search for public information about a person"""
    # In production, integrate with:
    # - Pipl API
    # - Whitepages API
    # - Social media searches
    # - News API

    possible_profiles = []
    public_records = []
    news_mentions = []

    # For now, simulate searching by generating possible profile URLs
    name_parts = full_name.lower().split()
    if len(name_parts) >= 2:
        username_variants = [
            "".join(name_parts),
            f"{name_parts[0]}{name_parts[-1]}",
            f"{name_parts[0]}.{name_parts[-1]}",
            f"{name_parts[0]}_{name_parts[-1]}",
        ]

        for variant in username_variants:
            possible_profiles.append({
                "platform": "LinkedIn",
                "url": f"https://linkedin.com/in/{variant}",
                "confidence": "possible"
            })
            possible_profiles.append({
                "platform": "Twitter",
                "url": f"https://twitter.com/{variant}",
                "confidence": "possible"
            })

    return NameResult(
        full_name=full_name,
        possible_profiles=possible_profiles,
        public_records=public_records,
        news_mentions=news_mentions,
        risk_level=RiskLevel.MEDIUM if possible_profiles else RiskLevel.SAFE
    )


async def check_ip(ip_address: str) -> IPResult:
    """Check IP address reputation and information"""
    location = None
    isp = None
    is_vpn = False
    is_proxy = False
    is_tor = False
    blacklisted = False
    blacklist_sources = []
    abuse_reports = 0

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Check ip-api.com for geolocation (free, no key needed)
        try:
            response = await client.get(f"http://ip-api.com/json/{ip_address}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    location = f"{data.get('city', '')}, {data.get('country', '')}"
                    isp = data.get("isp", "")

                    # Check if hosting provider (likely VPN/proxy)
                    org = data.get("org", "").lower()
                    if any(x in org for x in ["hosting", "cloud", "datacenter", "vpn"]):
                        is_vpn = True
        except Exception:
            pass

        # Check AbuseIPDB (requires API key)
        # For now, simulate

    # Calculate risk
    risk_factors = 0
    if is_vpn or is_proxy:
        risk_factors += 1
    if is_tor:
        risk_factors += 2
    if blacklisted:
        risk_factors += 2
    if abuse_reports > 10:
        risk_factors += 1

    if risk_factors >= 3:
        risk_level = RiskLevel.HIGH
    elif risk_factors >= 2:
        risk_level = RiskLevel.MEDIUM
    elif risk_factors >= 1:
        risk_level = RiskLevel.LOW
    else:
        risk_level = RiskLevel.SAFE

    return IPResult(
        ip_address=ip_address,
        location=location,
        isp=isp,
        is_vpn=is_vpn,
        is_proxy=is_proxy,
        is_tor=is_tor,
        blacklisted=blacklisted,
        blacklist_sources=blacklist_sources,
        abuse_reports=abuse_reports,
        risk_level=risk_level
    )


async def check_wallet(address: str, chain: str = "ethereum") -> WalletResult:
    """Check crypto wallet with deep scan: exchange interactions, mixers, OFAC, traceability."""
    from app.services.wallet_deep_scan import (
        deep_scan_eth, deep_scan_btc, check_ofac_eth,
        calculate_traceability_score, calculate_wallet_risk,
        KNOWN_EXCHANGE_ADDRESSES_ETH, KNOWN_EXCHANGE_ADDRESSES_BTC,
    )

    # Detect chain from address format
    if address.startswith("0x") and len(address) == 42:
        chain = "ethereum"
    elif address.startswith("bc1") or address.startswith("1") or address.startswith("3"):
        chain = "bitcoin"
    elif len(address) >= 32 and len(address) <= 44 and not address.startswith("0x"):
        chain = "solana"

    scan_result: dict = {}
    ofac_sanctioned = False
    warnings: list[str] = []

    try:
        if chain == "ethereum":
            scan_result = await deep_scan_eth(address)
            ofac_sanctioned = await check_ofac_eth(address)
        elif chain == "bitcoin":
            scan_result = await deep_scan_btc(address)
        else:
            warnings.append(f"Deep scan not supported for {chain} yet")
    except Exception as e:
        warnings.append(f"Deep scan error: {str(e)[:80]}")

    # Check if the address itself is a known exchange
    addr_lower = address.lower()
    labeled = False
    label = None
    if chain == "ethereum" and addr_lower in KNOWN_EXCHANGE_ADDRESSES_ETH:
        labeled = True
        label = KNOWN_EXCHANGE_ADDRESSES_ETH[addr_lower]
    elif chain == "bitcoin" and address in KNOWN_EXCHANGE_ADDRESSES_BTC:
        labeled = True
        label = KNOWN_EXCHANGE_ADDRESSES_BTC[address]

    # Calculate traceability
    traceability_score, traceability_details = calculate_traceability_score(
        scan_result, ofac_sanctioned
    )

    exchanges_detected = scan_result.get("exchanges_detected", [])
    used_mixer = scan_result.get("used_mixer", False)

    risk_level = calculate_wallet_risk(
        traceability_score, ofac_sanctioned, used_mixer, exchanges_detected
    )

    all_warnings = scan_result.get("warnings", []) + warnings
    if ofac_sanctioned:
        all_warnings.insert(0, "ADDRESS IS OFAC SANCTIONED")
    if used_mixer:
        all_warnings.insert(0, "Mixer (Tornado Cash) usage detected")

    return WalletResult(
        address=address,
        chain=chain,
        balance=scan_result.get("balance"),
        transaction_count=scan_result.get("tx_count"),
        linked_addresses=[],
        labeled=labeled,
        label=label,
        sanctions_check=ofac_sanctioned,
        risk_level=risk_level,
        # Deep scan fields
        deep_scan=True,
        exchange_interactions=scan_result.get("exchange_interactions", []),
        exchanges_detected=exchanges_detected,
        is_traceable=traceability_score >= 30,
        traceability_score=traceability_score,
        traceability_details=traceability_details,
        mixer_interactions=scan_result.get("mixer_interactions", []),
        used_mixer=used_mixer,
        ofac_sanctioned=ofac_sanctioned,
        first_tx_date=scan_result.get("first_tx_date"),
        last_tx_date=scan_result.get("last_tx_date"),
        unique_counterparties=scan_result.get("counterparties", 0),
        scan_warnings=all_warnings,
    )
