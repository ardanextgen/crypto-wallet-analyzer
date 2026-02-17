# ============================================================================
# CHAIN_DETECTOR.PY - Automatische Blockchain-Erkennung
# ============================================================================
#
# Was macht dieses Modul?
# - Erkennt automatisch die Blockchain einer Wallet-Adresse
# - Unterstützt: Ethereum, BSC, Polygon, Solana, Bitcoin, Cardano
# - Basiert auf Adressformat-Analyse
#
# Verwendung:
#     from chain_detector import detect_chain
#     chain = detect_chain("0x123...")  # Returns: "ethereum" oder "evm"
#     chain = detect_chain("DYw8j...")  # Returns: "solana"
# ============================================================================

import re
from typing import Optional, List, Dict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CHAIN ENUM
# ============================================================================
class Chain(str, Enum):
    """
    Unterstützte Blockchains.

    Kategorien:
    - EVM: Ethereum, BSC, Polygon, Arbitrum, etc. (gleiches Format!)
    - Solana: Eigenes Format
    - Bitcoin: Mehrere Formate (Legacy, SegWit, etc.)
    """

    # EVM-Chains (gleiches Adressformat!)
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    EVM_UNKNOWN = "evm"  # EVM-kompatibel, aber unbekannte Chain

    # Non-EVM Chains
    SOLANA = "solana"
    BITCOIN = "bitcoin"
    BITCOIN_SEGWIT = "bitcoin-segwit"
    BITCOIN_LEGACY = "bitcoin-legacy"
    CARDANO = "cardano"
    COSMOS = "cosmos"

    # Unknown
    UNKNOWN = "unknown"


# ============================================================================
# ADRESSFORMAT-PATTERNS
# ============================================================================

# Ethereum & EVM-Chains: 0x + 40 Hex-Zeichen
EVM_PATTERN = re.compile(r'^0x[a-fA-F0-9]{40}$')

# Solana: Base58, 32-44 Zeichen
SOLANA_PATTERN = re.compile(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$')

# Bitcoin Patterns
BTC_LEGACY_PATTERN = re.compile(r'^1[a-km-zA-HJ-NP-Z1-9]{25,34}$')
BTC_P2SH_PATTERN = re.compile(r'^3[a-km-zA-HJ-NP-Z1-9]{25,34}$')
BTC_SEGWIT_PATTERN = re.compile(r'^bc1[a-zA-HJ-NP-Z0-9]{39,59}$')

# Cardano
CARDANO_PATTERN = re.compile(r'^addr1[a-z0-9]{58,}$')

# Cosmos
COSMOS_PATTERN = re.compile(r'^cosmos1[a-z0-9]{38,}$')


# ============================================================================
# CHAIN DETECTION
# ============================================================================
def detect_chain(address: str) -> Chain:
    """
    Erkennt die Blockchain anhand der Adresse.

    Algorithmus:
    1. Prüfe Format gegen bekannte Patterns
    2. Bei EVM: Kann nicht zwischen ETH/BSC/etc. unterscheiden!
    3. Bei Solana/Bitcoin: Eindeutige Erkennung möglich

    Args:
        address: Wallet-Adresse als String

    Returns:
        Chain Enum

    Beispiele:
        >>> detect_chain("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
        Chain.EVM_UNKNOWN  # Könnte ETH, BSC, Polygon, etc. sein!

        >>> detect_chain("DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK")
        Chain.SOLANA

        >>> detect_chain("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
        Chain.BITCOIN_SEGWIT
    """
    # Normalisiere Input
    address = address.strip()

    # ========================================================================
    # ETHEREUM & EVM-CHAINS (Prüfe zuerst - sehr spezifisch: 0x...)
    # ========================================================================
    if EVM_PATTERN.match(address):
        # Problem: Alle EVM-Chains nutzen das gleiche Format!
        # 0x123... könnte Ethereum, BSC, Polygon, etc. sein
        # Für präzise Erkennung: Multi-Chain-Scan nötig (siehe unten)
        logger.info(f"EVM-Adresse erkannt: {address[:10]}...")
        return Chain.EVM_UNKNOWN

    # ========================================================================
    # BITCOIN (Prüfe VOR Solana - spezifischere Patterns!)
    # ========================================================================
    # Bitcoin SegWit (bc1...)
    if BTC_SEGWIT_PATTERN.match(address):
        logger.info(f"Bitcoin SegWit erkannt: {address[:10]}...")
        return Chain.BITCOIN_SEGWIT

    # Bitcoin Legacy (1...)
    if BTC_LEGACY_PATTERN.match(address):
        logger.info(f"Bitcoin Legacy erkannt: {address[:10]}...")
        return Chain.BITCOIN_LEGACY

    # Bitcoin P2SH (3...)
    if BTC_P2SH_PATTERN.match(address):
        logger.info(f"Bitcoin P2SH erkannt: {address[:10]}...")
        return Chain.BITCOIN

    # ========================================================================
    # SOLANA (Prüfe NACH Bitcoin - allgemeineres Pattern)
    # ========================================================================
    if SOLANA_PATTERN.match(address) and not address.startswith(('1', '3', 'bc1')):
        # Solana nutzt Base58-Encoding
        # Eindeutig erkennbar, aber NACH Bitcoin prüfen!
        logger.info(f"Solana-Adresse erkannt: {address[:10]}...")
        return Chain.SOLANA

    # ========================================================================
    # CARDANO
    # ========================================================================
    if CARDANO_PATTERN.match(address):
        logger.debug(f"Cardano-Adresse erkannt: {address[:10]}...")
        return Chain.CARDANO

    # ========================================================================
    # COSMOS
    # ========================================================================
    if COSMOS_PATTERN.match(address):
        logger.debug(f"Cosmos-Adresse erkannt: {address[:10]}...")
        return Chain.COSMOS

    # ========================================================================
    # UNKNOWN
    # ========================================================================
    logger.warning(f"Unbekanntes Adressformat: {address[:20]}...")
    return Chain.UNKNOWN


# ============================================================================
# EVM MULTI-CHAIN DETECTION
# ============================================================================
def detect_evm_chains(address: str, check_activity: bool = True) -> List[str]:
    """
    Bei EVM-Adressen: Prüft auf welchen Chains die Wallet aktiv ist.

    Problem: 0x123... ist auf Ethereum, BSC, Polygon identisch!
    Lösung: Parallel alle EVM-Chains prüfen, wo Aktivität vorhanden ist.

    Args:
        address: EVM-Adresse (0x...)
        check_activity: Wenn True, prüft Balance/TXs auf allen Chains

    Returns:
        Liste von aktiven Chain-Namen

    Beispiel:
        >>> detect_evm_chains("0x123...")
        ["ethereum", "bsc", "polygon"]  # Wallet ist auf allen 3 Chains aktiv!
    """
    if detect_chain(address) not in [Chain.EVM_UNKNOWN, Chain.ETHEREUM, Chain.BSC, Chain.POLYGON]:
        return []

    if not check_activity:
        # Ohne Activity-Check: Alle EVM-Chains sind möglich
        return ["ethereum", "bsc", "polygon", "arbitrum", "optimism", "avalanche"]

    # TODO: Implementiere parallele Balance/TX-Checks
    # Für jetzt: Gebe alle EVM-Chains zurück
    logger.info("Multi-Chain Activity-Check noch nicht implementiert")
    return ["ethereum", "bsc", "polygon"]


# ============================================================================
# HELPER: CHAIN INFO
# ============================================================================
def get_chain_info(chain: Chain) -> Dict:
    """
    Gibt Informationen über eine Chain zurück.

    Returns:
        Dictionary mit Chain-Details
    """
    chain_info = {
        Chain.ETHEREUM: {
            "name": "Ethereum",
            "native_token": "ETH",
            "type": "evm",
            "block_explorer": "https://etherscan.io",
            "rpc_url": "https://mainnet.infura.io/v3/",
        },
        Chain.BSC: {
            "name": "Binance Smart Chain",
            "native_token": "BNB",
            "type": "evm",
            "block_explorer": "https://bscscan.com",
            "rpc_url": "https://bsc-dataseed.binance.org",
        },
        Chain.POLYGON: {
            "name": "Polygon",
            "native_token": "MATIC",
            "type": "evm",
            "block_explorer": "https://polygonscan.com",
            "rpc_url": "https://polygon-rpc.com",
        },
        Chain.SOLANA: {
            "name": "Solana",
            "native_token": "SOL",
            "type": "solana",
            "block_explorer": "https://solscan.io",
            "rpc_url": "https://api.mainnet-beta.solana.com",
        },
        Chain.BITCOIN: {
            "name": "Bitcoin",
            "native_token": "BTC",
            "type": "bitcoin",
            "block_explorer": "https://blockchain.com",
            "rpc_url": None,  # Bitcoin nutzt andere APIs
        },
    }

    return chain_info.get(chain, {
        "name": str(chain),
        "native_token": "UNKNOWN",
        "type": "unknown"
    })


# ============================================================================
# VALIDATOR
# ============================================================================
def is_valid_address(address: str, chain: Optional[Chain] = None) -> bool:
    """
    Prüft ob eine Adresse gültig ist.

    Args:
        address: Zu prüfende Adresse
        chain: Optional spezifische Chain zum Prüfen

    Returns:
        True wenn gültig, False sonst
    """
    if chain:
        # Prüfe gegen spezifische Chain
        detected = detect_chain(address)
        if chain.startswith("bitcoin"):
            return detected.value.startswith("bitcoin")
        return detected == chain

    # Allgemeine Validierung
    return detect_chain(address) != Chain.UNKNOWN


# ============================================================================
# CLI DEMO
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 CHAIN DETECTOR - Demo")
    print("="*70 + "\n")

    # Test-Adressen
    test_addresses = [
        ("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", "Ethereum/BSC/Polygon"),
        ("DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK", "Solana"),
        ("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", "Bitcoin SegWit"),
        ("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin Legacy"),
        ("3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy", "Bitcoin P2SH"),
        ("addr1qxy2...", "Cardano"),
        ("cosmos1...", "Cosmos"),
        ("invalid_address", "Invalid"),
    ]

    for address, expected in test_addresses:
        chain = detect_chain(address)
        info = get_chain_info(chain)

        print(f"Adresse: {address[:30]}...")
        print(f"Erkannt: {chain.value} ({info.get('name', 'Unknown')})")
        print(f"Erwartet: {expected}")
        print(f"Match: {'✅' if expected.lower() in chain.value or chain.value in expected.lower() else '❌'}")
        print()

    print("="*70)
