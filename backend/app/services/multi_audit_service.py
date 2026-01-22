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
    NameResult, IPResult, WalletResult
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
        except:
            pass

        # MX records
        try:
            answers = resolver.resolve(domain, 'MX')
            dns_records['MX'] = [str(r) for r in answers]
        except:
            pass

        # TXT records (for SPF/DKIM)
        try:
            answers = resolver.resolve(domain, 'TXT')
            txt_records = [str(r) for r in answers]
            dns_records['TXT'] = txt_records

            for record in txt_records:
                if 'v=spf1' in record:
                    spf_configured = True
        except:
            pass

        # DMARC
        try:
            answers = resolver.resolve(f'_dmarc.{domain}', 'TXT')
            dmarc_configured = True
            dns_records['DMARC'] = [str(r) for r in answers]
        except:
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
        except:
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
    """Check crypto wallet for identity linking and sanctions"""
    balance = None
    transaction_count = None
    linked_addresses = []
    labeled = False
    label = None
    sanctions_check = False

    # Detect chain from address format if not specified
    if address.startswith("0x") and len(address) == 42:
        chain = "ethereum"
    elif address.startswith("bc1") or address.startswith("1") or address.startswith("3"):
        chain = "bitcoin"
    elif len(address) >= 32 and len(address) <= 44 and not address.startswith("0x"):
        chain = "solana"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # For Ethereum addresses, use Etherscan API (free tier)
        if chain == "ethereum":
            try:
                # Get balance from Etherscan (no API key needed for basic queries)
                response = await client.get(
                    f"https://api.etherscan.io/api",
                    params={
                        "module": "account",
                        "action": "balance",
                        "address": address,
                        "tag": "latest"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        wei_balance = int(data.get("result", 0))
                        eth_balance = wei_balance / 1e18
                        balance = f"{eth_balance:.4f} ETH"

                # Get transaction count
                response = await client.get(
                    f"https://api.etherscan.io/api",
                    params={
                        "module": "account",
                        "action": "txlist",
                        "address": address,
                        "startblock": 0,
                        "endblock": 99999999,
                        "page": 1,
                        "offset": 1,
                        "sort": "desc"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        # Get total count via another call
                        response2 = await client.get(
                            f"https://api.etherscan.io/api",
                            params={
                                "module": "account",
                                "action": "txlist",
                                "address": address,
                                "startblock": 0,
                                "endblock": 99999999,
                                "page": 1,
                                "offset": 10000,
                                "sort": "asc"
                            }
                        )
                        if response2.status_code == 200:
                            data2 = response2.json()
                            if data2.get("result"):
                                transaction_count = len(data2.get("result", []))

                # Check known labeled addresses (exchanges, contracts)
                known_addresses = {
                    "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae": ("Ethereum Foundation", True),
                    "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": ("Binance", True),
                    "0xd24400ae8bfebb18ca49be86258a3c749cf46853": ("Gemini", True),
                    "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0": ("Kraken", True),
                }
                addr_lower = address.lower()
                if addr_lower in known_addresses:
                    label, labeled = known_addresses[addr_lower]

            except Exception as e:
                print(f"Etherscan error: {e}")

        elif chain == "bitcoin":
            try:
                # Check blockchain.info for basic info
                response = await client.get(
                    f"https://blockchain.info/rawaddr/{address}?limit=0"
                )
                if response.status_code == 200:
                    data = response.json()
                    balance = str(data.get("final_balance", 0) / 100000000) + " BTC"
                    transaction_count = data.get("n_tx", 0)
            except:
                pass

    # Calculate risk
    # High risk if wallet is labeled (means identity is potentially known)
    # High risk if sanctioned
    risk_factors = 0

    if labeled:
        risk_factors += 2
    if sanctions_check:
        risk_factors += 3
    if transaction_count and transaction_count > 100:
        risk_factors += 1  # High activity = more visibility
    if linked_addresses:
        risk_factors += len(linked_addresses)

    if risk_factors >= 3 or sanctions_check:
        risk_level = RiskLevel.HIGH
    elif risk_factors >= 2 or labeled:
        risk_level = RiskLevel.MEDIUM
    elif risk_factors >= 1:
        risk_level = RiskLevel.LOW
    else:
        risk_level = RiskLevel.SAFE

    return WalletResult(
        address=address,
        chain=chain,
        balance=balance,
        transaction_count=transaction_count,
        linked_addresses=linked_addresses,
        labeled=labeled,
        label=label,
        sanctions_check=sanctions_check,
        risk_level=risk_level
    )
