# ============================================================================
# RISK_ENGINE.PY - Haupt-Risiko-Analyse-Engine
# ============================================================================
#
# Was macht die Risk Engine?
# - Kombiniert alle 6 Heuristiken
# - Berechnet gewichteten Gesamt-Score
# - Generiert Risiko-Level (low/medium/high)
# - Erstellt Liste von Warnungen/Flags
#
# Gewichtung der Heuristiken:
# - Scam-Interaktion: 30% (stärkster Indikator!)
# - Wallet-Alter: 20%
# - Token-Konzentration: 15%
# - TX-Volumen: 15%
# - Mixer-Nutzung: 10%
# - Inflow/Outflow: 10%
# ============================================================================

from typing import Dict, List
import logging

from ..blockchain.data_models import WalletData, RiskScore
from .heuristics import calculate_all_heuristics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# GEWICHTUNGS-KONFIGURATION
# ============================================================================
DEFAULT_WEIGHTS = {
    'wallet_age': 0.20,          # 20% - Alter ist wichtig
    'transaction_volume': 0.15,   # 15% - Aktivität zählt
    'token_concentration': 0.15,  # 15% - Diversifikation wichtig
    'scam_interaction': 0.30,     # 30% - STÄRKSTER Indikator!
    'mixer_usage': 0.10,          # 10% - Privacy vs. Risiko
    'inflow_outflow': 0.10,       # 10% - Verhalten-Muster
}

# Validiere dass Gewichte = 100% (1.0)
assert abs(sum(DEFAULT_WEIGHTS.values()) - 1.0) < 0.01, "Gewichte müssen 100% ergeben!"


# ============================================================================
# RISK ENGINE KLASSE
# ============================================================================
class RiskEngine:
    """
    Haupt-Engine für Risiko-Analyse.

    Verwendung:
        engine = RiskEngine()
        risk_score = engine.analyze(wallet_data)
    """

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialisiert Risk Engine.

        Args:
            weights: Custom Gewichtung (optional)
                    Falls None, werden DEFAULT_WEIGHTS verwendet
        """
        self.weights = weights or DEFAULT_WEIGHTS

        # Validiere Gewichte
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"⚠️  Gewichte ergeben {total_weight*100}% statt 100%!")

    # ========================================================================
    # HAUPT-ANALYSE
    # ========================================================================
    def analyze(self, wallet_data: WalletData) -> RiskScore:
        """
        Führt vollständige Risiko-Analyse durch.

        Schritte:
        1. Berechne alle Heuristiken
        2. Berechne gewichteten Gesamt-Score
        3. Bestimme Risiko-Level
        4. Sammle Flags/Warnungen
        5. Erstelle RiskScore-Objekt

        Args:
            wallet_data: WalletData-Objekt

        Returns:
            RiskScore-Objekt mit allen Ergebnissen
        """
        logger.info(f"\n🎯 STARTE RISIKO-ANALYSE für {wallet_data.address}")
        logger.info("=" * 70)

        # Schritt 1: Berechne alle Heuristiken
        heuristic_results = calculate_all_heuristics(wallet_data)

        # Schritt 2: Berechne gewichteten Gesamt-Score
        total_score = self._calculate_weighted_score(heuristic_results)

        # Schritt 3: Bestimme Risiko-Level
        risk_level = self._determine_risk_level(total_score)

        # Schritt 4: Sammle Flags/Warnungen
        flags = self._generate_flags(heuristic_results, total_score)

        # Schritt 5: Erstelle RiskScore-Objekt
        risk_score = RiskScore(
            total_score=round(total_score, 2),
            wallet_age_score=round(heuristic_results['wallet_age']['score'], 2),
            transaction_volume_score=round(heuristic_results['transaction_volume']['score'], 2),
            token_concentration_score=round(heuristic_results['token_concentration']['score'], 2),
            scam_interaction_score=round(heuristic_results['scam_interaction']['score'], 2),
            mixer_usage_score=round(heuristic_results['mixer_usage']['score'], 2),
            inflow_outflow_score=round(heuristic_results['inflow_outflow']['score'], 2),
            risk_level=risk_level,
            flags=flags
        )

        logger.info("=" * 70)
        logger.info(f"✅ ANALYSE ABGESCHLOSSEN")
        logger.info(f"   Gesamt-Score: {total_score:.2f}/100")
        logger.info(f"   Risiko-Level: {risk_level.upper()}")
        logger.info(f"   Flags: {len(flags)}")
        logger.info("")

        return risk_score

    # ========================================================================
    # GEWICHTETER SCORE
    # ========================================================================
    def _calculate_weighted_score(self, heuristic_results: Dict) -> float:
        """
        Berechnet gewichteten Gesamt-Score.

        Formel:
        Total = (Score1 * Weight1) + (Score2 * Weight2) + ... + (Score6 * Weight6)

        Beispiel:
        - Wallet-Alter: 20 * 0.20 = 4.0
        - TX-Volumen: 30 * 0.15 = 4.5
        - Token-Konz.: 60 * 0.15 = 9.0
        - Scam-Inter.: 80 * 0.30 = 24.0  <-- Größter Einfluss!
        - Mixer: 0 * 0.10 = 0.0
        - Inflow/Out: 20 * 0.10 = 2.0
        Total = 43.5

        Args:
            heuristic_results: Dictionary mit allen Heuristik-Ergebnissen

        Returns:
            Gewichteter Gesamt-Score (0-100)
        """
        total = 0.0

        logger.info("📊 Gewichtete Scores:")

        for heuristic_name, weight in self.weights.items():
            score = heuristic_results[heuristic_name]['score']
            weighted = score * weight

            total += weighted

            logger.info(f"   {heuristic_name:25} "
                       f"Score: {score:5.1f} × {weight:.2f} = {weighted:5.2f}")

        logger.info(f"   {'─' * 60}")
        logger.info(f"   {'GESAMT':25} {total:5.2f}/100")
        logger.info("")

        return total

    # ========================================================================
    # RISIKO-LEVEL BESTIMMUNG
    # ========================================================================
    def _determine_risk_level(self, score: float) -> str:
        """
        Bestimmt Risiko-Level basierend auf Score.

        Kategorien:
        - 0-30: low (niedriges Risiko)
        - 31-60: medium (mittleres Risiko)
        - 61-100: high (hohes Risiko)

        Args:
            score: Gesamt-Score

        Returns:
            "low", "medium", oder "high"
        """
        if score <= 30:
            return "low"
        elif score <= 60:
            return "medium"
        else:
            return "high"

    # ========================================================================
    # FLAGS/WARNUNGEN GENERIEREN
    # ========================================================================
    def _generate_flags(self, heuristic_results: Dict, total_score: float) -> List[str]:
        """
        Generiert Liste von Warnungen basierend auf Heuristiken.

        Flags werden erstellt wenn:
        - Einzelne Heuristik > 60 (hohes Risiko)
        - Scam-Interaktion > 40
        - Mixer-Nutzung > 0
        - Gesamt-Score > 60

        Args:
            heuristic_results: Heuristik-Ergebnisse
            total_score: Gesamt-Score

        Returns:
            Liste von Warnung-Strings
        """
        flags = []

        # Prüfe jede Heuristik
        for heuristic_name, result in heuristic_results.items():
            score = result['score']
            explanation = result['explanation']

            # Kritisch: Score > 70
            if score > 70:
                flags.append(f"🚨 KRITISCH - {heuristic_name}: {explanation}")

            # Warnung: Score > 50
            elif score > 50:
                flags.append(f"⚠️  WARNUNG - {heuristic_name}: {explanation}")

            # Info: Score > 30
            elif score > 30:
                flags.append(f"ℹ️  INFO - {heuristic_name}: {explanation}")

        # Spezielle Flags für Scam-Interaktion (selbst bei niedrigem Score)
        scam_score = heuristic_results['scam_interaction']['score']
        if scam_score > 0:
            flags.append(f"🔴 Scam-Kontakt erkannt - Score: {scam_score}")

        # Spezielle Flags für Mixer-Nutzung
        mixer_score = heuristic_results['mixer_usage']['score']
        if mixer_score > 0:
            flags.append(f"🌪️  Privacy-Mixer verwendet - Score: {mixer_score}")

        # Gesamt-Risiko Flag
        if total_score > 70:
            flags.append(f"🚨 HOHES GESAMT-RISIKO - Score: {total_score:.1f}/100")
        elif total_score > 40:
            flags.append(f"⚠️  ERHÖHTES GESAMT-RISIKO - Score: {total_score:.1f}/100")

        logger.info("🏴 Generierte Flags:")
        for flag in flags:
            logger.info(f"   {flag}")
        logger.info("")

        return flags


# ============================================================================
# CONVENIENCE-FUNKTION
# ============================================================================
def analyze_wallet_risk(wallet_data: WalletData, weights: Dict[str, float] = None) -> RiskScore:
    """
    Convenience-Funktion für schnelle Analyse.

    Args:
        wallet_data: WalletData-Objekt
        weights: Custom Gewichtung (optional)

    Returns:
        RiskScore-Objekt
    """
    engine = RiskEngine(weights=weights)
    return engine.analyze(wallet_data)


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("RISK ENGINE - Beispiel")
    print("=" * 70)
    print("\nDiese Engine kombiniert alle 6 Heuristiken zu einem Gesamt-Score.")
    print("\nGewichtung:")
    for name, weight in DEFAULT_WEIGHTS.items():
        print(f"  • {name:25} {weight * 100:>5.1f}%")

    print("\nScore-Bereiche:")
    print("  • 0-30:   Niedriges Risiko (low)")
    print("  • 31-60:  Mittleres Risiko (medium)")
    print("  • 61-100: Hohes Risiko (high)")
    print("\n" + "=" * 70)
