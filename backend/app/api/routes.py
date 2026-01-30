"""
FK94 Security Platform - API Routes
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
import uuid
import io

from app.models.schemas import (
    EmailCheckRequest, PasswordCheckRequest, FullAuditRequest, AIAnalysisRequest,
    UsernameCheckRequest, PhoneCheckRequest, DomainCheckRequest,
    NameCheckRequest, IPCheckRequest, WalletCheckRequest, MultiAuditRequest, AuditType,
    BreachCheckResult, PasswordExposure, AuditResult, AIResponse, SecurityScore,
    UsernameResult, PhoneResult, DomainResult, NameResult, IPResult, WalletResult,
    FullAuditJobRequest, MultiAuditJobRequest, JobCreateResponse, JobInfo, JobStatus
)
from app.core.config import settings
from app.services.osint_service import osint_service
from app.services.deepseek_service import deepseek_service
from app.services.scoring_service import scoring_service
from app.services.pdf_service import pdf_service
from app.services.audit_runner import run_full_audit, run_multi_audit
from app.services import job_store
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


@router.post("/check/password", response_model=PasswordExposure)
async def check_password_exposure(request: PasswordCheckRequest):
    """
    Check if a password has been exposed in data breaches.
    Uses k-anonymity - password is never sent over the network.
    """
    try:
        result = await osint_service.check_password_pwned(request.password)
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
        return await run_full_audit(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audit/multi", response_model=AuditResult)
async def run_multi_audit_endpoint(request: MultiAuditRequest):
    """
    Run audit on different data types: username, phone, domain, name, or IP.
    """
    try:
        return await run_multi_audit(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/automation/audit/full", response_model=JobCreateResponse)
async def enqueue_full_audit(request: FullAuditJobRequest):
    """Enqueue a full audit to run asynchronously."""
    try:
        payload = request.model_dump()
        run_at = payload.pop("run_at", None)
        job = job_store.create_job(
            db_path=settings.JOB_DB_PATH,
            job_type="full_audit",
            payload=payload,
            run_at=run_at,
        )
        return JobCreateResponse(job_id=job["id"], status=JobStatus.QUEUED, job_type="full_audit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/automation/audit/multi", response_model=JobCreateResponse)
async def enqueue_multi_audit(request: MultiAuditJobRequest):
    """Enqueue a multi audit to run asynchronously."""
    try:
        payload = request.model_dump()
        run_at = payload.pop("run_at", None)
        job = job_store.create_job(
            db_path=settings.JOB_DB_PATH,
            job_type="multi_audit",
            payload=payload,
            run_at=run_at,
        )
        return JobCreateResponse(job_id=job["id"], status=JobStatus.QUEUED, job_type="multi_audit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/automation/jobs/{job_id}", response_model=JobInfo)
async def get_job_status(job_id: str):
    """Get async job status/result."""
    job = job_store.get_job(settings.JOB_DB_PATH, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobInfo(
        job_id=job["id"],
        status=JobStatus(job["status"]),
        job_type=job["job_type"],
        run_at=job["run_at"],
        created_at=job["created_at"],
        started_at=job["started_at"],
        finished_at=job["finished_at"],
        result=job["result"],
        error=job["error"],
    )


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
        "ai": bool(settings.AI_API_KEY),
        "deepseek": bool(settings.DEEPSEEK_API_KEY),
    }

    return {
        "apis": apis,
        "all_configured": all(apis.values()),
        "minimal_configured": apis["ai"] or apis["deepseek"]  # At minimum need AI
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
