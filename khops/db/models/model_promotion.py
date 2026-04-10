"""Model promotion history database model"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from khops.db.base import Base


class ModelPromotion(Base):
    """Stores model promotion audit history."""

    __tablename__ = "model_promotions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)
    from_stage = Column(String(50), nullable=False)
    to_stage = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    promoted_by = Column(String(100), nullable=True)
    previous_model_id = Column(Integer, nullable=True)
    promoted_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    model = relationship("Model", back_populates="promotions")

    def __repr__(self):
        return f"<ModelPromotion(id={self.id}, model_id={self.model_id}, from='{self.from_stage}', to='{self.to_stage}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "from_stage": self.from_stage,
            "to_stage": self.to_stage,
            "reason": self.reason,
            "promoted_by": self.promoted_by,
            "previous_model_id": self.previous_model_id,
            "promoted_at": self.promoted_at.isoformat() if self.promoted_at else None,
        }
