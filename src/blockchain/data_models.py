# ============================================================================
# DATA_MODELS.PY - Pydantic-Modelle für Typ-Sicherheit
# ============================================================================
#
# Was sind Pydantic Models?
# - Klassen, die Datenstrukturen mit automatischer Validierung definieren
# - Stellen sicher, dass Daten das richtige Format haben
# - Konvertieren Datentypen automatisch (z.B. String -> int)
# - Generieren hilfreiche Fehlermeldungen bei ungültigen Daten
#
# Warum verwenden wir sie?
# - Typ-Sicherheit: Weniger Bugs durch falsche Datentypen
# - Dokumentation: Code ist selbst-dokumentierend
# - FastAPI-Integration: Automatische API-Validierung
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal


# ============================================================================
# TRANSACTION MODEL - Einzelne Blockchain-Transaktion
# ============================================================================
class Transaction(BaseModel):
    """
    Repräsentiert eine einzelne Ethereum-Transaktion.

    Attribute erklärt:
    - hash: Eindeutige ID der Transaktion (z.B. "0xabc123...")
    - from_address: Absender-Wallet
    - to_address: Empfänger-Wallet oder Contract
    - value: Transferierter Betrag in Wei (1 ETH = 10^18 Wei)
    - timestamp: Wann wurde die Transaktion bestätigt?
    - block_number: In welchem Block ist die Transaktion?
    - gas_used: Wie viel Gas (Gebühr) wurde verbraucht?
    - is_error: Ist die Transaktion fehlgeschlagen? (1 = Ja, 0 = Nein)
    """

    # 'Field' ermöglicht zusätzliche Metadaten und Validierung
    hash: str = Field(..., description="Transaction Hash")
    from_address: str = Field(..., alias="from", description="Sender Address")
    to_address: Optional[str] = Field(None, alias="to", description="Receiver Address")
    value: str = Field(..., description="Value in Wei")  # String weil große Zahlen
    timestamp: int = Field(..., description="Unix Timestamp")
    block_number: int = Field(..., description="Block Number")
    gas_used: int = Field(..., description="Gas Used")
    is_error: str = Field(default="0", description="0 = Success, 1 = Failed")

    # Erlaubt Verwendung von 'from' (Python Keyword) als Feldname
    class Config:
        populate_by_name = True  # Erlaubt sowohl 'from' als auch 'from_address'

    @validator('value', pre=True)
    def convert_value_to_string(cls, v):
        """
        Konvertiert value zu String (falls es als int kommt).
        Wichtig: Ethereum-Werte können sehr groß sein (> int64)
        """
        return str(v)

    def get_value_in_eth(self) -> float:
        """
        Konvertiert Wei zu ETH für bessere Lesbarkeit.
        1 ETH = 1,000,000,000,000,000,000 Wei (10^18)
        """
        # Verwende Decimal für präzise Berechnungen
        wei_value = Decimal(self.value)
        eth_value = wei_value / Decimal(10 ** 18)
        return float(eth_value)

    def get_datetime(self) -> datetime:
        """Konvertiert Unix Timestamp zu Python datetime"""
        return datetime.fromtimestamp(self.timestamp)


# ============================================================================
# TOKEN HOLDING MODEL - ERC20 Token Balance
# ============================================================================
class TokenHolding(BaseModel):
    """
    Repräsentiert einen ERC20-Token im Wallet.

    ERC20 = Standard für Tokens auf Ethereum
    Beispiele: USDT, USDC, DAI, LINK, etc.
    """

    token_address: str = Field(..., description="Smart Contract Address des Tokens")
    token_name: str = Field(..., description="Name (z.B. 'Tether USD')")
    token_symbol: str = Field(..., description="Symbol (z.B. 'USDT')")
    balance: str = Field(..., description="Balance in kleinster Einheit")
    decimals: int = Field(default=18, description="Anzahl Dezimalstellen")

    # Optional: Wert in USD (wenn verfügbar)
    usd_value: Optional[float] = Field(None, description="Aktueller Wert in USD")

    def get_balance_decimal(self) -> float:
        """
        Konvertiert Balance zu lesbarer Dezimalzahl.
        Beispiel: 1000000 USDT (6 decimals) -> 1.0 USDT
        """
        balance_decimal = Decimal(self.balance) / Decimal(10 ** self.decimals)
        return float(balance_decimal)


# ============================================================================
# WALLET DATA MODEL - Alle Wallet-Informationen
# ============================================================================
class WalletData(BaseModel):
    """
    Zentrale Datenstruktur mit allen Wallet-Informationen.
    Wird von der Blockchain abgerufen und dann analysiert.
    """

    address: str = Field(..., description="Ethereum Wallet Address")

    # Balance
    eth_balance: str = Field(default="0", description="ETH Balance in Wei")

    # Transaktionen
    transactions: List[Transaction] = Field(
        default_factory=list,
        description="Liste aller Transaktionen"
    )

    # Token-Holdings
    token_holdings: List[TokenHolding] = Field(
        default_factory=list,
        description="Liste aller ERC20 Tokens"
    )

    # Metadaten
    first_transaction_timestamp: Optional[int] = Field(
        None,
        description="Zeitstempel der ersten Transaktion"
    )
    last_transaction_timestamp: Optional[int] = Field(
        None,
        description="Zeitstempel der letzten Transaktion"
    )
    total_transactions: int = Field(default=0, description="Gesamtanzahl Transaktionen")

    def get_eth_balance_decimal(self) -> float:
        """ETH Balance in lesbarem Format"""
        wei_value = Decimal(self.eth_balance)
        return float(wei_value / Decimal(10 ** 18))

    def get_wallet_age_days(self) -> Optional[int]:
        """
        Berechnet Wallet-Alter in Tagen.
        Returns None wenn keine Transaktionen vorhanden.
        """
        if not self.first_transaction_timestamp:
            return None

        # Differenz zwischen jetzt und erster Transaktion
        now = datetime.now().timestamp()
        age_seconds = now - self.first_transaction_timestamp
        age_days = int(age_seconds / 86400)  # 86400 Sekunden = 1 Tag
        return age_days

    def get_total_token_value_usd(self) -> float:
        """
        Summiert den USD-Wert aller Tokens.
        Nur Tokens mit verfügbarem USD-Wert werden gezählt.
        """
        total = 0.0
        for token in self.token_holdings:
            if token.usd_value:
                total += token.usd_value
        return total


# ============================================================================
# RISK SCORE MODEL - Ergebnis der Risikoanalyse
# ============================================================================
class RiskScore(BaseModel):
    """
    Resultat der Risiko-Analyse mit allen Detail-Scores.
    """

    # Gesamt-Score (0-100, höher = riskanter)
    total_score: float = Field(..., ge=0, le=100, description="Gesamt-Risiko-Score")

    # Individual Scores (jeweils 0-100)
    wallet_age_score: float = Field(..., ge=0, le=100)
    transaction_volume_score: float = Field(..., ge=0, le=100)
    token_concentration_score: float = Field(..., ge=0, le=100)
    scam_interaction_score: float = Field(..., ge=0, le=100)
    mixer_usage_score: float = Field(..., ge=0, le=100)
    inflow_outflow_score: float = Field(..., ge=0, le=100)

    # Risiko-Level (niedrig/mittel/hoch)
    risk_level: str = Field(..., description="low, medium, oder high")

    # Zusätzliche Details
    flags: List[str] = Field(
        default_factory=list,
        description="Liste von Warnungen/Flags"
    )

    @validator('risk_level')
    def validate_risk_level(cls, v):
        """Stelle sicher, dass nur gültige Risiko-Levels verwendet werden"""
        allowed = ['low', 'medium', 'high']
        if v not in allowed:
            raise ValueError(f"risk_level muss einer von {allowed} sein")
        return v

    @classmethod
    def calculate_risk_level(cls, score: float) -> str:
        """
        Berechnet Risiko-Level basierend auf Score.
        0-30 = low
        31-60 = medium
        61-100 = high
        """
        if score <= 30:
            return "low"
        elif score <= 60:
            return "medium"
        else:
            return "high"


# ============================================================================
# AI REPORT MODEL - AI-generierter Analyse-Report
# ============================================================================
class AIReport(BaseModel):
    """
    Struktur des AI-generierten Reports.
    """

    summary: str = Field(..., description="Kurze Zusammenfassung (1-2 Sätze)")

    risk_assessment: str = Field(
        ...,
        description="Detaillierte Risiko-Einschätzung"
    )

    key_factors: List[str] = Field(
        default_factory=list,
        description="Hauptfaktoren, die zum Score beitragen"
    )

    recommendations: List[str] = Field(
        default_factory=list,
        description="Empfehlungen für den Nutzer"
    )

    raw_response: Optional[str] = Field(
        None,
        description="Vollständige AI-Antwort (für Debugging)"
    )


# ============================================================================
# COMPLETE ANALYSIS MODEL - Finale Analyse mit allen Daten
# ============================================================================
class CompleteAnalysis(BaseModel):
    """
    Finale Analyse-Struktur, die alle Komponenten vereint.
    Diese wird vom API-Endpoint zurückgegeben.
    """

    # Wallet-Daten
    wallet_data: WalletData

    # Risiko-Analyse
    risk_score: RiskScore

    # AI-Report
    ai_report: Optional[AIReport] = None

    # Metadaten
    analysis_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Wann wurde die Analyse durchgeführt?"
    )

    analysis_version: str = Field(
        default="0.1.0",
        description="Version des Analyse-Algorithmus"
    )

    class Config:
        # Beispiel-Daten für API-Dokumentation
        json_schema_extra = {
            "example": {
                "wallet_data": {
                    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                    "eth_balance": "1500000000000000000",  # 1.5 ETH
                    "total_transactions": 234
                },
                "risk_score": {
                    "total_score": 45,
                    "risk_level": "medium"
                }
            }
        }
