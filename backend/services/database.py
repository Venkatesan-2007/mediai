"""Database configuration and models for SQLAlchemy with SQLite (local development) or PostgreSQL (production)."""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional
import os
from pathlib import Path

# Database URL - uses SQLite for local development, PostgreSQL for production
# SQLite is perfect for local development - no setup required!
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./database/medi_ai.db"  # SQLite file-based database
)

# Use check_same_thread=False for SQLite (not needed for PostgreSQL)
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
else:
    # PostgreSQL connection
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    books = relationship("Book", back_populates="owner", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Book(Base):
    """Book/PDF model for storing uploaded documents."""
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    pdf_content = Column(LargeBinary, nullable=False)  # Store full PDF binary
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="books")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# NOTE: Chunk model removed - vectors now stored in ChromaDB instead of SQLAlchemy
# ChromaDB provides better performance for vector operations and large-scale embeddings


def init_db():
    """Initialize database tables."""
    # Create database directory if using SQLite
    if "sqlite" in DATABASE_URL:
        db_path = DATABASE_URL.replace("sqlite:///./", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session for dependency injection in FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
