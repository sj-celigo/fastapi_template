import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


# Test database URL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a clean database session for a test.
    
    Returns:
        Session: SQLAlchemy session.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a connection and session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
    # Drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with the test database.
    
    Args:
        db: SQLAlchemy session.
        
    Returns:
        TestClient: FastAPI test client.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Override the dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
        
    # Reset the dependency overrides
    app.dependency_overrides = {} 