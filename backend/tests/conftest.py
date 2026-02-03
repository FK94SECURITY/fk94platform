"""
FK94 Security Platform - Shared Test Fixtures
"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Set test environment variables BEFORE importing app modules
os.environ.setdefault("HIBP_API_KEY", "test-hibp-key")
os.environ.setdefault("DEHASHED_API_KEY", "test-dehashed-key")
os.environ.setdefault("DEHASHED_EMAIL", "test@test.com")
os.environ.setdefault("HUNTER_API_KEY", "test-hunter-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake123")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test123")
os.environ.setdefault("AI_API_KEY", "test-ai-key")
os.environ.setdefault("ENABLE_JOB_WORKER", "false")

from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import (
    BreachCheckResult, BreachInfo, PasswordExposure,
    OSINTResult, RiskLevel, SecurityScore
)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_breach_result_clean():
    """No breaches found."""
    return BreachCheckResult(
        email="safe@example.com",
        breached=False,
        breach_count=0,
        breaches=[],
        risk_level=RiskLevel.SAFE,
    )


@pytest.fixture
def sample_breach_result_minor():
    """1 breach, no passwords."""
    return BreachCheckResult(
        email="minor@example.com",
        breached=True,
        breach_count=1,
        breaches=[
            BreachInfo(name="SomeService", date="2022-01-01", data_types=["Emails"], description="Minor breach")
        ],
        risk_level=RiskLevel.LOW,
    )


@pytest.fixture
def sample_breach_result_critical():
    """Multiple breaches with passwords and financial data."""
    return BreachCheckResult(
        email="critical@example.com",
        breached=True,
        breach_count=5,
        breaches=[
            BreachInfo(name="MegaBreach", date="2023-06-01", data_types=["Passwords", "Emails"], description="Big one"),
            BreachInfo(name="FinanceLeak", date="2023-03-01", data_types=["Credit cards", "Emails"], description="Financial"),
            BreachInfo(name="SocialHack", date="2022-11-01", data_types=["Passwords", "Names"], description="Social"),
            BreachInfo(name="OldBreach", date="2020-01-01", data_types=["Emails"], description="Old"),
            BreachInfo(name="AnotherOne", date="2021-06-01", data_types=["Emails", "Names"], description="Another"),
        ],
        risk_level=RiskLevel.CRITICAL,
    )


@pytest.fixture
def sample_password_clean():
    """Password not found in breaches."""
    return PasswordExposure(found=False, count=0, sources=[])


@pytest.fixture
def sample_password_exposed():
    """Password found many times."""
    return PasswordExposure(found=True, count=150, sources=["HIBP Password Database"])


@pytest.fixture
def sample_osint_clean():
    """Minimal OSINT exposure."""
    return OSINTResult(email="clean@example.com")


@pytest.fixture
def sample_osint_exposed():
    """High OSINT exposure."""
    return OSINTResult(
        email="exposed@example.com",
        domains_found=["example.com", "corp.com"],
        social_profiles=["https://gravatar.com/abc", "https://github.com/user", "https://twitter.com/user"],
        data_brokers=["spokeo.com", "whitepages.com", "radaris.com"],
        public_records=["Organization: ACME Corp", "Position: Engineer", "Public emails found on domain: 5"],
    )
