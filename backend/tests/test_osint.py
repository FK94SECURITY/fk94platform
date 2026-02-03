"""
FK94 Security Platform - OSINT Service Tests
Tests with mocked external API calls (HIBP, Dehashed, Hunter).
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.osint_service import OSINTService
from app.models.schemas import RiskLevel, BreachInfo


@pytest.fixture
def osint():
    svc = OSINTService()
    svc.hibp_key = "test-key"
    svc.dehashed_key = "test-key"
    svc.dehashed_email = "test@test.com"
    svc.hunter_key = "test-key"
    return svc


# === HIBP Breach Check ===

@pytest.mark.asyncio
async def test_hibp_no_breaches(osint):
    """Email not found in any breaches returns safe."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        # 404 is handled before raise_for_status
        mock_response.raise_for_status = MagicMock()  # won't be called for 404
        result = await osint.check_hibp_breaches("safe@example.com")

    assert result.breached is False
    assert result.breach_count == 0
    assert result.risk_level == RiskLevel.SAFE


@pytest.mark.asyncio
async def test_hibp_with_breaches(osint):
    """Email found in breaches returns correct data."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = [
        {
            "Name": "Adobe",
            "BreachDate": "2013-10-04",
            "DataClasses": ["Emails", "Passwords"],
            "Description": "Adobe breach"
        },
        {
            "Name": "LinkedIn",
            "BreachDate": "2012-05-05",
            "DataClasses": ["Emails"],
            "Description": "LinkedIn breach"
        }
    ]

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        result = await osint.check_hibp_breaches("hacked@example.com")

    assert result.breached is True
    assert result.breach_count == 2
    assert result.breaches[0].name == "Adobe"
    assert "Passwords" in result.breaches[0].data_types


@pytest.mark.asyncio
async def test_hibp_no_api_key_falls_back():
    """Without API key, falls back to free check."""
    svc = OSINTService()
    svc.hibp_key = ""
    result = await svc.check_hibp_breaches("test@example.com")
    assert result.breached is False
    assert result.risk_level == RiskLevel.LOW


# === Password Check ===

@pytest.mark.asyncio
async def test_password_pwned_found(osint):
    """Password found in HIBP password database."""
    # SHA1 of "password" = 5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.text = "1E4C9B93F3F0682250B6CF8331B7EE68FD8:3861493\nOTHERHASH:123"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        result = await osint.check_password_pwned("password")

    assert result.found is True
    assert result.count == 3861493


@pytest.mark.asyncio
async def test_password_pwned_not_found(osint):
    """Password not in HIBP database."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.text = "AAAAAAA:1\nBBBBBBB:2"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        result = await osint.check_password_pwned("my-super-unique-password-12345")

    assert result.found is False
    assert result.count == 0


# === Dehashed ===

@pytest.mark.asyncio
async def test_dehashed_found(osint):
    """Email found in Dehashed."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "entries": [
            {"database_name": "Collection1"},
            {"database_name": "Collection2"},
            {"database_name": "Collection1"},  # duplicate
        ]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        result = await osint.check_dehashed("test@example.com")

    assert result is not None
    assert result.found is True
    assert result.count == 3
    assert "Collection1" in result.sources
    assert "Collection2" in result.sources


@pytest.mark.asyncio
async def test_dehashed_no_key():
    """Without API key, returns None."""
    svc = OSINTService()
    svc.dehashed_key = ""
    result = await svc.check_dehashed("test@example.com")
    assert result is None


# === Hunter.io ===

@pytest.mark.asyncio
async def test_hunter_email_verify(osint):
    """Hunter.io email verification returns data."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "result": "deliverable",
            "score": 95,
            "organization": "ACME Corp",
            "sources": [{"domain": "acme.com", "uri": "https://acme.com/about"}]
        }
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        result = await osint.check_hunter("user@acme.com")

    assert result is not None
    assert result["organization"] == "ACME Corp"


@pytest.mark.asyncio
async def test_hunter_no_key():
    """Without API key, returns None."""
    svc = OSINTService()
    svc.hunter_key = ""
    result = await svc.check_hunter("test@example.com")
    assert result is None


# === Risk Calculation ===

def test_risk_no_breaches(osint):
    assert osint._calculate_breach_risk([]) == RiskLevel.SAFE


def test_risk_one_breach_no_passwords(osint):
    breaches = [BreachInfo(name="Test", data_types=["Emails"])]
    assert osint._calculate_breach_risk(breaches) == RiskLevel.LOW


def test_risk_with_passwords(osint):
    breaches = [BreachInfo(name="Test", data_types=["Passwords", "Emails"])]
    assert osint._calculate_breach_risk(breaches) == RiskLevel.HIGH


def test_risk_with_financial(osint):
    breaches = [BreachInfo(name="Test", data_types=["Credit cards", "Emails"])]
    assert osint._calculate_breach_risk(breaches) == RiskLevel.CRITICAL


def test_risk_many_breaches(osint):
    breaches = [BreachInfo(name=f"B{i}", data_types=["Emails"]) for i in range(5)]
    assert osint._calculate_breach_risk(breaches) == RiskLevel.HIGH


def test_risk_passwords_plus_many(osint):
    breaches = [
        BreachInfo(name="B1", data_types=["Passwords"]),
        BreachInfo(name="B2", data_types=["Emails"]),
        BreachInfo(name="B3", data_types=["Names"]),
    ]
    assert osint._calculate_breach_risk(breaches) == RiskLevel.CRITICAL


# === Helpers ===

def test_compact_list(osint):
    result = osint._compact_list(["a", "b", "a", None, "c", "b"])
    assert result == ["a", "b", "c"]


def test_normalize_domain(osint):
    assert osint._normalize_domain("https://example.com/page") == "example.com"
    assert osint._normalize_domain("http://test.org") == "test.org"
    assert osint._normalize_domain("") == ""


def test_broker_domains(osint):
    brokers = osint._broker_domains()
    assert "spokeo.com" in brokers
    assert "whitepages.com" in brokers
    assert len(brokers) == 10
