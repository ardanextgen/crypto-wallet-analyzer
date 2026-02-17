# ============================================================================
# AUTH_ROUTES.PY - Authentication Endpoints
# ============================================================================
#
# Endpoints:
#   POST /api/auth/signup       - User registrieren
#   POST /api/auth/login        - User login
#   POST /api/auth/logout       - User logout (Client-seitig)
#   GET  /api/auth/me           - Current User Info
#   PUT  /api/auth/update       - Update User Info
#
# ============================================================================

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional

from ..database.database import get_db
from ..database.models import User
from ..utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SignupRequest(BaseModel):
    """Request für User-Registrierung"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Mindestens 8 Zeichen")


class LoginRequest(BaseModel):
    """Request für Login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response mit User-Daten (ohne password!)"""
    id: str
    email: str
    created_at: Optional[datetime]
    subscription_status: str
    usage_count: int
    is_active: bool
    is_verified: bool


class TokenResponse(BaseModel):
    """Response mit Access Token"""
    access_token: str
    token_type: str
    user: UserResponse


class UpdateUserRequest(BaseModel):
    """Request für User-Update"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


# ============================================================================
# SIGNUP - User Registrierung
# ============================================================================

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Registriert neuen User.

    Flow:
    1. Prüfe ob Email bereits existiert
    2. Hash Passwort
    3. Erstelle User in DB
    4. Generiere JWT Token
    5. Return Token + User Info

    Args:
        request: SignupRequest mit email & password
        db: Database Session

    Returns:
        Access Token + User Info

    Raises:
        400 wenn Email bereits existiert
    """
    # Prüfe ob Email bereits existiert
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash Passwort
    password_hash = get_password_hash(request.password)

    # Erstelle User
    new_user = User(
        email=request.email,
        password_hash=password_hash,
        subscription_status="free",
        usage_count=0,
        usage_reset_at=datetime.utcnow(),
        is_active=True,
        is_verified=False  # TODO: Email-Verifizierung implementieren
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")

    # Generiere Access Token
    access_token = create_access_token(
        data={"sub": new_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**new_user.to_dict())
    )


# ============================================================================
# LOGIN - User Authentication
# ============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login mit Email + Passwort.

    Args:
        request: LoginRequest mit email & password
        db: Database Session

    Returns:
        Access Token + User Info

    Raises:
        401 wenn Credentials falsch
    """
    # Authentifiziere User
    user = authenticate_user(db, request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last_login_at
    user.last_login_at = datetime.utcnow()
    db.commit()

    logger.info(f"User logged in: {user.email}")

    # Generiere Access Token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user.to_dict())
    )


# ============================================================================
# LOGIN (OAuth2 Form) - Für Swagger Docs
# ============================================================================

@router.post("/token", response_model=TokenResponse)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2-kompatibler Login Endpoint.

    Verwendet für:
    - Swagger UI "Authorize" Button
    - OAuth2 Password Flow

    Args:
        form_data: username (=email) & password
        db: Database Session

    Returns:
        Access Token
    """
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user.to_dict())
    )


# ============================================================================
# GET CURRENT USER - Holt User-Infos
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Holt Informationen über den aktuell eingeloggten User.

    Benötigt:
    - Authorization Header: Bearer <token>

    Returns:
        User-Informationen
    """
    return UserResponse(**current_user.to_dict())


# ============================================================================
# UPDATE USER - Ändert User-Daten
# ============================================================================

@router.put("/update", response_model=UserResponse)
async def update_user(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aktualisiert User-Daten.

    Kann ändern:
    - Email
    - Passwort

    Args:
        request: UpdateUserRequest
        current_user: Aktueller User
        db: Database Session

    Returns:
        Aktualisierte User-Daten
    """
    # Update Email (wenn angegeben)
    if request.email:
        # Prüfe ob Email bereits existiert
        existing = db.query(User).filter(
            User.email == request.email,
            User.id != current_user.id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

        current_user.email = request.email

    # Update Passwort (wenn angegeben)
    if request.password:
        current_user.password_hash = get_password_hash(request.password)

    db.commit()
    db.refresh(current_user)

    logger.info(f"User updated: {current_user.email}")

    return UserResponse(**current_user.to_dict())


# ============================================================================
# LOGOUT - Client-seitiges Logout
# ============================================================================

@router.post("/logout")
async def logout():
    """
    Logout Endpoint (Client-seitig).

    Da wir JWT verwenden (stateless), gibt es kein echtes Server-side Logout.
    Der Client muss einfach den Token löschen.

    Diese Endpoint existiert nur für API-Konsistenz.

    Returns:
        Success Message
    """
    return {"message": "Logged out successfully"}


# ============================================================================
# DELETE ACCOUNT - Löscht User-Account
# ============================================================================

@router.delete("/delete-account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Löscht User-Account (DSGVO Art. 17 - Recht auf Löschung).

    WARNUNG: Diese Aktion kann nicht rückgängig gemacht werden!

    Args:
        current_user: Aktueller User
        db: Database Session

    Returns:
        Success Message
    """
    logger.warning(f"Deleting user account: {current_user.email}")

    db.delete(current_user)
    db.commit()

    return {"message": "Account deleted successfully"}
