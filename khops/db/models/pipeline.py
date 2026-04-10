"""Pipeline Database Model"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, func
from sqlalchemy.orm import relationship
from datetime import datetime
from khops.db.base import Base


class Pipeline(Base):
    """Pipeline model - represents an ML workflow"""
    
    __tablename__ = "pipelines"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    definition = Column(JSON, nullable=False)  # Pipeline YAML as JSON
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    runs = relationship("Run", back_populates="pipeline", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Pipeline(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "definition": self.definition,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
