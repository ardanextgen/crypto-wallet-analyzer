# ============================================================================
# REPORT_GENERATOR.PY - AI-gesteuerte Report-Generierung
# ============================================================================
#
# Was macht dieses Modul?
# - Nutzt Claude AI (Anthropic API) für Report-Generierung
# - Konvertiert technische Scores in verständliche Erklärungen
# - Gibt Empfehlungen basierend auf Risiko-Profil
#
# Warum AI-generierte Reports?
# - Flexibel: Passt sich an verschiedene Risiko-Profile an
# - Verständlich: Erklärt in natürlicher Sprache
# - Kontextbewusst: Berücksichtigt alle Details
#
# API-Kosten (Claude Haiku):
# - ~$0.003 pro Report (sehr günstig!)
# - Input: ~500 Tokens
# - Output: ~300 Tokens
# ============================================================================

import os
from typing import Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
import logging
import json

from ..blockchain.data_models import WalletData, RiskScore, AIReport

# Lade Umgebungsvariablen
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# AI REPORT GENERATOR KLASSE
# ============================================================================
class AIReportGenerator:
    """
    Generiert AI-basierte Wallet-Analyse-Reports.

    Verwendet Claude API für natürlichsprachige Reports.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialisiert AI Report Generator.

        Args:
            api_key: Anthropic API Key (optional, aus .env)
            model: Claude-Modell (optional, default: haiku für Kosten-Effizienz)
        """
        # API Key aus .env oder Parameter
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            logger.error("❌ Kein Anthropic API Key gefunden!")
            logger.error("   Setze ANTHROPIC_API_KEY in .env Datei")
            raise ValueError("Anthropic API Key fehlt")

        # Modell-Auswahl
        # Haiku = schnell & günstig (empfohlen für Reports)
        # Sonnet = bessere Qualität, teurer
        # Opus = beste Qualität, sehr teuer
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")

        # Anthropic Client erstellen
        self.client = Anthropic(api_key=self.api_key)

        logger.info(f"✅ AI Report Generator initialisiert (Modell: {self.model})")

    # ========================================================================
    # REPORT GENERIERUNG
    # ========================================================================
    def generate_report(
        self,
        wallet_data: WalletData,
        risk_score: RiskScore
    ) -> AIReport:
        """
        Generiert AI-basierten Analyse-Report.

        Args:
            wallet_data: WalletData-Objekt
            risk_score: RiskScore-Objekt

        Returns:
            AIReport-Objekt
        """
        logger.info("🤖 Generiere AI-Report...")

        # Schritt 1: Bereite Daten für Prompt auf
        prompt_data = self._prepare_prompt_data(wallet_data, risk_score)

        # Schritt 2: Erstelle Prompt
        prompt = self._build_prompt(prompt_data)

        # Schritt 3: Rufe Claude API auf
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,  # Max. Länge der Antwort
                temperature=0.7,  # Kreativität (0.0-1.0)
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extrahiere Text-Antwort
            # response.content ist eine Liste von Content-Blocks
            raw_response = response.content[0].text

            logger.info("✅ AI-Report generiert")
            logger.debug(f"Token-Nutzung: Input={response.usage.input_tokens}, "
                        f"Output={response.usage.output_tokens}")

        except Exception as e:
            logger.error(f"❌ Fehler bei AI-Report-Generierung: {e}")
            # Fallback: Erstelle einfachen Report ohne AI
            return self._create_fallback_report(wallet_data, risk_score)

        # Schritt 4: Parse AI-Response
        ai_report = self._parse_response(raw_response, risk_score)

        return ai_report

    # ========================================================================
    # PROMPT VORBEREITUNG
    # ========================================================================
    def _prepare_prompt_data(
        self,
        wallet_data: WalletData,
        risk_score: RiskScore
    ) -> Dict:
        """
        Bereitet Daten für Prompt auf.

        Konvertiert WalletData und RiskScore in übersichtliches Dict.

        Args:
            wallet_data: WalletData-Objekt
            risk_score: RiskScore-Objekt

        Returns:
            Dictionary mit formatierten Daten
        """
        return {
            'address': wallet_data.address,
            'eth_balance': wallet_data.get_eth_balance_decimal(),
            'wallet_age_days': wallet_data.get_wallet_age_days(),
            'total_transactions': wallet_data.total_transactions,
            'token_count': len(wallet_data.token_holdings),

            # Risk Scores
            'total_score': risk_score.total_score,
            'risk_level': risk_score.risk_level,
            'wallet_age_score': risk_score.wallet_age_score,
            'transaction_volume_score': risk_score.transaction_volume_score,
            'token_concentration_score': risk_score.token_concentration_score,
            'scam_interaction_score': risk_score.scam_interaction_score,
            'mixer_usage_score': risk_score.mixer_usage_score,
            'inflow_outflow_score': risk_score.inflow_outflow_score,

            # Flags
            'flags': risk_score.flags,
        }

    # ========================================================================
    # PROMPT ERSTELLEN
    # ========================================================================
    def _build_prompt(self, data: Dict) -> str:
        """
        Erstellt strukturierten Prompt für Claude.

        Args:
            data: Aufbereitete Wallet-Daten

        Returns:
            Prompt-String
        """
        prompt = f"""Du bist ein Blockchain-Sicherheitsexperte, der Krypto-Wallets auf Betrugs-Risiken analysiert.

Analysiere folgende Ethereum-Wallet und erstelle einen verständlichen Report:

═══════════════════════════════════════════════════════════════
WALLET-DATEN
═══════════════════════════════════════════════════════════════

Adresse: {data['address']}
ETH Balance: {data['eth_balance']:.4f} ETH
Wallet-Alter: {data['wallet_age_days']} Tage (~{data['wallet_age_days'] // 30} Monate)
Transaktionen: {data['total_transactions']}
Token-Holdings: {data['token_count']}

═══════════════════════════════════════════════════════════════
RISIKO-ANALYSE
═══════════════════════════════════════════════════════════════

GESAMT-SCORE: {data['total_score']:.1f}/100
RISIKO-LEVEL: {data['risk_level'].upper()}

Detail-Scores (0-100, höher = riskanter):
  • Wallet-Alter:        {data['wallet_age_score']:>5.1f}
  • Transaktionsvolumen: {data['transaction_volume_score']:>5.1f}
  • Token-Konzentration: {data['token_concentration_score']:>5.1f}
  • Scam-Interaktion:    {data['scam_interaction_score']:>5.1f}  ⚠️ WICHTIGSTER Faktor!
  • Mixer-Nutzung:       {data['mixer_usage_score']:>5.1f}
  • Ein-/Ausgangs-Muster:{data['inflow_outflow_score']:>5.1f}

Erkannte Flags:
{self._format_flags(data['flags'])}

═══════════════════════════════════════════════════════════════
AUFGABE
═══════════════════════════════════════════════════════════════

Erstelle einen Report im folgenden JSON-Format:

{{
  "summary": "1-2 Sätze Zusammenfassung des Risiko-Profils",
  "risk_assessment": "Detaillierte Einschätzung (2-3 Sätze): Was sind die Hauptrisiken? Wie vertrauenswürdig ist die Wallet?",
  "key_factors": [
    "Faktor 1: Was trägt am meisten zum Risiko bei?",
    "Faktor 2: Weitere wichtige Faktoren",
    "Faktor 3: (falls relevant)"
  ],
  "recommendations": [
    "Empfehlung 1: Was sollte der Nutzer tun/beachten?",
    "Empfehlung 2: Weitere Handlungsempfehlungen",
    "Empfehlung 3: (falls relevant)"
  ]
}}

WICHTIG:
- Sei objektiv und faktenbasiert
- Erkläre in einfacher Sprache (auch für Nicht-Experten)
- Berücksichtige ALLE Scores, nicht nur den höchsten
- Scam-Interaktion-Score ist am wichtigsten!
- Gib 2-4 Empfehlungen, die praktisch umsetzbar sind

Antworte NUR mit dem JSON-Objekt, nichts anderes."""

        return prompt

    def _format_flags(self, flags: list) -> str:
        """Formatiert Flags für Prompt"""
        if not flags:
            return "  (Keine kritischen Flags)"

        formatted = []
        for i, flag in enumerate(flags[:5], 1):  # Max 5 Flags
            formatted.append(f"  {i}. {flag}")

        return "\n".join(formatted)

    # ========================================================================
    # RESPONSE PARSING
    # ========================================================================
    def _parse_response(self, raw_response: str, risk_score: RiskScore) -> AIReport:
        """
        Parst Claude's Response zu AIReport-Objekt.

        Args:
            raw_response: Claude's Text-Antwort
            risk_score: RiskScore für Fallback

        Returns:
            AIReport-Objekt
        """
        try:
            # Versuche JSON zu parsen
            # Manchmal fügt Claude Markdown-Formatierung hinzu (```json...)
            # Entferne diese falls vorhanden
            cleaned = raw_response.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]  # Entferne ```json
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]  # Entferne ```
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]  # Entferne ```

            cleaned = cleaned.strip()

            # Parse JSON
            data = json.loads(cleaned)

            # Erstelle AIReport
            ai_report = AIReport(
                summary=data.get('summary', 'Keine Zusammenfassung verfügbar'),
                risk_assessment=data.get('risk_assessment', 'Keine Einschätzung verfügbar'),
                key_factors=data.get('key_factors', []),
                recommendations=data.get('recommendations', []),
                raw_response=raw_response
            )

            return ai_report

        except json.JSONDecodeError as e:
            logger.warning(f"⚠️  Konnte AI-Response nicht als JSON parsen: {e}")
            logger.debug(f"Raw Response: {raw_response}")

            # Fallback: Verwende raw_response direkt
            return AIReport(
                summary=raw_response[:200] + "...",
                risk_assessment=raw_response,
                key_factors=[],
                recommendations=[],
                raw_response=raw_response
            )

    # ========================================================================
    # FALLBACK REPORT (ohne AI)
    # ========================================================================
    def _create_fallback_report(
        self,
        wallet_data: WalletData,
        risk_score: RiskScore
    ) -> AIReport:
        """
        Erstellt einfachen Report ohne AI (Fallback).

        Wird verwendet wenn AI-Generierung fehlschlägt.

        Args:
            wallet_data: WalletData-Objekt
            risk_score: RiskScore-Objekt

        Returns:
            AIReport-Objekt
        """
        logger.info("ℹ️  Erstelle Fallback-Report (ohne AI)")

        # Einfache Zusammenfassung
        if risk_score.risk_level == "low":
            summary = "Diese Wallet zeigt keine signifikanten Risiko-Indikatoren."
        elif risk_score.risk_level == "medium":
            summary = "Diese Wallet zeigt einige Risiko-Indikatoren, die beachtet werden sollten."
        else:
            summary = "WARNUNG: Diese Wallet zeigt erhebliche Risiko-Indikatoren!"

        # Key Factors
        key_factors = []
        if risk_score.scam_interaction_score > 60:
            key_factors.append("Interaktionen mit bekannten Scam-Adressen erkannt")
        if risk_score.mixer_usage_score > 50:
            key_factors.append("Nutzung von Privacy-Mixern erkannt")
        if risk_score.wallet_age_score > 60:
            key_factors.append("Wallet ist sehr neu")

        # Empfehlungen
        recommendations = [
            "Überprüfen Sie alle Transaktionen sorgfältig",
            "Nutzen Sie einen Hardware-Wallet für größere Beträge",
        ]

        return AIReport(
            summary=summary,
            risk_assessment=f"Gesamt-Risiko-Score: {risk_score.total_score}/100 ({risk_score.risk_level})",
            key_factors=key_factors,
            recommendations=recommendations,
            raw_response="Fallback-Report (AI nicht verfügbar)"
        )


# ============================================================================
# CONVENIENCE-FUNKTION
# ============================================================================
def generate_ai_report(wallet_data: WalletData, risk_score: RiskScore) -> Optional[AIReport]:
    """
    Convenience-Funktion für schnelle Report-Generierung.

    Args:
        wallet_data: WalletData-Objekt
        risk_score: RiskScore-Objekt

    Returns:
        AIReport-Objekt oder None bei Fehler
    """
    try:
        generator = AIReportGenerator()
        return generator.generate_report(wallet_data, risk_score)
    except Exception as e:
        logger.error(f"Fehler bei Report-Generierung: {e}")
        return None


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AI REPORT GENERATOR")
    print("=" * 70)
    print("\nDieses Modul nutzt Claude AI um verständliche Reports zu generieren.")
    print("\nVoraussetzungen:")
    print("  • ANTHROPIC_API_KEY in .env setzen")
    print("  • ~$0.003 pro Report (Claude Haiku)")
    print("\nModell-Optionen:")
    print("  • claude-3-haiku-20240307 (schnell & günstig) ← Standard")
    print("  • claude-3-sonnet-20240229 (bessere Qualität)")
    print("  • claude-3-opus-20240229 (beste Qualität, teuer)")
    print("\n" + "=" * 70)
