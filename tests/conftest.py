"""
Pytest configuration and fixtures for Issue Tracker API tests.

This module provides:
- Database test fixtures
- Test client setup
- Sample data creation
- Common test utilities
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User, Project, Issue, Comment, Attachment


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    
    Yields:
        Session: SQLAlchemy database session
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create test client with database dependency override.
    
    Args:
        db_session: Database session fixture
        
    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """
    Create a sample user for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        User: Sample user instance
    """
    user = User(
        email="test@example.com",
        password_hash="$2b$12$hashed_password",
        full_name="Test User",
        role="developer",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_project(db_session, sample_user):
    """
    Create a sample project for testing.
    
    Args:
        db_session: Database session fixture
        sample_user: Sample user fixture
        
    Returns:
        Project: Sample project instance
    """
    project = Project(
        name="Test Project",
        description="A test project",
        status="planning",
        owner_id=sample_user.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def sample_issue(db_session, sample_project, sample_user):
    """
    Create a sample issue for testing.
    
    Args:
        db_session: Database session fixture
        sample_project: Sample project fixture
        sample_user: Sample user fixture
        
    Returns:
        Issue: Sample issue instance
    """
    issue = Issue(
        title="Test Issue",
        description="A test issue",
        type="bug",
        status="open",
        priority="medium",
        project_id=sample_project.id,
        creator_id=sample_user.id,
        assignee_id=sample_user.id
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


@pytest.fixture
def temp_upload_dir():
    """
    Create temporary upload directory for file tests.
    
    Yields:
        str: Temporary directory path
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
