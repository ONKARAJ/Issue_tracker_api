"""
Database configuration and session management for Issue Tracker API.

This module provides:
- PostgreSQL database connection
- SQLAlchemy session management
- Connection pooling configuration
- Transaction handling utilities
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from typing import Generator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
# In production, use environment variables or secrets management
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:ICECREAM12@localhost:5432/issue_tracker"
)

# Create engine with optimized connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,          # Number of connections to maintain
    max_overflow=20,       # Additional connections when pool is full
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600,     # Recycle connections after 1 hour
    echo=False,            # Set to True for SQL logging in development
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def create_db_session() -> Session:
    """
    Create a new database session for manual management.
    
    Returns:
        Session: New SQLAlchemy session
        
    Note: Caller is responsible for closing the session
    """
    return SessionLocal()


class DatabaseTransaction:
    """
    Context manager for database transactions.
    
    Provides automatic commit/rollback handling for database operations.
    
    Example:
        with DatabaseTransaction() as db:
            user = User(name="John")
            db.add(user)
            # Transaction automatically commits on success
    """
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.should_close = session is None
    
    def __enter__(self) -> Session:
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            if self.should_close:
                self.session.close()


def check_database_connection() -> bool:
    """
    Test database connectivity.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception:
        return False
