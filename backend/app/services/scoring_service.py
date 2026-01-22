"""
FK94 Security Platform - Security Scoring Service
Calculates overall security score from audit results
"""
from app.models.schemas import (
    SecurityScore, RiskLevel, BreachCheckResult,
    PasswordExposure, OSINTResult
)


class ScoringService:
    """Calculate security scores from audit data"""

    # Scoring weights (total = 100)
    WEIGHTS = {
        "breaches": 35,      # Email in data breaches
        "passwords": 30,     # Password exposure
        "osint": 20,         # Public data exposure
        "configuration": 15  # Device/account config (future)
    }

    def calculate_score(
        self,
        breach_result: BreachCheckResult = None,
        password_exposure: PasswordExposure = None,
        osint_result: OSINTResult = None
    ) -> SecurityScore:
        """Calculate overall security score from audit components"""

        breakdown = {}
        issues = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        # === Breach Score ===
        breach_score = self.WEIGHTS["breaches"]
        if breach_result and breach_result.breached:
            count = breach_result.breach_count
            if count >= 10:
                breach_score = 0
                issues["critical"] += 1
            elif count >= 5:
                breach_score = 5
                issues["high"] += 1
            elif count >= 3:
                breach_score = 15
                issues["high"] += 1
            elif count >= 1:
                breach_score = 25
                issues["medium"] += 1

            # Extra penalty for password breaches
            has_passwords = any("Passwords" in b.data_types for b in breach_result.breaches)
            if has_passwords:
                breach_score = max(0, breach_score - 10)
                issues["critical"] += 1

        breakdown["breaches"] = breach_score

        # === Password Exposure Score ===
        password_score = self.WEIGHTS["passwords"]
        if password_exposure and password_exposure.found:
            count = password_exposure.count
            if count >= 100:
                password_score = 0
                issues["critical"] += 1
            elif count >= 10:
                password_score = 5
                issues["critical"] += 1
            elif count >= 1:
                password_score = 15
                issues["high"] += 1

        breakdown["passwords"] = password_score

        # === OSINT Score ===
        osint_score = self.WEIGHTS["osint"]
        if osint_result:
            exposure_count = (
                len(osint_result.domains_found) +
                len(osint_result.social_profiles) +
                len(osint_result.data_brokers)
            )
            if exposure_count >= 10:
                osint_score = 5
                issues["high"] += 1
            elif exposure_count >= 5:
                osint_score = 10
                issues["medium"] += 1
            elif exposure_count >= 1:
                osint_score = 15
                issues["low"] += 1

        breakdown["osint"] = osint_score

        # === Configuration Score (placeholder for future) ===
        config_score = self.WEIGHTS["configuration"]  # Full score by default
        breakdown["configuration"] = config_score

        # === Calculate Total ===
        total_score = sum(breakdown.values())

        # Determine risk level
        if total_score >= 80:
            risk_level = RiskLevel.SAFE
        elif total_score >= 60:
            risk_level = RiskLevel.LOW
        elif total_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif total_score >= 20:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        return SecurityScore(
            score=total_score,
            risk_level=risk_level,
            breakdown=breakdown,
            issues_critical=issues["critical"],
            issues_high=issues["high"],
            issues_medium=issues["medium"],
            issues_low=issues["low"]
        )

    def get_recommendations(self, score: SecurityScore, breach_result: BreachCheckResult = None) -> list[str]:
        """Generate prioritized recommendations based on score"""

        recommendations = []

        # Critical issues first
        if score.issues_critical > 0:
            if breach_result and any("Passwords" in b.data_types for b in breach_result.breaches):
                recommendations.append(
                    "🔴 URGENTE: Tus contraseñas fueron filtradas. Cambialas TODAS inmediatamente, "
                    "empezando por email y banco."
                )
            recommendations.append(
                "🔴 CRÍTICO: Activá autenticación de 2 factores (2FA) en todas tus cuentas importantes."
            )

        # High priority
        if score.issues_high > 0:
            recommendations.append(
                "🟠 ALTO: Usá un password manager (Bitwarden es gratis) para generar contraseñas únicas."
            )
            if breach_result and breach_result.breach_count >= 3:
                recommendations.append(
                    "🟠 ALTO: Tu email está en múltiples breaches. Considerá usar un email alias "
                    "para registros online (SimpleLogin, Firefox Relay)."
                )

        # Medium priority
        if score.issues_medium > 0:
            recommendations.append(
                "🟡 MEDIO: Revisá qué permisos tienen las apps conectadas a tus cuentas de Google/Facebook."
            )
            recommendations.append(
                "🟡 MEDIO: Configurá alertas de seguridad en tu email y banco."
            )

        # General recommendations
        if score.score < 80:
            recommendations.append(
                "🟢 TIP: Usá un email diferente para cuentas importantes (banco, trabajo) "
                "vs cuentas de redes sociales y suscripciones."
            )

        return recommendations


# Singleton instance
scoring_service = ScoringService()
