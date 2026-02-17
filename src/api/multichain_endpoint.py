# ============================================================================
# MULTICHAIN_ENDPOINT.PY - Multi-Chain API Endpoint
# ============================================================================
#
# Neuer Endpoint für automatische Chain-Erkennung und Analyse
# Mit Usage Limits: Free (10/day) vs Pro (unlimited)
# ============================================================================

from fastapi import HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from ..blockchain.chain_detector import detect_chain, Chain, get_chain_info
from ..blockchain.etherscan_client import EtherscanClient
from ..blockchain.solana_client import SolanaClient
from ..blockchain.web3_client import Web3Client
from ..analysis.risk_engine import RiskEngine
from ..database.database import get_db
from ..database.models import User

logger = logging.getLogger(__name__)

# ============================================================================
# USAGE LIMITS
# ============================================================================
FREE_TIER_DAILY_LIMIT = 10  # Free users: 10 analyses per day
PRO_TIER_DAILY_LIMIT = None  # Pro users: Unlimited


async def analyze_multichain_wallet(
    address: str,
    current_user: Optional[User] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Analysiert Wallet automatisch über alle unterstützten Chains.

    Args:
        address: Wallet-Adresse (beliebige Chain)
        current_user: Optional authenticated user (for usage tracking)
        db: Optional database session (for usage tracking)

    Returns:
        Dict mit Analyse-Ergebnissen

    Workflow:
        1. Check Usage Limits (if user authenticated)
        2. Erkenne Chain automatisch
        3. Nutze chain-spezifischen Client
        4. Führe Risiko-Analyse durch
        5. Increment Usage Count
        6. Gebe einheitliche Response zurück
    """
    logger.info(f"Multi-Chain Analyse für: {address}")

    # ========================================================================
    # STEP 1: Check Usage Limits (für authenticated users)
    # ========================================================================
    if current_user and db:
        # Reset usage count if it's a new day
        _reset_usage_if_needed(current_user, db)

        # Check limits für Free-Tier Users
        if current_user.subscription_status == "free":
            if current_user.usage_count >= FREE_TIER_DAILY_LIMIT:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Daily limit reached",
                        "message": f"Free tier is limited to {FREE_TIER_DAILY_LIMIT} analyses per day.",
                        "limit": FREE_TIER_DAILY_LIMIT,
                        "used": current_user.usage_count,
                        "reset_at": current_user.usage_reset_at.isoformat() if current_user.usage_reset_at else None,
                        "upgrade_url": "/pricing"
                    }
                )

        logger.info(f"User {current_user.email}: {current_user.usage_count}/{FREE_TIER_DAILY_LIMIT if current_user.subscription_status == 'free' else 'unlimited'}")

    # ========================================================================
    # STEP 2: Chain Detection
    # ========================================================================
    detected_chain = detect_chain(address)
    chain_info = get_chain_info(detected_chain)

    logger.info(f"Erkannte Chain: {detected_chain.value}")

    # ========================================================================
    # STEP 3 & 4: Chain-spezifische Analyse
    # ========================================================================
    result = None
    try:
        if detected_chain == Chain.EVM_UNKNOWN:
            # Ethereum/BSC/Polygon (nutze Ethereum-Client)
            result = await _analyze_evm(address, chain_info)

        elif detected_chain == Chain.SOLANA:
            # Solana
            result = await _analyze_solana(address, chain_info)

        elif detected_chain.value.startswith("bitcoin"):
            # Bitcoin
            result = _analyze_bitcoin(address, chain_info)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Chain nicht unterstützt: {detected_chain.value}"
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Fehler bei Multi-Chain Analyse: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # STEP 5: Increment Usage Count (nur bei Erfolg!)
    # ========================================================================
    if current_user and db and result:
        current_user.usage_count += 1
        db.commit()
        logger.info(f"Usage incremented: {current_user.email} - {current_user.usage_count}/{FREE_TIER_DAILY_LIMIT if current_user.subscription_status == 'free' else '∞'}")

    return result


async def _analyze_evm(address: str, chain_info: Dict) -> Dict:
    """Analysiert EVM-kompatible Wallet (ETH/BSC/Polygon)"""
    # Nutze bestehenden Ethereum-Code
    web3_client = Web3Client()
    etherscan_client = EtherscanClient()

    # Lade Daten
    wallet_data = etherscan_client.get_complete_wallet_data(address, max_transactions=50)
    eth_balance = web3_client.get_eth_balance(address)
    wallet_data.eth_balance = eth_balance

    # Risiko-Analyse
    risk_engine = RiskEngine()
    risk_score = risk_engine.analyze(wallet_data)

    return {
        "chain": "ethereum",  # Default zu Ethereum (könnte auch BSC/Polygon sein)
        "chain_info": chain_info,
        "address": address,
        "balance": wallet_data.get_eth_balance_decimal(),
        "native_token": "ETH",
        "transaction_count": wallet_data.total_transactions,
        "risk_score": {
            "total": risk_score.total_score,
            "level": risk_score.risk_level,
            "details": {
                "wallet_age": risk_score.wallet_age_score,
                "scam_interaction": risk_score.scam_interaction_score,
            }
        },
        "timestamp": str(datetime.now())
    }


async def _analyze_solana(address: str, chain_info: Dict) -> Dict:
    """Analysiert Solana-Wallet"""
    client = SolanaClient()

    # Lade Daten
    wallet_data = client.get_wallet_data(address)

    # Risiko-Analyse
    risk = client.calculate_risk_score(wallet_data)

    return {
        "chain": "solana",
        "chain_info": chain_info,
        "address": address,
        "balance": wallet_data["balance"],
        "native_token": "SOL",
        "transaction_count": wallet_data["transaction_count"],
        "risk_score": {
            "total": risk["total_score"],
            "level": risk["risk_level"],
            "factors": risk["factors"]
        },
        "timestamp": str(datetime.now())
    }


def _analyze_bitcoin(address: str, chain_info: Dict) -> Dict:
    """Analysiert Bitcoin-Wallet (Placeholder)"""
    return {
        "chain": "bitcoin",
        "chain_info": chain_info,
        "address": address,
        "balance": 0,  # TODO: Bitcoin-API Integration
        "native_token": "BTC",
        "transaction_count": 0,
        "risk_score": {
            "total": 50,
            "level": "medium",
            "message": "Bitcoin-Analyse noch nicht vollständig implementiert"
        },
        "timestamp": str(datetime.now())
    }


# ============================================================================
# HELPER FUNCTIONS - Usage Tracking
# ============================================================================

def _reset_usage_if_needed(user: User, db: Session) -> None:
    """
    Reset usage count if it's a new day.

    Checks if usage_reset_at is in the past and resets counter.
    Usage resets at midnight UTC.

    Args:
        user: User object
        db: Database session
    """
    now = datetime.utcnow()

    # If no reset time set or reset time is in the past
    if not user.usage_reset_at or user.usage_reset_at <= now:
        # Reset counter
        user.usage_count = 0

        # Set next reset to tomorrow midnight UTC
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        user.usage_reset_at = tomorrow

        db.commit()

        logger.info(f"Usage reset for {user.email}. Next reset: {tomorrow}")
