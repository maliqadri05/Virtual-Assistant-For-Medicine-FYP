"""
Database configuration and setup

Handles PostgreSQL connection pooling, session management, and base model setup.
"""

import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://medai:medai_secure_password_123@localhost:5432/medai_db"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connection before using
    echo=False
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session
    
    Usage in endpoints:
    @router.get("/example")
    async def example(db: Session = Depends(get_db)):
        ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
