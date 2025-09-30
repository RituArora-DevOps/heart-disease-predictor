import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Assuming db_schema is in the same directory 
from .db_schema import Base 

# 1. Configuration (Reads from Environment)
# The default is for local development or a typical Docker Compose setup
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://user:password@db:5432/heartdb"
)

# 2. Engine and Session Creation
# PostgreSQL engine (pool_pre_ping is good practice for production connections)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Local session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Utility Functions

def create_db_tables():
    """Ensures all tables defined in Base.metadata exist in the database."""
    # This is run once on API startup
    Base.metadata.create_all(bind=engine) 

def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI routes. 
    It creates a new session and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        # Yields the session to the FastAPI route
        yield db
    finally:
        # Ensures the session is closed, regardless of success or failure
        db.close()