"""Model Registry Database Model"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, func, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from khops.db.base import Base


class Model(Base):
    """Model model - represents a registered ML model"""

    __tablename__ = "models"

    __table_args__ = (UniqueConstraint("name", "version", name="uq_model_name_version"),)

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    stage = Column(
        String(50), default="dev", nullable=False, index=True
    )  # dev, staging, production
    path = Column(String(500), nullable=True)  # Storage path
    framework = Column(String(100), nullable=True)  # Framework (sklearn, tensorflow, pytorch, etc.)
    metrics = Column(JSON, nullable=True)  # Model metrics as JSON
    meta = Column(JSON, nullable=True)  # Additional metadata
    tags = Column(JSON, nullable=True)  # Model tags for categorization
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    promotions = relationship(
        "ModelPromotion", back_populates="model", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Model(id={self.id}, name='{self.name}', version='{self.version}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "stage": self.stage,
            "path": self.path,
            "metrics": self.metrics,
            "meta": self.meta,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
