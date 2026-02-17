# ============================================================================
# SERVER.PY - FastAPI REST API Server
# ============================================================================
#
# Was macht dieser Server?
# - Stellt HTTP-API bereit für Wallet-Analysen
# - Automatische Swagger-Dokumentation
# - Error-Handling und Validierung
# - JSON-Responses
#
# Endpoints:
#   GET  /               - API Info
#   GET  /health         - Health Check
#   GET  /analyze/{address}  - Analysiere Wallet
#   POST /batch-analyze  - Mehrere Wallets gleichzeitig
#
# Starten:
#   uvicorn src.api.server:app --reload --port 8000
#
# Swagger Docs:
#   http://localhost:8000/docs
# ============================================================================

import os
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
import logging
import bcrypt
from jose import jwt  # Using python-jose instead of PyJWT
import uuid

# Unsere Module
from ..blockchain.web3_client import Web3Client
from ..blockchain.etherscan_client import EtherscanClient
from ..analysis.risk_engine import RiskEngine
from ..ai.report_generator import AIReportGenerator
from ..blockchain.data_models import CompleteAnalysis
from .multichain_endpoint import analyze_multichain_wallet
from .stripe_routes import router as stripe_router
from .auth_routes import router as auth_router
from ..database.database import get_db
from ..database.models import User

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# FASTAPI APP INITIALISIERUNG
# ============================================================================
app = FastAPI(
    title="🔍 Krypto-Wallet-Analyse-API",
    description="""
    REST API für Ethereum-Wallet-Analyse und Scam-Risiko-Bewertung.

    ## Features
    * 📊 Vollständige Wallet-Analyse (Balance, Transaktionen, Tokens)
    * 🎯 6 Risiko-Heuristiken
    * 🤖 AI-generierte Reports (Claude)
    * 📝 Batch-Analyse für mehrere Wallets

    ## Verwendung
    1. Einzelne Wallet: `GET /analyze/{address}`
    2. Mehrere Wallets: `POST /batch-analyze`
    3. Health Check: `GET /health`

    ## Rate Limits
    - Etherscan: 5 Requests/Sekunde
    - Claude AI: Abhängig von API-Key-Tier

    ## Kosten
    - Etherscan: Kostenlos (bis 100k Requests/Tag)
    - Claude AI: ~$0.003 pro Report (Haiku)
    """,
    version="0.1.0",
    contact={
        "name": "Krypto-Wallet-Analyzer",
        "url": "https://github.com/yourusername/crypto-wallet-analyzer",
    },
    license_info={
        "name": "MIT",
    }
)

# ============================================================================
# CORS MIDDLEWARE (für Browser-Zugriff)
# ============================================================================
# Cross-Origin Resource Sharing ermöglichen
# Wichtig wenn API von Webseite aus aufgerufen wird
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Production: Spezifische Origins erlauben
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ROUTES INTEGRATION
# ============================================================================
# Integriere Stripe Payment Endpoints
app.include_router(stripe_router)

# Integriere Authentication Endpoints
try:
    app.include_router(auth_router)
except Exception as e:
    logger.warning(f"Auth router not available: {e}")


# ============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# ============================================================================
class AnalysisRequest(BaseModel):
    """Request-Schema für Wallet-Analyse"""
    address: str = Field(..., description="Ethereum Wallet-Adresse")
    generate_ai_report: bool = Field(
        default=True,
        description="AI-Report generieren? (kostet API-Credits)"
    )
    max_transactions: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximale Anzahl Transaktionen zum Analysieren"
    )


class BatchAnalysisRequest(BaseModel):
    """Request-Schema für Batch-Analyse"""
    addresses: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Liste von Wallet-Adressen (max 10)"
    )
    generate_ai_report: bool = Field(
        default=False,
        description="AI-Reports für alle generieren? (kann teuer werden!)"
    )


class HealthResponse(BaseModel):
    """Response-Schema für Health Check"""
    status: str
    timestamp: datetime
    version: str
    services: dict


# ============================================================================
# HELPER-FUNKTIONEN
# ============================================================================

async def get_optional_current_user(
    token: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Holt optional den aktuellen User aus dem JWT Token.

    Im Gegensatz zu get_current_user wirft dies keinen Error wenn kein Token vorhanden ist.
    Nützlich für Endpoints die sowohl für anonyme als auch authenticated Users funktionieren.

    Args:
        token: Optional JWT Token aus Authorization Header
        db: Database Session

    Returns:
        User-Objekt oder None
    """
    if not token:
        return None

    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        from ..utils.auth import decode_access_token

        email = decode_access_token(token)
        if not email:
            return None

        user = db.query(User).filter(User.email == email).first()
        return user if user and user.is_active else None

    except Exception:
        return None


def validate_ethereum_address(address: str) -> bool:
    """
    Validiert Ethereum-Adresse.

    Args:
        address: Zu prüfende Adresse

    Returns:
        True wenn gültig

    Raises:
        HTTPException wenn ungültig
    """
    if not address.startswith('0x'):
        raise HTTPException(
            status_code=400,
            detail="Adresse muss mit '0x' beginnen"
        )

    if len(address) != 42:
        raise HTTPException(
            status_code=400,
            detail=f"Adresse muss 42 Zeichen lang sein (ist: {len(address)})"
        )

    # Prüfe ob nur Hex-Zeichen
    try:
        int(address[2:], 16)  # Konvertiere zu int (wirft ValueError bei non-hex)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Adresse enthält ungültige Zeichen (nur 0-9, a-f erlaubt)"
        )

    return True


def perform_analysis(
    address: str,
    generate_ai: bool = True,
    max_transactions: int = 100
) -> CompleteAnalysis:
    """
    Führt Wallet-Analyse durch.

    Args:
        address: Wallet-Adresse
        generate_ai: AI-Report generieren?
        max_transactions: Max. Anzahl Transaktionen

    Returns:
        CompleteAnalysis-Objekt

    Raises:
        HTTPException bei Fehlern
    """
    try:
        # Validiere Adresse
        validate_ethereum_address(address)

        # Initialisiere Clients
        web3_client = Web3Client()
        etherscan_client = EtherscanClient()

        # Lade Wallet-Daten
        wallet_data = etherscan_client.get_complete_wallet_data(
            address,
            max_transactions=max_transactions
        )

        # ETH-Balance von Web3
        eth_balance = web3_client.get_eth_balance(address)
        wallet_data.eth_balance = eth_balance

        # Risiko-Analyse
        risk_engine = RiskEngine()
        risk_score = risk_engine.analyze(wallet_data)

        # AI-Report (optional)
        ai_report = None
        if generate_ai:
            try:
                ai_generator = AIReportGenerator()
                ai_report = ai_generator.generate_report(wallet_data, risk_score)
            except Exception as e:
                logger.warning(f"AI-Report fehlgeschlagen: {e}")
                # Weiter ohne AI-Report

        # Erstelle CompleteAnalysis
        analysis = CompleteAnalysis(
            wallet_data=wallet_data,
            risk_score=risk_score,
            ai_report=ai_report,
            analysis_timestamp=datetime.now()
        )

        return analysis

    except HTTPException:
        # Re-raise HTTP Exceptions
        raise

    except Exception as e:
        logger.error(f"Fehler bei Analyse: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analyse fehlgeschlagen: {str(e)}"
        )


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """
    API Root - Zeigt Informationen über die API.
    """
    return {
        "name": "CryptoGuard Multi-Chain Wallet Analyzer",
        "version": "0.2.0",
        "description": "REST API für Multi-Chain Wallet-Analyse und Scam-Risiko-Bewertung",
        "supported_chains": ["Ethereum", "BSC", "Polygon", "Solana", "Bitcoin"],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "analyze": "/analyze/{address}",  # Legacy Ethereum-only
            "analyze_multichain": "/analyze-multichain/{address}",  # NEW: Auto-detect chain
            "batch_analyze": "/batch-analyze"
        },
        "github": "https://github.com/yourusername/crypto-wallet-analyzer"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health Check - Prüft ob alle Services verfügbar sind.

    Prüft:
    - API läuft
    - Etherscan API Key vorhanden
    - Anthropic API Key vorhanden
    - Web3 Provider verfügbar
    """
    services = {}

    # Etherscan API Key
    etherscan_key = os.getenv("ETHERSCAN_API_KEY")
    services["etherscan"] = {
        "status": "ok" if etherscan_key else "missing_api_key",
        "available": bool(etherscan_key)
    }

    # Anthropic API Key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    services["anthropic"] = {
        "status": "ok" if anthropic_key else "missing_api_key",
        "available": bool(anthropic_key)
    }

    # Web3 Provider
    try:
        web3_client = Web3Client()
        services["web3"] = {
            "status": "ok",
            "available": True,
            "current_block": web3_client.get_current_block_number()
        }
    except Exception as e:
        services["web3"] = {
            "status": f"error: {str(e)}",
            "available": False
        }

    # Gesamt-Status
    all_ok = all(s.get("available", False) for s in services.values())

    return HealthResponse(
        status="healthy" if all_ok else "degraded",
        timestamp=datetime.now(),
        version="0.1.0",
        services=services
    )


@app.get("/analyze/{address}", response_model=CompleteAnalysis, tags=["Analysis"])
async def analyze_wallet(
    address: str,
    generate_ai: bool = Query(
        default=True,
        description="AI-Report generieren? (kostet API-Credits)"
    ),
    max_transactions: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Max. Anzahl Transaktionen"
    )
):
    """
    Analysiert eine einzelne Ethereum-Wallet.

    **Parameter:**
    - `address`: Ethereum-Adresse (0x...)
    - `generate_ai`: AI-Report generieren? (default: true)
    - `max_transactions`: Max. Anzahl Transaktionen (default: 100)

    **Returns:**
    - Vollständige Analyse mit Wallet-Daten, Risiko-Score und optional AI-Report

    **Beispiel:**
    ```
    GET /analyze/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045?generate_ai=true&max_transactions=50
    ```
    """
    logger.info(f"Analysiere Wallet: {address}")

    analysis = perform_analysis(
        address=address,
        generate_ai=generate_ai,
        max_transactions=max_transactions
    )

    return analysis


@app.get("/analyze-multichain/{address}", tags=["Analysis"])
async def analyze_multichain(
    address: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    🌐 **Multi-Chain Wallet-Analyse** - NEUE FUNKTION!

    Erkennt automatisch die Blockchain und analysiert die Wallet.

    **Usage Limits:**
    - 🆓 Free (unauthenticated): Unlimited (for now)
    - 🆓 Free (authenticated): 10 analyses per day
    - 💎 Pro: Unlimited analyses

    **Unterstützte Chains:**
    - ✅ Ethereum (0x...)
    - ✅ BSC / Binance Smart Chain (0x...)
    - ✅ Polygon (0x...)
    - ✅ Solana (Base58)
    - ✅ Bitcoin SegWit (bc1...)
    - ✅ Bitcoin Legacy (1...)
    - ✅ Bitcoin P2SH (3...)

    **Parameter:**
    - `address`: Wallet-Adresse (beliebige Chain)
    - `Authorization` (header, optional): Bearer token für authenticated users

    **Returns:**
    - Chain-Info
    - Balance
    - Risiko-Score (0-100)
    - Risiko-Level (low/medium/high)
    - Transaktionsanzahl
    - Risk-Faktoren

    **Beispiel:**
    ```
    GET /analyze-multichain/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045  # Ethereum
    GET /analyze-multichain/bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh  # Bitcoin
    GET /analyze-multichain/7EqDdP...  # Solana
    ```
    """
    logger.info(f"Multi-Chain Analyse: {address} (User: {current_user.email if current_user else 'anonymous'})")

    result = await analyze_multichain_wallet(address, current_user, db)
    return result


@app.post("/batch-analyze", tags=["Analysis"])
async def batch_analyze_wallets(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analysiert mehrere Wallets gleichzeitig.

    **WARNUNG:** Mit AI-Reports kann dies teuer werden!
    (10 Wallets × $0.003 = $0.03 pro Request)

    **Parameter:**
    - `addresses`: Liste von max. 10 Wallet-Adressen
    - `generate_ai_report`: AI-Reports generieren? (default: false)

    **Returns:**
    - Liste von Analysen

    **Beispiel:**
    ```json
    {
      "addresses": [
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
      ],
      "generate_ai_report": false
    }
    ```
    """
    logger.info(f"Batch-Analyse für {len(request.addresses)} Wallets")

    results = []

    for address in request.addresses:
        try:
            analysis = perform_analysis(
                address=address,
                generate_ai=request.generate_ai_report,
                max_transactions=100
            )
            results.append({
                "address": address,
                "status": "success",
                "analysis": analysis
            })

        except Exception as e:
            logger.error(f"Fehler bei {address}: {e}")
            results.append({
                "address": address,
                "status": "error",
                "error": str(e)
            })

    return {
        "total": len(request.addresses),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom Handler für HTTP Exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Custom Handler für allgemeine Exceptions"""
    logger.error(f"Unerwarteter Fehler: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Interner Server-Fehler",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# INLINE AUTH ENDPOINTS (Quick-Fix for deployment)
# ============================================================================

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/api/auth/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        password_hash=hash_password(request.password),
        subscription_status="free",
        usage_count=0,
        is_active=True,
        is_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    access_token = create_access_token({"sub": user.email, "user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create access token
    access_token = create_access_token({"sub": user.email, "user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@app.get("/api/auth/me")
async def get_current_user_info(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Get current user info from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user.to_dict()
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================================================
# STARTUP EVENT
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """
    Wird beim Start des Servers ausgeführt.
    Prüft Konfiguration und initialisiert Database.
    """
    logger.info("=" * 70)
    logger.info("🚀 Krypto-Wallet-Analyse-API startet...")
    logger.info("=" * 70)

    # Initialisiere Database
    try:
        from ..database.database import init_db
        init_db()
        logger.info("✅ Database initialisiert!")
    except Exception as e:
        logger.error(f"❌ Database-Fehler: {e}")

    # Prüfe API Keys
    etherscan_key = os.getenv("ETHERSCAN_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    stripe_key = os.getenv("STRIPE_SECRET_KEY")

    if not etherscan_key:
        logger.warning("⚠️  ETHERSCAN_API_KEY nicht gefunden - API-Limits aktiv!")

    if not anthropic_key:
        logger.warning("⚠️  ANTHROPIC_API_KEY nicht gefunden - AI-Reports deaktiviert!")

    if not stripe_key:
        logger.warning("⚠️  STRIPE_SECRET_KEY nicht gefunden - Payments deaktiviert!")

    logger.info("✅ API bereit!")
    logger.info("📖 Dokumentation: http://localhost:8000/docs")
    logger.info("🔐 Auth Endpoints: /api/auth/signup, /api/auth/login")
    logger.info("=" * 70)


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================
if __name__ == "__main__":
    import uvicorn

    # Server starten
    # In Production: uvicorn src.api.server:app --host 0.0.0.0 --port 8000
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,  # Auto-reload bei Code-Änderungen
        log_level="info"
    )
