"""Run Database Model"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from khops.db.base import Base


class Run(Base):
    """Run model - represents a pipeline execution"""
    
    __tablename__ = "runs"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, running, success, failed
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    logs = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="runs")
    metrics = relationship("Metrics", back_populates="run", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Run(id={self.id}, pipeline_id={self.pipeline_id}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "logs": self.logs,
            "meta": self.meta,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
