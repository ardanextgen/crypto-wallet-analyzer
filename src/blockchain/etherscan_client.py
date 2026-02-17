# ============================================================================
# ETHERSCAN_CLIENT.PY - Etherscan API Integration
# ============================================================================
#
# Was ist Etherscan?
# - Block Explorer für Ethereum
# - Webseite: https://etherscan.io
# - Bietet API für historische Blockchain-Daten
#
# Warum Etherscan statt direktem Blockchain-Zugriff?
# - Schneller: Daten sind indexiert
# - Einfacher: Keine Block-für-Block-Iteration nötig
# - Mehr Features: Token-Balances, Contract-Info, etc.
#
# API-Limits (kostenloser Tier):
# - 5 Requests pro Sekunde
# - 100.000 Requests pro Tag
# ============================================================================

import os
import requests
import time
from typing import List, Optional, Dict
from dotenv import load_dotenv
import logging

from .data_models import Transaction, TokenHolding, WalletData

# Lade Umgebungsvariablen
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ETHERSCAN CLIENT KLASSE
# ============================================================================
class EtherscanClient:
    """
    Client für Etherscan API.

    Funktionen:
    - Transaktionshistorie abrufen
    - Token-Balances abrufen
    - Contract-Informationen abrufen

    Verwendung:
        client = EtherscanClient()
        transactions = client.get_transactions("0x123...")
    """

    # API Basis-URL (V2 - aktualisiert Feb 2026)
    BASE_URL = "https://api.etherscan.io/v2/api"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert Etherscan Client.

        Args:
            api_key: Etherscan API Key (optional, wird aus .env geladen)
        """
        # API Key aus .env laden falls nicht gegeben
        self.api_key = api_key or os.getenv("ETHERSCAN_API_KEY")

        if not self.api_key:
            logger.warning("⚠️  Kein Etherscan API Key gefunden!")
            logger.warning("   API-Calls sind stark limitiert ohne Key.")
            logger.warning("   Erstelle einen kostenlosen Key auf https://etherscan.io")

        # Rate Limiting (max 5 Requests/Sekunde)
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms = 5 req/sec

    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    def _wait_for_rate_limit(self):
        """
        Wartet um Rate-Limit einzuhalten.

        Etherscan erlaubt max 5 Requests/Sekunde.
        Wir warten mindestens 200ms zwischen Requests.
        """
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    # ========================================================================
    # API REQUEST HELPER
    # ========================================================================
    def _make_request(self, params: Dict) -> Dict:
        """
        Führt API-Request aus mit Error-Handling.

        Args:
            params: Query-Parameter für die API

        Returns:
            JSON-Response als Dictionary

        Raises:
            Exception bei API-Fehlern
        """
        # Rate Limit einhalten
        self._wait_for_rate_limit()

        # API Key hinzufügen
        params['apikey'] = self.api_key

        # Chain ID für V2 API (1 = Ethereum Mainnet)
        params['chainid'] = 1

        try:
            # HTTP GET Request
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()  # Wirft Exception bei HTTP-Fehler

            # Parse JSON
            data = response.json()

            # Prüfe Etherscan-spezifische Fehler
            if data.get('status') == '0' and data.get('message') != 'No transactions found':
                error_msg = data.get('result', 'Unknown error')
                logger.error(f"Etherscan API Error: {error_msg}")
                raise Exception(f"Etherscan API Error: {error_msg}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request Error: {e}")
            raise

    # ========================================================================
    # TRANSAKTIONSHISTORIE
    # ========================================================================
    def get_transactions(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
        sort: str = "desc",
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """
        Ruft normale ETH-Transaktionen einer Wallet ab.

        Args:
            address: Wallet-Adresse
            start_block: Erster Block (default: 0 = Anfang)
            end_block: Letzter Block (default: 99999999 = neuester)
            sort: "asc" oder "desc" (neueste zuerst)
            limit: Max. Anzahl Transaktionen (optional)

        Returns:
            Liste von Transaction-Objekten
        """
        logger.info(f"Rufe Transaktionen ab für {address[:10]}...")

        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': sort,
        }

        try:
            data = self._make_request(params)

            # Parse Transaktionen
            transactions = []
            raw_txs = data.get('result', [])

            # Limitiere Anzahl falls angegeben
            if limit and isinstance(raw_txs, list):
                raw_txs = raw_txs[:limit]

            # Konvertiere zu Transaction-Objekten
            for tx in raw_txs:
                if isinstance(tx, dict):  # Validierung
                    try:
                        transaction = Transaction(
                            hash=tx['hash'],
                            from_address=tx['from'],  # Nutze from_address
                            to_address=tx.get('to', ''),  # Contract Creation kann to=None haben
                            value=tx['value'],
                            timestamp=int(tx['timeStamp']),
                            block_number=int(tx['blockNumber']),
                            gas_used=int(tx['gasUsed']),
                            is_error=tx.get('isError', '0')
                        )
                        transactions.append(transaction)
                    except Exception as e:
                        logger.warning(f"Fehler beim Parsen von TX {tx.get('hash', 'unknown')}: {e}")
                        continue

            logger.info(f"✅ {len(transactions)} Transaktionen abgerufen")
            return transactions

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Transaktionen: {e}")
            # Gebe leere Liste zurück statt zu crashen
            return []

    # ========================================================================
    # INTERNAL TRANSACTIONS (Contract-Interaktionen)
    # ========================================================================
    def get_internal_transactions(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
        sort: str = "desc"
    ) -> List[Transaction]:
        """
        Ruft interne Transaktionen ab.

        Was sind interne Transaktionen?
        - ETH-Transfers, die von Smart Contracts ausgelöst werden
        - Nicht direkt in der Blockchain sichtbar
        - Wichtig für vollständige Analyse!

        Beispiel:
        - User sendet ETH an DEX (Uniswap)
        - DEX sendet ETH intern weiter an Liquidity Pool
        - Interne TX: DEX -> Pool

        Args:
            address: Wallet-Adresse
            start_block: Erster Block
            end_block: Letzter Block
            sort: "asc" oder "desc"

        Returns:
            Liste von Transaction-Objekten
        """
        logger.info(f"Rufe interne Transaktionen ab für {address[:10]}...")

        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': sort,
        }

        try:
            data = self._make_request(params)

            transactions = []
            raw_txs = data.get('result', [])

            for tx in raw_txs:
                if isinstance(tx, dict):
                    try:
                        transaction = Transaction(
                            hash=tx['hash'],
                            from_address=tx['from'],
                            to_address=tx.get('to', ''),
                            value=tx.get('value', '0'),
                            timestamp=int(tx['timeStamp']),
                            block_number=int(tx['blockNumber']),
                            gas_used=int(tx.get('gasUsed', 0)),
                            is_error=tx.get('isError', '0')
                        )
                        transactions.append(transaction)
                    except Exception as e:
                        logger.warning(f"Fehler beim Parsen von interner TX: {e}")
                        continue

            logger.info(f"✅ {len(transactions)} interne Transaktionen abgerufen")
            return transactions

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der internen Transaktionen: {e}")
            return []

    # ========================================================================
    # ERC20 TOKEN TRANSFERS
    # ========================================================================
    def get_token_transfers(
        self,
        address: str,
        contract_address: Optional[str] = None,
        start_block: int = 0,
        end_block: int = 99999999
    ) -> List[Dict]:
        """
        Ruft ERC20 Token-Transfers ab.

        ERC20 = Standard für Tokens auf Ethereum
        Beispiele: USDT, USDC, DAI, UNI, etc.

        Args:
            address: Wallet-Adresse
            contract_address: Spezifischer Token (optional)
            start_block: Erster Block
            end_block: Letzter Block

        Returns:
            Liste von Token-Transfer-Dicts
        """
        logger.info(f"Rufe Token-Transfers ab für {address[:10]}...")

        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': 'desc',
        }

        # Falls spezifischer Token gewünscht
        if contract_address:
            params['contractaddress'] = contract_address

        try:
            data = self._make_request(params)
            transfers = data.get('result', [])

            logger.info(f"✅ {len(transfers)} Token-Transfers abgerufen")
            return transfers if isinstance(transfers, list) else []

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Token-Transfers: {e}")
            return []

    # ========================================================================
    # TOKEN BALANCES
    # ========================================================================
    def get_token_balance(
        self,
        address: str,
        contract_address: str
    ) -> str:
        """
        Ruft Balance eines spezifischen ERC20 Tokens ab.

        Args:
            address: Wallet-Adresse
            contract_address: Token Contract Address

        Returns:
            Balance als String (in kleinster Einheit)
        """
        params = {
            'module': 'account',
            'action': 'tokenbalance',
            'contractaddress': contract_address,
            'address': address,
            'tag': 'latest',
        }

        try:
            data = self._make_request(params)
            return data.get('result', '0')

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Token-Balance: {e}")
            return '0'

    # ========================================================================
    # ZUSAMMENFASSENDE WALLET-DATEN
    # ========================================================================
    def get_complete_wallet_data(
        self,
        address: str,
        max_transactions: int = 100
    ) -> WalletData:
        """
        Ruft alle verfügbaren Wallet-Daten ab.

        Dies ist die Hauptmethode, die alles kombiniert:
        - Normale Transaktionen
        - Interne Transaktionen
        - Token-Transfers und Balances

        Args:
            address: Wallet-Adresse
            max_transactions: Max. Anzahl Transaktionen

        Returns:
            Vollständiges WalletData-Objekt
        """
        logger.info(f"\n🔍 Lade vollständige Wallet-Daten für {address}")
        logger.info("=" * 60)

        # 1. Normale Transaktionen
        transactions = self.get_transactions(address, limit=max_transactions)

        # 2. Interne Transaktionen (für vollständigere Analyse)
        internal_txs = self.get_internal_transactions(address)

        # Kombiniere beide Listen (nur unique hashes)
        all_tx_hashes = set()
        combined_transactions = []

        for tx in transactions + internal_txs:
            if tx.hash not in all_tx_hashes:
                all_tx_hashes.add(tx.hash)
                combined_transactions.append(tx)

        # Sortiere nach Timestamp (neueste zuerst)
        combined_transactions.sort(key=lambda x: x.timestamp, reverse=True)

        # 3. Token-Transfers analysieren
        token_transfers = self.get_token_transfers(address)

        # Extrahiere unique Token-Contract-Adressen
        token_contracts = {}
        for transfer in token_transfers:
            contract = transfer.get('contractAddress')
            if contract and contract not in token_contracts:
                token_contracts[contract] = {
                    'name': transfer.get('tokenName', 'Unknown'),
                    'symbol': transfer.get('tokenSymbol', '???'),
                    'decimals': int(transfer.get('tokenDecimal', 18))
                }

        # 4. Hole Token-Balances
        token_holdings = []
        for contract_address, token_info in token_contracts.items():
            balance = self.get_token_balance(address, contract_address)

            if balance != '0':  # Nur Tokens mit Balance
                holding = TokenHolding(
                    token_address=contract_address,
                    token_name=token_info['name'],
                    token_symbol=token_info['symbol'],
                    balance=balance,
                    decimals=token_info['decimals']
                )
                token_holdings.append(holding)

        # 5. Berechne Metadaten
        first_tx_time = None
        last_tx_time = None

        if combined_transactions:
            # Sortiere für älteste/neueste
            sorted_txs = sorted(combined_transactions, key=lambda x: x.timestamp)
            first_tx_time = sorted_txs[0].timestamp
            last_tx_time = sorted_txs[-1].timestamp

        # 6. Erstelle WalletData-Objekt
        wallet_data = WalletData(
            address=address,
            eth_balance="0",  # Wird von Web3Client gefüllt
            transactions=combined_transactions,
            token_holdings=token_holdings,
            first_transaction_timestamp=first_tx_time,
            last_transaction_timestamp=last_tx_time,
            total_transactions=len(combined_transactions)
        )

        logger.info("=" * 60)
        logger.info(f"✅ Wallet-Daten komplett!")
        logger.info(f"   📝 Transaktionen: {len(combined_transactions)}")
        logger.info(f"   🪙 Token-Holdings: {len(token_holdings)}")
        logger.info("")

        return wallet_data


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================
if __name__ == "__main__":
    # Test mit bekannter Wallet
    TEST_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik

    # Client erstellen
    client = EtherscanClient()

    # Vollständige Daten abrufen
    wallet_data = client.get_complete_wallet_data(TEST_ADDRESS, max_transactions=10)

    # Ausgabe
    print(f"\n📊 WALLET ANALYSE")
    print(f"Adresse: {wallet_data.address}")
    print(f"Transaktionen: {wallet_data.total_transactions}")
    print(f"Token-Holdings: {len(wallet_data.token_holdings)}")

    if wallet_data.token_holdings:
        print(f"\n🪙 Top Tokens:")
        for token in wallet_data.token_holdings[:5]:
            print(f"   - {token.token_symbol}: {token.get_balance_decimal():.2f}")

    if wallet_data.get_wallet_age_days():
        print(f"\n⏱️  Wallet-Alter: {wallet_data.get_wallet_age_days()} Tage")
