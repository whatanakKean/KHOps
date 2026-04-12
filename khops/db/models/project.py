"""Project Database Model"""

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from khops.db.base import Base


class Project(Base):
    """Project model - groups pipelines and models."""

    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("name", name="uq_project_name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    pipelines = relationship(
        "Pipeline",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    models = relationship(
        "Model",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
