"""Pipeline Database Model"""

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


class Pipeline(Base):
    """Pipeline model - represents an ML workflow"""

    __tablename__ = "pipelines"
    __table_args__ = (
        UniqueConstraint("project_id", "name", "version", name="uq_pipeline_project_name_version"),
    )

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), default="1.0.0", nullable=False, index=True)
    description = Column(Text, nullable=True)
    definition = Column(JSON, nullable=False)  # Pipeline YAML as JSON
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="pipelines")
    runs = relationship("Run", back_populates="pipeline", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="pipeline", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pipeline(id={self.id}, name='{self.name}', version='{self.version}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "definition": self.definition,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
