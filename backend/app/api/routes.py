"""
FK94 Security Platform - API Routes
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
import uuid
import io

from app.models.schemas import (
    EmailCheckRequest, FullAuditRequest, AIAnalysisRequest,
    UsernameCheckRequest, PhoneCheckRequest, DomainCheckRequest,
    NameCheckRequest, IPCheckRequest, WalletCheckRequest, MultiAuditRequest, AuditType,
    BreachCheckResult, AuditResult, AIResponse, SecurityScore,
    UsernameResult, PhoneResult, DomainResult, NameResult, IPResult, WalletResult
)
from app.services.osint_service import osint_service
from app.services.deepseek_service import deepseek_service
from app.services.scoring_service import scoring_service
from app.services.pdf_service import pdf_service
from app.services.multi_audit_service import (
    check_username, check_phone, check_domain, check_name, check_ip, check_wallet
)


router = APIRouter()


# === QUICK CHECKS ===

@router.post("/check/email", response_model=BreachCheckResult)
async def check_email_breaches(request: EmailCheckRequest):
    """
    Quick breach check for an email address.
    Returns breach count and risk level.
    """
    try:
        result = await osint_service.check_hibp_breaches(request.email)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check/username", response_model=UsernameResult)
async def check_username_endpoint(request: UsernameCheckRequest):
    """
    Check if a username exists across multiple platforms.
    """
    try:
        result = await check_username(request.username)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check/phone", response_model=PhoneResult)
async def check_phone_endpoint(request: PhoneCheckRequest):
    """
    Check phone number information and breaches.
    """
    try:
        result = await check_phone(request.phone, request.country_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check/domain", response_model=DomainResult)
async def check_domain_endpoint(request: DomainCheckRequest):
    """
    Check domain security configuration (SSL, DNS, SPF, DMARC).
    """
    try:
        result = await check_domain(request.domain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check/name", response_model=NameResult)
async def check_name_endpoint(request: NameCheckRequest):
    """
    Search for public information about a person.
    """
    try:
        result = await check_name(request.full_name, request.location)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check/ip", response_model=IPResult)
async def check_ip_endpoint(request: IPCheckRequest):
    """
    Check IP address reputation and information.
    """
    try:
        result = await check_ip(request.ip_address)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check/wallet", response_model=WalletResult)
async def check_wallet_endpoint(request: WalletCheckRequest):
    """
    Check crypto wallet for identity linking and sanctions.
    """
    try:
        result = await check_wallet(request.address, request.chain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check/password")
async def check_password_exposure(password: str):
    """
    Check if a password has been exposed in data breaches.
    Uses k-anonymity - password is never sent over the network.
    """
    try:
        result = await osint_service.check_password_pwned(password)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === FULL AUDIT ===

@router.post("/audit/full", response_model=AuditResult)
async def run_full_audit(request: FullAuditRequest):
    """
    Run comprehensive security audit on an email.
    Checks breaches, password exposure, OSINT, and generates AI analysis.
    """
    try:
        audit_id = str(uuid.uuid4())[:8]
        email = request.email

        # Run checks in parallel (simplified for now)
        breach_result = None
        password_exposure = None
        osint_result = None

        if request.check_breaches:
            breach_result = await osint_service.check_hibp_breaches(email)
            # Also check Dehashed if available
            dehashed = await osint_service.check_dehashed(email)
            if dehashed:
                password_exposure = dehashed

        # Check password if provided (HIBP Passwords API - FREE)
        if request.password:
            password_exposure = await osint_service.check_password_pwned(request.password)

        if request.check_osint:
            osint_result = await osint_service.full_osint_check(email)

        # Calculate security score
        security_score = scoring_service.calculate_score(
            breach_result=breach_result,
            password_exposure=password_exposure,
            osint_result=osint_result
        )

        # Get recommendations
        recommendations = scoring_service.get_recommendations(
            security_score, breach_result
        )

        # Build audit data for AI analysis
        audit_data = {
            "email": email,
            "security_score": security_score.model_dump(),
            "breach_check": breach_result.model_dump() if breach_result else None,
            "password_exposure": password_exposure.model_dump() if password_exposure else None,
            "osint_result": osint_result.model_dump() if osint_result else None
        }

        # Get AI analysis
        ai_analysis = await deepseek_service.analyze_audit(audit_data)

        return AuditResult(
            id=audit_id,
            audit_type=AuditType.EMAIL,
            query_value=email,
            email=email,
            timestamp=datetime.now(),
            security_score=security_score,
            breach_check=breach_result,
            password_exposure=password_exposure,
            osint_result=osint_result,
            ai_analysis=ai_analysis,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audit/multi", response_model=AuditResult)
async def run_multi_audit(request: MultiAuditRequest):
    """
    Run audit on different data types: username, phone, domain, name, or IP.
    """
    try:
        audit_id = str(uuid.uuid4())[:8]
        audit_type = request.audit_type
        value = request.value

        username_result = None
        phone_result = None
        domain_result = None
        name_result = None
        ip_result = None
        wallet_result = None

        # Run the appropriate check
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
            raise HTTPException(status_code=400, detail=f"Unsupported audit type: {audit_type}")

        # Calculate security score based on risk level
        from app.models.schemas import RiskLevel
        score_map = {
            RiskLevel.CRITICAL: 15,
            RiskLevel.HIGH: 35,
            RiskLevel.MEDIUM: 60,
            RiskLevel.LOW: 80,
            RiskLevel.SAFE: 95
        }
        score = score_map.get(risk_level, 50)

        security_score = SecurityScore(
            score=score,
            risk_level=risk_level,
            breakdown={audit_type.value: 100 - score},
            issues_critical=1 if risk_level == RiskLevel.CRITICAL else 0,
            issues_high=1 if risk_level == RiskLevel.HIGH else 0,
            issues_medium=1 if risk_level == RiskLevel.MEDIUM else 0,
            issues_low=1 if risk_level == RiskLevel.LOW else 0
        )

        # Generate recommendations based on audit type
        recommendations = generate_recommendations_for_type(
            audit_type, value, risk_level,
            username_result, phone_result, domain_result, name_result, ip_result
        )

        # Get AI analysis
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
            timestamp=datetime.now(),
            security_score=security_score,
            username_result=username_result,
            phone_result=phone_result,
            domain_result=domain_result,
            name_result=name_result,
            ip_result=ip_result,
            wallet_result=wallet_result,
            ai_analysis=ai_analysis,
            recommendations=recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_recommendations_for_type(
    audit_type: AuditType,
    value: str,
    risk_level,
    username_result=None,
    phone_result=None,
    domain_result=None,
    name_result=None,
    ip_result=None,
    wallet_result=None
) -> list[str]:
    """Generate recommendations based on audit type and results"""
    recommendations = []

    if audit_type == AuditType.USERNAME:
        if username_result and len(username_result.platforms_found) > 5:
            recommendations.append("Consider reducing your digital footprint by deleting unused accounts")
            recommendations.append("Use different usernames for sensitive vs. public accounts")
        recommendations.append("Enable 2FA on all accounts using this username")
        recommendations.append("Check if any of these accounts have been compromised in data breaches")

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
                recommendations.append("Your wallet is labeled/known - consider using a fresh wallet for privacy")
            if wallet_result.sanctions_check:
                recommendations.append("CRITICAL: This wallet may be on sanctions lists - seek legal advice")
            if wallet_result.transaction_count and wallet_result.transaction_count > 50:
                recommendations.append("High transaction volume increases traceability - consider using mixers or fresh wallets")
        recommendations.append("Never share wallet addresses on public forums linked to your identity")
        recommendations.append("Consider using privacy-focused chains or coin-joining services")

    return recommendations


# === SECURITY SCORE ===

@router.post("/score", response_model=SecurityScore)
async def get_security_score(request: EmailCheckRequest):
    """
    Get quick security score for an email.
    Faster than full audit, just breach check + score.
    """
    try:
        breach_result = await osint_service.check_hibp_breaches(request.email)
        score = scoring_service.calculate_score(breach_result=breach_result)
        return score
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === AI CHAT ===

@router.post("/ai/analyze", response_model=AIResponse)
async def ai_analyze(request: AIAnalysisRequest):
    """
    Ask the AI security analyst a question.
    Can include audit context for personalized advice.
    """
    try:
        response = await deepseek_service.analyze(
            request.query,
            context=request.context
        )

        # Extract recommendations if any
        recommendations = []
        if "recomend" in response.lower() or "deberías" in response.lower():
            lines = response.split("\n")
            for line in lines:
                if line.strip().startswith(("-", "•", "1.", "2.", "3.", "4.", "5.")):
                    recommendations.append(line.strip())

        return AIResponse(
            response=response,
            recommendations=recommendations[:5]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/chat")
async def ai_chat(message: str):
    """
    Simple chat endpoint for security questions.
    """
    try:
        response = await deepseek_service.chat(message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === HEALTH & STATUS ===

@router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.get("/status/apis")
async def api_status():
    """Check status of integrated APIs"""
    from app.core.config import settings

    apis = {
        "hibp": bool(settings.HIBP_API_KEY),
        "dehashed": bool(settings.DEHASHED_API_KEY),
        "hunter": bool(settings.HUNTER_API_KEY),
        "deepseek": bool(settings.DEEPSEEK_API_KEY),
    }

    return {
        "apis": apis,
        "all_configured": all(apis.values()),
        "minimal_configured": apis["deepseek"]  # At minimum need AI
    }


# === PDF REPORT ===

@router.post("/report/pdf")
async def generate_pdf_report(request: FullAuditRequest):
    """
    Run full audit and generate downloadable PDF report.
    """
    try:
        # First run the full audit
        audit_id = str(uuid.uuid4())[:8]
        email = request.email

        breach_result = await osint_service.check_hibp_breaches(email)
        password_exposure = await osint_service.check_dehashed(email)
        osint_result = await osint_service.full_osint_check(email)

        security_score = scoring_service.calculate_score(
            breach_result=breach_result,
            password_exposure=password_exposure,
            osint_result=osint_result
        )

        recommendations = scoring_service.get_recommendations(security_score, breach_result)

        audit_data = {
            "email": email,
            "security_score": security_score.model_dump(),
            "breach_check": breach_result.model_dump() if breach_result else None,
        }

        ai_analysis = await deepseek_service.analyze_audit(audit_data)

        audit_result = AuditResult(
            id=audit_id,
            audit_type=AuditType.EMAIL,
            query_value=email,
            email=email,
            timestamp=datetime.now(),
            security_score=security_score,
            breach_check=breach_result,
            password_exposure=password_exposure,
            osint_result=osint_result,
            ai_analysis=ai_analysis,
            recommendations=recommendations
        )

        # Generate PDF
        pdf_bytes = pdf_service.generate_report(audit_result)

        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=FK94_Security_Report_{audit_id}.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === STRIPE PAYMENTS ===

from fastapi import Request
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    user_email: str
    user_id: str
    success_url: str = "http://localhost:3000/dashboard?success=true"
    cancel_url: str = "http://localhost:3000/pricing?cancelled=true"


class PortalRequest(BaseModel):
    customer_id: str
    return_url: str = "http://localhost:3000/dashboard"


@router.post("/stripe/create-checkout")
async def create_checkout_session(request: CheckoutRequest):
    """Create Stripe checkout session for Pro subscription"""
    from app.services.stripe_service import stripe_service

    result = await stripe_service.create_checkout_session(
        user_email=request.user_email,
        user_id=request.user_id,
        success_url=request.success_url,
        cancel_url=request.cancel_url
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/stripe/create-portal")
async def create_portal_session(request: PortalRequest):
    """Create Stripe customer portal session for managing subscription"""
    from app.services.stripe_service import stripe_service

    result = await stripe_service.create_portal_session(
        customer_id=request.customer_id,
        return_url=request.return_url
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    from app.services.stripe_service import stripe_service

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    result = await stripe_service.handle_webhook(payload, sig_header)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/stripe/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    from app.core.config import settings

    return {
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY
    }
