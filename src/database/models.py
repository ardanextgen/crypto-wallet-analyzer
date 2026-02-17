# ============================================================================
# MODELS.PY - Database Models (User, etc.)
# ============================================================================

from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .database import Base


# ============================================================================
# USER MODEL
# ============================================================================
class User(Base):
    """
    User Model - Speichert alle User-Informationen.

    Fields:
        id: Eindeutige User ID (UUID)
        email: Email-Adresse (unique, für Login)
        password_hash: Gehashtes Passwort (bcrypt)
        created_at: Registrierungsdatum
        subscription_status: free/pro/enterprise
        stripe_customer_id: Stripe Customer ID (für Subscription-Tracking)
        usage_count: Anzahl Analysen heute
        usage_reset_at: Wann wird usage_count zurückgesetzt
        is_active: User-Account aktiv?
        api_key: Optional API Key (für programmatic access)
    """
    __tablename__ = "users"

    # Primärschlüssel - UUID für bessere Sicherheit
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Login-Credentials
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Subscription Info
    subscription_status = Column(
        String,
        default="free",
        nullable=False
    )  # free, pro, enterprise

    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    # Usage Tracking (für Free-Tier Limits)
    usage_count = Column(Integer, default=0)
    usage_reset_at = Column(DateTime(timezone=True), default=func.now())

    # Account Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email-Verifizierung (später)

    # Optional: API Key für programmatischen Zugriff
    api_key = Column(String, nullable=True, unique=True)

    def __repr__(self):
        return f"<User {self.email} ({self.subscription_status})>"

    def to_dict(self):
        """Konvertiert User zu Dictionary (ohne password_hash!)"""
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "subscription_status": self.subscription_status,
            "usage_count": self.usage_count,
            "usage_reset_at": self.usage_reset_at.isoformat() if self.usage_reset_at else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
        }
