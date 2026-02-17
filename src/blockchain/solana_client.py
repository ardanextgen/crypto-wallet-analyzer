# ============================================================================
# SOLANA_CLIENT.PY - Solana-Blockchain-Integration
# ============================================================================
#
# Was macht dieser Client?
# - Verbindet sich zu Solana-RPC
# - Ruft SOL-Balance ab
# - Lädt Transaktionshistorie
# - Basic Risiko-Analyse
#
# Solana vs Ethereum:
# - Schneller (400ms Blockzeit vs 12s)
# - Günstiger (Bruchteile eines Cents)
# - Andere API-Struktur
# ============================================================================

import os
from typing import List, Optional, Dict
from dotenv import load_dotenv
import logging
import requests

# Lade Umgebungsvariablen
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# SOLANA CLIENT KLASSE
# ============================================================================
class SolanaClient:
    """
    Client für Solana-Blockchain-Interaktion.

    Verwendet JSON-RPC API (einfacher als solana-py für MVP).
    """

    # Public RPC Endpoints
    MAINNET_RPC = "https://api.mainnet-beta.solana.com"

    def __init__(self, rpc_url: Optional[str] = None):
        """
        Initialisiert Solana Client.

        Args:
            rpc_url: Custom RPC URL (optional)
        """
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", self.MAINNET_RPC)
        logger.info(f"Solana Client initialisiert: {self.rpc_url}")

    def _rpc_call(self, method: str, params: List = None) -> Dict:
        """
        Führt JSON-RPC Call aus.

        Args:
            method: RPC-Methode (z.B. "getBalance")
            params: Parameter-Liste

        Returns:
            Response-Dictionary
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or []
        }

        try:
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise Exception(f"RPC Error: {data['error']}")

            return data.get("result", {})

        except Exception as e:
            logger.error(f"RPC Call failed: {e}")
            raise

    def get_balance(self, address: str) -> float:
        """
        Ruft SOL-Balance ab.

        Args:
            address: Solana-Wallet-Adresse

        Returns:
            Balance in SOL (nicht Lamports!)
        """
        try:
            result = self._rpc_call("getBalance", [address])
            lamports = result.get("value", 0)

            # Konvertiere Lamports zu SOL (1 SOL = 1B Lamports)
            sol = lamports / 1_000_000_000

            logger.info(f"Balance: {sol:.4f} SOL")
            return sol

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Balance: {e}")
            return 0.0

    def get_transaction_count(self, address: str) -> int:
        """
        Ruft Anzahl der Transaktionen ab.

        Args:
            address: Solana-Wallet-Adresse

        Returns:
            Anzahl Transaktionen
        """
        try:
            # Hole Signatur-Liste (limitiert auf 1000)
            result = self._rpc_call("getSignaturesForAddress", [
                address,
                {"limit": 1000}
            ])

            count = len(result) if isinstance(result, list) else 0
            logger.info(f"Transaktionen: {count}")
            return count

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der TX-Anzahl: {e}")
            return 0

    def get_wallet_data(self, address: str) -> Dict:
        """
        Ruft alle Wallet-Daten ab.

        Args:
            address: Solana-Wallet-Adresse

        Returns:
            Dictionary mit Wallet-Informationen
        """
        logger.info(f"Lade Solana Wallet-Daten: {address[:20]}...")

        balance = self.get_balance(address)
        tx_count = self.get_transaction_count(address)

        return {
            "chain": "solana",
            "address": address,
            "balance": balance,
            "native_token": "SOL",
            "transaction_count": tx_count,
            "tokens": [],  # TODO: SPL Token Support
        }

    def calculate_risk_score(self, wallet_data: Dict) -> Dict:
        """
        Einfache Risiko-Bewertung für Solana-Wallets.

        Args:
            wallet_data: Wallet-Daten-Dictionary

        Returns:
            Risk-Score-Dictionary
        """
        tx_count = wallet_data.get("transaction_count", 0)
        balance = wallet_data.get("balance", 0)

        # Einfache Heuristiken
        risk_score = 0
        factors = []

        # Zu wenige Transaktionen
        if tx_count < 5:
            risk_score += 60
            factors.append("Sehr wenige Transaktionen")
        elif tx_count < 20:
            risk_score += 30
            factors.append("Wenige Transaktionen")

        # Sehr neue Wallet (nur via TX-Count schätzbar)
        if tx_count == 0:
            risk_score += 40
            factors.append("Keine Transaktionshistorie")

        # Normalisiere Score
        risk_score = min(100, risk_score)

        # Risk Level
        if risk_score <= 30:
            risk_level = "low"
        elif risk_score <= 60:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "total_score": risk_score,
            "risk_level": risk_level,
            "factors": factors,
            "chain": "solana"
        }


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 SOLANA CLIENT - Test")
    print("="*60 + "\n")

    client = SolanaClient()

    # Bekannte Solana-Wallet (Solana Labs)
    test_address = "7Np41oeYqPefeNQEHSv1UDhYrehxin3NStELsSKCT4K2"

    print(f"Teste Wallet: {test_address}\n")

    # Hole Daten
    wallet_data = client.get_wallet_data(test_address)

    print(f"Balance: {wallet_data['balance']:.4f} SOL")
    print(f"Transaktionen: {wallet_data['transaction_count']}")

    # Risiko-Bewertung
    risk = client.calculate_risk_score(wallet_data)
    print(f"\nRisiko-Score: {risk['total_score']}/100")
    print(f"Risk-Level: {risk['risk_level']}")

    print("\n" + "="*60)
