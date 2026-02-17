# ============================================================================
# WEB3_CLIENT.PY - Direkte Ethereum-Blockchain-Interaktion
# ============================================================================
#
# Was macht dieser Client?
# - Verbindet sich zu einem Ethereum-Node (via Infura/Alchemy)
# - Ruft aktuelle Wallet-Balances ab
# - Lädt Transaktionshistorie
# - Prüft Smart Contract Interaktionen
#
# Was ist Web3.py?
# - Python-Bibliothek für Ethereum-Interaktion
# - Ermöglicht Zugriff auf Blockchain-Daten ohne eigenen Node
# - Verwendet RPC (Remote Procedure Call) Protokoll
#
# Was ist ein RPC Provider?
# - Ein Server, der Zugriff auf die Ethereum-Blockchain bietet
# - Beispiele: Infura, Alchemy, QuickNode
# - Wir brauchen keinen eigenen Node (würde >1TB Speicher brauchen!)
# ============================================================================

import os
from typing import List, Optional
from web3 import Web3
from web3.exceptions import Web3Exception
from eth_utils import is_address, to_checksum_address
from dotenv import load_dotenv
import logging

from .data_models import Transaction, WalletData

# Lade Umgebungsvariablen aus .env Datei
load_dotenv()

# Logging konfigurieren (für Debug-Ausgaben)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# WEB3 CLIENT KLASSE
# ============================================================================
class Web3Client:
    """
    Client für direkte Ethereum-Blockchain-Interaktion.

    Verwendung:
        client = Web3Client()
        balance = client.get_eth_balance("0x123...")
    """

    def __init__(self, provider_url: Optional[str] = None):
        """
        Initialisiert Web3-Verbindung.

        Args:
            provider_url: URL des RPC-Providers (optional)
                        Falls nicht angegeben, wird aus .env geladen
        """
        # Wenn keine URL gegeben, aus .env laden
        if not provider_url:
            # Versuche verschiedene Provider
            infura_id = os.getenv("INFURA_PROJECT_ID")
            alchemy_url = os.getenv("ALCHEMY_URL")

            if infura_id:
                # Infura URL zusammenbauen
                # Format: https://mainnet.infura.io/v3/{PROJECT_ID}
                provider_url = f"https://mainnet.infura.io/v3/{infura_id}"
                logger.info("Verwende Infura als RPC Provider")

            elif alchemy_url:
                provider_url = alchemy_url
                logger.info("Verwende Alchemy als RPC Provider")

            else:
                # Fallback: Öffentlicher Ethereum Node (langsam, rate-limited)
                provider_url = "https://eth.llamarpc.com"
                logger.warning("Kein API-Key gefunden! Verwende öffentlichen Node (langsam)")

        # Web3 Instanz erstellen
        try:
            self.w3 = Web3(Web3.HTTPProvider(provider_url))

            # Prüfe ob Verbindung funktioniert
            if not self.w3.is_connected():
                raise ConnectionError("Konnte nicht zur Ethereum-Blockchain verbinden")

            # Hole aktuelle Block-Nummer (um Verbindung zu testen)
            current_block = self.w3.eth.block_number
            logger.info(f"Verbunden mit Ethereum! Aktueller Block: {current_block}")

        except Exception as e:
            logger.error(f"Fehler bei Web3-Initialisierung: {e}")
            raise

    # ========================================================================
    # ADRESS-VALIDIERUNG
    # ========================================================================
    def is_valid_address(self, address: str) -> bool:
        """
        Prüft ob eine Adresse gültig ist.

        Ethereum-Adressen:
        - Beginnen mit "0x"
        - Haben 40 Hex-Zeichen (+ "0x" = 42 Zeichen total)
        - Beispiel: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

        Args:
            address: Zu prüfende Wallet-Adresse

        Returns:
            True wenn gültig, False sonst
        """
        return is_address(address)

    def to_checksum_address(self, address: str) -> str:
        """
        Konvertiert Adresse zu Checksum-Format.

        Was ist Checksum?
        - Großschreibung kodiert eine Prüfsumme
        - Verhindert Tippfehler
        - Beispiel: 0xabc... -> 0xAbC... (Groß/Klein hat Bedeutung!)

        Args:
            address: Ethereum-Adresse

        Returns:
            Adresse im Checksum-Format
        """
        if not self.is_valid_address(address):
            raise ValueError(f"Ungültige Ethereum-Adresse: {address}")

        return to_checksum_address(address)

    # ========================================================================
    # BALANCE-ABFRAGE
    # ========================================================================
    def get_eth_balance(self, address: str) -> str:
        """
        Ruft ETH-Balance einer Wallet ab.

        Args:
            address: Wallet-Adresse

        Returns:
            Balance in Wei (als String, wegen großen Zahlen)

        Beispiel:
            balance = client.get_eth_balance("0x123...")
            # Returns: "1500000000000000000" (= 1.5 ETH)
        """
        try:
            # Normalisiere Adresse zu Checksum-Format
            address = self.to_checksum_address(address)

            # Rufe Balance ab
            # eth.get_balance gibt Wei zurück (kleinste ETH-Einheit)
            balance_wei = self.w3.eth.get_balance(address)

            # Konvertiere zu String (Python int kann sehr groß werden)
            return str(balance_wei)

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Balance für {address}: {e}")
            raise

    # ========================================================================
    # BLOCK-INFORMATIONEN
    # ========================================================================
    def get_current_block_number(self) -> int:
        """
        Gibt die aktuelle Block-Nummer zurück.

        Wichtig für:
        - Prüfen wie alt eine Transaktion ist
        - Berechnen von Zeitstempeln

        Returns:
            Aktuelle Block-Nummer
        """
        return self.w3.eth.block_number

    def get_block_timestamp(self, block_number: int) -> int:
        """
        Ruft Zeitstempel eines Blocks ab.

        Ethereum-Blöcke:
        - Werden ca. alle 12 Sekunden erstellt
        - Enthalten einen Unix-Timestamp

        Args:
            block_number: Block-Nummer

        Returns:
            Unix-Timestamp (Sekunden seit 1970)
        """
        try:
            block = self.w3.eth.get_block(block_number)
            return block['timestamp']

        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Block {block_number}: {e}")
            raise

    # ========================================================================
    # TRANSAKTIONS-DETAILS
    # ========================================================================
    def get_transaction(self, tx_hash: str) -> dict:
        """
        Ruft Details einer spezifischen Transaktion ab.

        Args:
            tx_hash: Transaction Hash (z.B. "0xabc123...")

        Returns:
            Dictionary mit Transaktions-Details
        """
        try:
            # Hole Transaktion
            tx = self.w3.eth.get_transaction(tx_hash)

            # Hole Transaction Receipt (für Status und Gas)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)

            # Kombiniere Daten
            return {
                'hash': tx['hash'].hex(),
                'from': tx['from'],
                'to': tx['to'],
                'value': str(tx['value']),  # in Wei
                'gas': tx['gas'],
                'gasPrice': str(tx['gasPrice']),
                'gasUsed': receipt['gasUsed'],
                'blockNumber': tx['blockNumber'],
                'status': receipt['status'],  # 1 = success, 0 = failed
            }

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Transaktion {tx_hash}: {e}")
            raise

    # ========================================================================
    # SMART CONTRACT PRÜFUNG
    # ========================================================================
    def is_contract(self, address: str) -> bool:
        """
        Prüft ob eine Adresse ein Smart Contract ist.

        Unterschied Wallet vs Contract:
        - Wallet: Wird von einem User kontrolliert (Private Key)
        - Contract: Code auf der Blockchain

        Wie erkennen?
        - Contracts haben Code (bytecode) an ihrer Adresse
        - Wallets haben leeren Code

        Args:
            address: Zu prüfende Adresse

        Returns:
            True wenn Contract, False wenn Wallet
        """
        try:
            address = self.to_checksum_address(address)

            # Hole Code an der Adresse
            code = self.w3.eth.get_code(address)

            # Wenn Code vorhanden (länger als "0x"), ist es ein Contract
            return len(code) > 0

        except Exception as e:
            logger.error(f"Fehler beim Prüfen von Contract {address}: {e}")
            return False

    # ========================================================================
    # WALLET-DATEN ZUSAMMENFASSEN
    # ========================================================================
    def get_wallet_data(self, address: str) -> WalletData:
        """
        Ruft alle Basis-Wallet-Daten ab.

        Wichtig: Diese Methode gibt nur Basis-Daten!
        Für vollständige Transaktionshistorie nutze EtherscanClient.

        Args:
            address: Wallet-Adresse

        Returns:
            WalletData Objekt mit aktueller Balance
        """
        try:
            # Validiere Adresse
            address = self.to_checksum_address(address)

            # Hole ETH Balance
            eth_balance = self.get_eth_balance(address)

            # Erstelle WalletData Objekt
            wallet_data = WalletData(
                address=address,
                eth_balance=eth_balance,
                transactions=[],  # Wird von EtherscanClient gefüllt
                token_holdings=[],  # Wird von EtherscanClient gefüllt
                total_transactions=0
            )

            logger.info(f"Wallet-Daten abgerufen für {address}")
            return wallet_data

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Wallet-Daten: {e}")
            raise


# ============================================================================
# HELPER-FUNKTIONEN
# ============================================================================
def wei_to_eth(wei: int) -> float:
    """
    Konvertiert Wei zu ETH.

    1 ETH = 10^18 Wei
    1 Wei = 0.000000000000000001 ETH

    Args:
        wei: Betrag in Wei

    Returns:
        Betrag in ETH
    """
    return wei / (10 ** 18)


def eth_to_wei(eth: float) -> int:
    """
    Konvertiert ETH zu Wei.

    Args:
        eth: Betrag in ETH

    Returns:
        Betrag in Wei
    """
    return int(eth * (10 ** 18))


# ============================================================================
# BEISPIEL-VERWENDUNG (zum Testen)
# ============================================================================
if __name__ == "__main__":
    # Dieser Code läuft nur wenn Datei direkt ausgeführt wird
    # (nicht beim Import)

    # Test mit Vitalik's Wallet (bekannte Adresse)
    VITALIK_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    # Client erstellen
    client = Web3Client()

    # Balance abfragen
    print(f"\n🔍 Analysiere Wallet: {VITALIK_ADDRESS}\n")

    balance_wei = client.get_eth_balance(VITALIK_ADDRESS)
    balance_eth = wei_to_eth(int(balance_wei))

    print(f"💰 ETH Balance: {balance_eth:.4f} ETH")
    print(f"   (= {balance_wei} Wei)")

    # Prüfe ob es ein Contract ist
    is_contract = client.is_contract(VITALIK_ADDRESS)
    print(f"📜 Ist Contract: {'Ja' if is_contract else 'Nein'}")

    # Aktueller Block
    current_block = client.get_current_block_number()
    print(f"⛓️  Aktueller Block: {current_block}")
