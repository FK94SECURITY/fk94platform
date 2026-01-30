"""
FK94 Security Platform - Audit Runner
"""
from datetime import datetime, timezone

from app.models.schemas import (
    AuditResult,
    AuditType,
    FullAuditRequest,
    MultiAuditRequest,
    RiskLevel,
    SecurityScore,
)
from app.services.deepseek_service import deepseek_service
from app.services.multi_audit_service import (
    check_domain,
    check_ip,
    check_name,
    check_phone,
    check_username,
    check_wallet,
)
from app.services.osint_service import osint_service
from app.services.scoring_service import scoring_service


async def run_full_audit(request: FullAuditRequest) -> AuditResult:
    """Run comprehensive security audit on an email."""
    audit_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")[-8:]
    email = request.email

    breach_result = None
    password_exposure = None
    osint_result = None

    if request.check_breaches:
        breach_result = await osint_service.check_hibp_breaches(email)
        dehashed = await osint_service.check_dehashed(email)
        if dehashed:
            password_exposure = dehashed

    if request.password:
        password_exposure = await osint_service.check_password_pwned(request.password)

    if request.check_osint:
        osint_result = await osint_service.full_osint_check(email)

    security_score = scoring_service.calculate_score(
        breach_result=breach_result,
        password_exposure=password_exposure,
        osint_result=osint_result,
    )

    recommendations = scoring_service.get_recommendations(security_score, breach_result)

    audit_data = {
        "email": email,
        "security_score": security_score.model_dump(),
        "breach_check": breach_result.model_dump() if breach_result else None,
        "password_exposure": password_exposure.model_dump() if password_exposure else None,
        "osint_result": osint_result.model_dump() if osint_result else None,
    }

    ai_analysis = await deepseek_service.analyze_audit(audit_data)

    return AuditResult(
        id=audit_id,
        audit_type=AuditType.EMAIL,
        query_value=email,
        email=email,
        timestamp=datetime.now(timezone.utc),
        security_score=security_score,
        breach_check=breach_result,
        password_exposure=password_exposure,
        osint_result=osint_result,
        ai_analysis=ai_analysis,
        recommendations=recommendations,
    )


async def run_multi_audit(request: MultiAuditRequest) -> AuditResult:
    """Run audit on different data types: username, phone, domain, name, IP, wallet."""
    audit_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")[-8:]
    audit_type = request.audit_type
    value = request.value

    username_result = None
    phone_result = None
    domain_result = None
    name_result = None
    ip_result = None
    wallet_result = None

    if audit_type == AuditType.USERNAME:
        username_result = await check_username(value)
        risk_level = username_result.risk_level
    elif audit_type == AuditType.PHONE:
        country = request.extra_data.get("country_code", "US") if request.extra_data else "US"
        phone_result = await check_phone(value, country)
        risk_level = phone_result.risk_level
    elif audit_type == AuditType.DOMAIN:
        domain_result = await check_domain(value)
        risk_level = domain_result.risk_level
    elif audit_type == AuditType.NAME:
        location = request.extra_data.get("location") if request.extra_data else None
        name_result = await check_name(value, location)
        risk_level = name_result.risk_level
    elif audit_type == AuditType.IP:
        ip_result = await check_ip(value)
        risk_level = ip_result.risk_level
    elif audit_type == AuditType.WALLET:
        chain = request.extra_data.get("chain", "ethereum") if request.extra_data else "ethereum"
        wallet_result = await check_wallet(value, chain)
        risk_level = wallet_result.risk_level
    else:
        raise ValueError(f"Unsupported audit type: {audit_type}")

    score_map = {
        RiskLevel.CRITICAL: 15,
        RiskLevel.HIGH: 35,
        RiskLevel.MEDIUM: 60,
        RiskLevel.LOW: 80,
        RiskLevel.SAFE: 95,
    }
    score = score_map.get(risk_level, 50)

    security_score = SecurityScore(
        score=score,
        risk_level=risk_level,
        breakdown={audit_type.value: 100 - score},
        issues_critical=1 if risk_level == RiskLevel.CRITICAL else 0,
        issues_high=1 if risk_level == RiskLevel.HIGH else 0,
        issues_medium=1 if risk_level == RiskLevel.MEDIUM else 0,
        issues_low=1 if risk_level == RiskLevel.LOW else 0,
    )

    recommendations = generate_recommendations_for_type(
        audit_type,
        value,
        risk_level,
        username_result,
        phone_result,
        domain_result,
        name_result,
        ip_result,
        wallet_result,
    )

    audit_data = {
        "audit_type": audit_type.value,
        "value": value,
        "security_score": security_score.model_dump(),
        "username_result": username_result.model_dump() if username_result else None,
        "phone_result": phone_result.model_dump() if phone_result else None,
        "domain_result": domain_result.model_dump() if domain_result else None,
        "name_result": name_result.model_dump() if name_result else None,
        "ip_result": ip_result.model_dump() if ip_result else None,
        "wallet_result": wallet_result.model_dump() if wallet_result else None,
    }

    ai_analysis = await deepseek_service.analyze_audit(audit_data)

    return AuditResult(
        id=audit_id,
        audit_type=audit_type,
        query_value=value,
        timestamp=datetime.now(timezone.utc),
        security_score=security_score,
        username_result=username_result,
        phone_result=phone_result,
        domain_result=domain_result,
        name_result=name_result,
        ip_result=ip_result,
        wallet_result=wallet_result,
        ai_analysis=ai_analysis,
        recommendations=recommendations,
    )


def generate_recommendations_for_type(
    audit_type: AuditType,
    value: str,
    risk_level,
    username_result=None,
    phone_result=None,
    domain_result=None,
    name_result=None,
    ip_result=None,
    wallet_result=None,
) -> list[str]:
    """Generate recommendations based on audit type and results."""
    recommendations = []

    if audit_type == AuditType.USERNAME:
        if username_result and len(username_result.platforms_found) > 5:
            recommendations.append(
                "Consider reducing your digital footprint by deleting unused accounts"
            )
            recommendations.append("Use different usernames for sensitive vs. public accounts")
        recommendations.append("Enable 2FA on all accounts using this username")
        recommendations.append(
            "Check if any of these accounts have been compromised in data breaches"
        )

    elif audit_type == AuditType.PHONE:
        recommendations.append("Consider using a secondary number for online sign-ups")
        recommendations.append("Register with the Do Not Call registry")
        recommendations.append("Review which services have your phone number")

    elif audit_type == AuditType.DOMAIN:
        if domain_result:
            if not domain_result.ssl_valid:
                recommendations.append("Install a valid SSL certificate immediately")
            if not domain_result.spf_configured:
                recommendations.append("Configure SPF records to prevent email spoofing")
            if not domain_result.dmarc_configured:
                recommendations.append("Set up DMARC policy for email authentication")
        recommendations.append("Regularly monitor your domain for security issues")

    elif audit_type == AuditType.NAME:
        recommendations.append("Search for yourself periodically to monitor your online presence")
        recommendations.append("Request removal from data broker sites")
        recommendations.append("Set up Google Alerts for your name")

    elif audit_type == AuditType.IP:
        if ip_result and (ip_result.is_vpn or ip_result.is_proxy):
            recommendations.append("Your IP appears to be from a VPN/proxy - good for privacy")
        else:
            recommendations.append("Consider using a VPN for enhanced privacy")
        if ip_result and ip_result.blacklisted:
            recommendations.append("Your IP is blacklisted - contact your ISP")

    elif audit_type == AuditType.WALLET:
        if wallet_result:
            if wallet_result.labeled:
                recommendations.append(
                    "Your wallet is labeled/known - consider using a fresh wallet for privacy"
                )
            if wallet_result.sanctions_check:
                recommendations.append(
                    "CRITICAL: This wallet may be on sanctions lists - seek legal advice"
                )
            if wallet_result.transaction_count and wallet_result.transaction_count > 50:
                recommendations.append(
                    "High transaction volume increases traceability - consider using mixers or fresh wallets"
                )
        recommendations.append(
            "Never share wallet addresses on public forums linked to your identity"
        )
        recommendations.append("Consider using privacy-focused chains or coin-joining services")

    return recommendations
