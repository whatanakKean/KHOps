"""Metrics Database Model"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from khops.db.base import Base


class Metrics(Base):
    """Metrics model - stores performance metrics"""

    __tablename__ = "metrics"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    tags = Column(JSON, nullable=True)  # Additional metadata
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=True, index=True)

    # Relationships
    run = relationship("Run", back_populates="metrics")

    def __repr__(self):
        return f"<Metrics(id={self.id}, name='{self.name}', value={self.value})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tags": self.tags,
            "run_id": self.run_id,
        }
