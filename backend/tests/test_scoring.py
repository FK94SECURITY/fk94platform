"""
FK94 Security Platform - Scoring Service Tests
Tests the security score calculation algorithm.
"""
import pytest
from app.services.scoring_service import ScoringService
from app.models.schemas import (
    BreachCheckResult, BreachInfo, PasswordExposure,
    OSINTResult, RiskLevel, SecurityScore
)


@pytest.fixture
def scorer():
    return ScoringService()


# === Perfect Score ===

def test_perfect_score(scorer, sample_breach_result_clean, sample_password_clean, sample_osint_clean):
    """No issues = perfect 100."""
    score = scorer.calculate_score(
        breach_result=sample_breach_result_clean,
        password_exposure=sample_password_clean,
        osint_result=sample_osint_clean,
    )
    assert score.score == 100
    assert score.risk_level == RiskLevel.SAFE
    assert score.issues_critical == 0
    assert score.issues_high == 0


def test_no_data_perfect_score(scorer):
    """No data provided = full score (no negatives)."""
    score = scorer.calculate_score()
    assert score.score == 100
    assert score.risk_level == RiskLevel.SAFE


# === Breach Impact ===

def test_one_breach_minor(scorer, sample_breach_result_minor, sample_password_clean, sample_osint_clean):
    """1 breach without passwords = medium issue."""
    score = scorer.calculate_score(
        breach_result=sample_breach_result_minor,
        password_exposure=sample_password_clean,
        osint_result=sample_osint_clean,
    )
    assert score.breakdown["breaches"] == 25
    assert score.issues_medium == 1
    assert score.score == 25 + 30 + 20 + 15  # 90


def test_critical_breaches(scorer, sample_breach_result_critical, sample_password_clean, sample_osint_clean):
    """5 breaches with passwords and financial = critical."""
    score = scorer.calculate_score(
        breach_result=sample_breach_result_critical,
        password_exposure=sample_password_clean,
        osint_result=sample_osint_clean,
    )
    # 5 breaches → breach_score=5, has passwords → -10 → max(0, -5) = 0
    assert score.breakdown["breaches"] == 0
    assert score.issues_critical >= 1


def test_many_breaches_no_passwords(scorer, sample_password_clean, sample_osint_clean):
    """10+ breaches without passwords = critical score of 0 for breaches."""
    breach = BreachCheckResult(
        email="many@example.com",
        breached=True,
        breach_count=12,
        breaches=[BreachInfo(name=f"B{i}", data_types=["Emails"]) for i in range(12)],
        risk_level=RiskLevel.HIGH,
    )
    score = scorer.calculate_score(
        breach_result=breach,
        password_exposure=sample_password_clean,
        osint_result=sample_osint_clean,
    )
    assert score.breakdown["breaches"] == 0
    assert score.issues_critical >= 1


# === Password Impact ===

def test_password_exposed_heavily(scorer, sample_breach_result_clean, sample_osint_clean):
    """Password found 150+ times = critical."""
    pw = PasswordExposure(found=True, count=150, sources=["HIBP"])
    score = scorer.calculate_score(
        breach_result=sample_breach_result_clean,
        password_exposure=pw,
        osint_result=sample_osint_clean,
    )
    assert score.breakdown["passwords"] == 0
    assert score.issues_critical >= 1


def test_password_exposed_few_times(scorer, sample_breach_result_clean, sample_osint_clean):
    """Password found 5 times = high issue."""
    pw = PasswordExposure(found=True, count=5, sources=["HIBP"])
    score = scorer.calculate_score(
        breach_result=sample_breach_result_clean,
        password_exposure=pw,
        osint_result=sample_osint_clean,
    )
    assert score.breakdown["passwords"] == 15
    assert score.issues_high >= 1


# === OSINT Impact ===

def test_high_osint_exposure(scorer, sample_breach_result_clean, sample_password_clean, sample_osint_exposed):
    """High OSINT exposure lowers score."""
    score = scorer.calculate_score(
        breach_result=sample_breach_result_clean,
        password_exposure=sample_password_clean,
        osint_result=sample_osint_exposed,
    )
    # 2 domains + 3 social + 3 brokers = 8 → osint_score = 10
    assert score.breakdown["osint"] == 10
    assert score.issues_medium >= 1


def test_massive_osint_exposure(scorer, sample_breach_result_clean, sample_password_clean):
    """10+ OSINT items = high issue."""
    osint = OSINTResult(
        email="exposed@example.com",
        domains_found=["d1.com", "d2.com", "d3.com"],
        social_profiles=["p1", "p2", "p3", "p4"],
        data_brokers=["b1.com", "b2.com", "b3.com", "b4.com"],
    )
    score = scorer.calculate_score(
        breach_result=sample_breach_result_clean,
        password_exposure=sample_password_clean,
        osint_result=osint,
    )
    assert score.breakdown["osint"] == 5
    assert score.issues_high >= 1


# === Combined Worst Case ===

def test_worst_case(scorer, sample_breach_result_critical, sample_password_exposed, sample_osint_exposed):
    """Everything bad = very low score."""
    score = scorer.calculate_score(
        breach_result=sample_breach_result_critical,
        password_exposure=sample_password_exposed,
        osint_result=sample_osint_exposed,
    )
    assert score.score <= 30
    assert score.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
    assert score.issues_critical >= 2


# === Risk Level Thresholds ===

def test_risk_levels(scorer):
    """Verify risk level thresholds map correctly."""
    # score >= 80 = SAFE
    s = scorer.calculate_score()
    assert s.risk_level == RiskLevel.SAFE

    # Manually check thresholds by constructing scenarios
    # 60-79 = LOW
    pw = PasswordExposure(found=True, count=150, sources=["HIBP"])  # -30
    s = scorer.calculate_score(password_exposure=pw)
    # 100 - 30 = 70
    assert s.score == 70
    assert s.risk_level == RiskLevel.LOW


# === Recommendations ===

def test_recommendations_critical(scorer, sample_breach_result_critical):
    """Critical breaches generate urgent recommendations."""
    score = scorer.calculate_score(breach_result=sample_breach_result_critical)
    recs = scorer.get_recommendations(score, breach_result=sample_breach_result_critical)
    assert any("URGENTE" in r or "CRÍTICO" in r for r in recs)
    assert len(recs) >= 2


def test_recommendations_clean(scorer, sample_breach_result_clean):
    """Clean result generates minimal recommendations."""
    score = scorer.calculate_score(breach_result=sample_breach_result_clean)
    recs = scorer.get_recommendations(score, breach_result=sample_breach_result_clean)
    # Score is 100, no issues, no recs about urgency
    assert not any("URGENTE" in r for r in recs)


def test_recommendations_medium(scorer, sample_breach_result_minor):
    """Minor breach generates medium-priority recommendations."""
    score = scorer.calculate_score(breach_result=sample_breach_result_minor)
    recs = scorer.get_recommendations(score, breach_result=sample_breach_result_minor)
    # Score is 90 so general tip about < 80 won't fire, but medium issue rec should
    assert any("MEDIO" in r for r in recs)
