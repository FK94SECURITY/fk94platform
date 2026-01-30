"""
FK94 Security Platform - Data Models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"


class AuditType(str, Enum):
    EMAIL = "email"
    USERNAME = "username"
    PHONE = "phone"
    DOMAIN = "domain"
    NAME = "name"
    IP = "ip"
    WALLET = "wallet"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# === Request Models ===

class EmailCheckRequest(BaseModel):
    email: EmailStr


class PasswordCheckRequest(BaseModel):
    password: str


class UsernameCheckRequest(BaseModel):
    username: str


class PhoneCheckRequest(BaseModel):
    phone: str
    country_code: str = "AR"  # Default Argentina


class DomainCheckRequest(BaseModel):
    domain: str


class NameCheckRequest(BaseModel):
    full_name: str
    location: Optional[str] = None


class IPCheckRequest(BaseModel):
    ip_address: str


class WalletCheckRequest(BaseModel):
    address: str
    chain: str = "ethereum"  # ethereum, bitcoin, solana, etc.


class FullAuditRequest(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # Optional password to check if leaked
    check_breaches: bool = True
    check_osint: bool = True
    check_dark_web: bool = False


class MultiAuditRequest(BaseModel):
    audit_type: AuditType
    value: str
    extra_data: Optional[dict] = None


class FullAuditJobRequest(FullAuditRequest):
    run_at: Optional[datetime] = None


class MultiAuditJobRequest(MultiAuditRequest):
    run_at: Optional[datetime] = None


class AIAnalysisRequest(BaseModel):
    query: str
    context: Optional[dict] = None


# === Response Models ===

class BreachInfo(BaseModel):
    name: str
    date: Optional[str] = None
    data_types: list[str] = []
    description: Optional[str] = None


class BreachCheckResult(BaseModel):
    email: str
    breached: bool
    breach_count: int
    breaches: list[BreachInfo]
    risk_level: RiskLevel


class PasswordExposure(BaseModel):
    found: bool
    count: int
    sources: list[str] = []


class OSINTResult(BaseModel):
    email: str
    domains_found: list[str] = []
    social_profiles: list[str] = []
    data_brokers: list[str] = []
    public_records: list[str] = []


class UsernameResult(BaseModel):
    username: str
    platforms_found: List[str] = []
    platforms_checked: int = 0
    profile_urls: List[str] = []
    risk_level: RiskLevel


class PhoneResult(BaseModel):
    phone: str
    carrier: Optional[str] = None
    line_type: Optional[str] = None
    location: Optional[str] = None
    breaches_found: int = 0
    spam_reports: int = 0
    risk_level: RiskLevel
    # Truecaller data
    owner_name: Optional[str] = None
    tags: List[str] = []
    email: Optional[str] = None
    error: Optional[str] = None


class DomainResult(BaseModel):
    domain: str
    ssl_valid: bool = False
    ssl_expiry: Optional[str] = None
    dns_records: dict = {}
    spf_configured: bool = False
    dmarc_configured: bool = False
    dkim_configured: bool = False
    open_ports: List[int] = []
    vulnerabilities: List[str] = []
    risk_level: RiskLevel


class NameResult(BaseModel):
    full_name: str
    possible_profiles: List[dict] = []
    public_records: List[str] = []
    news_mentions: List[str] = []
    risk_level: RiskLevel


class IPResult(BaseModel):
    ip_address: str
    location: Optional[str] = None
    isp: Optional[str] = None
    is_vpn: bool = False
    is_proxy: bool = False
    is_tor: bool = False
    blacklisted: bool = False
    blacklist_sources: List[str] = []
    abuse_reports: int = 0
    risk_level: RiskLevel


class ExchangeInteraction(BaseModel):
    exchange: str
    address: str
    direction: str  # "sent" or "received"
    tx_hash: str
    value: Optional[str] = None
    timestamp: Optional[str] = None


class WalletResult(BaseModel):
    address: str
    chain: str
    balance: Optional[str] = None
    transaction_count: Optional[int] = None
    linked_addresses: List[str] = []
    labeled: bool = False
    label: Optional[str] = None
    sanctions_check: bool = False
    risk_level: RiskLevel
    # Deep scan fields
    deep_scan: bool = False
    exchange_interactions: List[ExchangeInteraction] = []
    exchanges_detected: List[str] = []
    is_traceable: bool = False
    traceability_score: int = 0
    traceability_details: List[str] = []
    mixer_interactions: List[str] = []
    used_mixer: bool = False
    ofac_sanctioned: bool = False
    first_tx_date: Optional[str] = None
    last_tx_date: Optional[str] = None
    unique_counterparties: int = 0
    scan_warnings: List[str] = []


class SecurityScore(BaseModel):
    score: int  # 0-100
    risk_level: RiskLevel
    breakdown: dict  # {"breaches": 20, "passwords": 15, "osint": 30, ...}
    issues_critical: int
    issues_high: int
    issues_medium: int
    issues_low: int


class AuditResult(BaseModel):
    id: str
    audit_type: AuditType = AuditType.EMAIL
    query_value: str  # The email, username, phone, etc that was audited
    email: Optional[str] = None  # Keep for backwards compatibility
    timestamp: datetime
    security_score: SecurityScore
    breach_check: Optional[BreachCheckResult] = None
    password_exposure: Optional[PasswordExposure] = None
    osint_result: Optional[OSINTResult] = None
    username_result: Optional[UsernameResult] = None
    phone_result: Optional[PhoneResult] = None
    domain_result: Optional[DomainResult] = None
    name_result: Optional[NameResult] = None
    ip_result: Optional[IPResult] = None
    wallet_result: Optional[WalletResult] = None
    ai_analysis: Optional[str] = None
    recommendations: list[str] = []


class AIResponse(BaseModel):
    response: str
    recommendations: list[str] = []


# === Automation ===

class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus
    job_type: str


class JobInfo(BaseModel):
    job_id: str
    status: JobStatus
    job_type: str
    run_at: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None


# === API Status ===

class APIStatus(BaseModel):
    name: str
    available: bool
    message: Optional[str] = None
