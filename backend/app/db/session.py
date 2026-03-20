"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Use in-memory SQLite for simplicity
engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# For async compatibility
async_session_factory = SessionLocal

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db_context():
    """Get async database session context."""
    async with async_session_factory() as session:
        yield session

def close_db():
    """Close database connections."""
    engine.dispose()

def init_db():
    """Initialize database."""
    from app.db.models.base import Base
    Base.metadata.create_all(bind=engine)

def create_tables():
    """Create all database tables."""
    init_db()
