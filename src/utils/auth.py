# ============================================================================
# AUTH.PY - Authentication Utilities
# ============================================================================
#
# Funktionen:
# - create_access_token()    - JWT Token erstellen
# - verify_password()        - Passwort validieren
# - get_password_hash()      - Passwort hashen
# - get_current_user()       - User aus JWT Token holen
#
# ============================================================================

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..database.models import User

# ============================================================================
# KONFIGURATION
# ============================================================================

# Secret Key für JWT (in Production: starker Random-Key aus .env!)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 Tage

# Password Hashing Context (bcrypt)
# Truncate_error=False to handle bcrypt's 72-byte limitation automatically
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False
)

# OAuth2 Schema (für FastAPI Swagger Docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vergleicht Plain-Text Passwort mit gehashtem Passwort.

    Args:
        plain_password: User-Eingabe
        hashed_password: Gespeicherter Hash aus DB

    Returns:
        True wenn Passwort korrekt
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hasht ein Passwort mit bcrypt.

    Args:
        password: Plain-Text Passwort

    Returns:
        Bcrypt Hash

    Note: Bcrypt has a 72-byte limitation, so we truncate long passwords
    """
    # Truncate to 72 bytes (bcrypt limitation)
    if len(password) > 72:
        password = password[:72]

    return pwd_context.hash(password)


# ============================================================================
# JWT TOKEN HANDLING
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Erstellt einen JWT Access Token.

    Args:
        data: Payload (z.B. {"sub": user_email})
        expires_delta: Optional custom expiry time

    Returns:
        JWT Token String
    """
    to_encode = data.copy()

    # Expiry Time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Token encodieren
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Dekodiert JWT Token und gibt User-Email zurück.

    Args:
        token: JWT Token

    Returns:
        User-Email oder None bei Fehler
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Holt den aktuellen User aus dem JWT Token.

    Dependency für protected Routes:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}

    Args:
        token: JWT Token aus Authorization Header
        db: Database Session

    Returns:
        User-Objekt

    Raises:
        HTTPException 401 wenn Token ungültig
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Token dekodieren
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    # User aus DB holen
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Zusätzlicher Check: User muss aktiv sein.

    Usage:
        @app.get("/me")
        def read_users_me(current_user: User = Depends(get_current_active_user)):
            return current_user
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authentifiziert User mit Email + Passwort.

    Args:
        db: Database Session
        email: User Email
        password: Plain-Text Passwort

    Returns:
        User-Objekt wenn Login erfolgreich, sonst None
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
