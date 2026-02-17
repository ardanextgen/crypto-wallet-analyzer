# ============================================================================
# DATABASE.PY - Database Connection & Session Management
# ============================================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL (SQLite für Development, später PostgreSQL für Production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cryptoguard.db")

# SQLAlchemy Engine
# check_same_thread=False nur für SQLite nötig (erlaubt multi-threading)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session Factory
# Erstellt neue Database Sessions für jede API-Request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Class für alle Models
Base = declarative_base()


# ============================================================================
# DEPENDENCY - Holt Database Session für FastAPI Endpoints
# ============================================================================
def get_db():
    """
    Dependency-Funktion für FastAPI.

    Erstellt eine neue Database Session für jeden Request
    und schließt sie automatisch nach Verwendung.

    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# INIT DATABASE - Erstellt alle Tabellen
# ============================================================================
def init_db():
    """
    Erstellt alle Datenbank-Tabellen.

    Muss beim Start der App aufgerufen werden.
    """
    from .models import User  # Import hier um circular imports zu vermeiden
    Base.metadata.create_all(bind=engine)
