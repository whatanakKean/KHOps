"""Model Registry Database Model"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from khops.db.base import Base


class Model(Base):
    """Model model - represents a registered ML model"""

    __tablename__ = "models"
    __table_args__ = (
        UniqueConstraint("project_id", "name", "version", name="uq_model_project_name_version"),
        UniqueConstraint("pipeline_id", "name", "version", name="uq_model_pipeline_name_version"),
    )

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    stage = Column(
        String(50), default="dev", nullable=False, index=True
    )  # dev, staging, production
    api_port = Column(Integer, nullable=True)
    path = Column(String(500), nullable=True)  # Storage path
    framework = Column(String(100), nullable=True)  # Framework (sklearn, tensorflow, pytorch, etc.)
    metrics = Column(JSON, nullable=True)  # Model metrics as JSON
    meta = Column(JSON, nullable=True)  # Additional metadata
    tags = Column(JSON, nullable=True)  # Model tags for categorization
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship("Project", back_populates="models")
    pipeline = relationship("Pipeline", back_populates="models")
    run = relationship("Run", back_populates="models")
    promotions = relationship(
        "ModelPromotion", back_populates="model", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Model(id={self.id}, name='{self.name}', version='{self.version}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "version": self.version,
            "stage": self.stage,
            "api_port": self.api_port,
            "path": self.path,
            "framework": self.framework,
            "metrics": self.metrics,
            "meta": self.meta,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
