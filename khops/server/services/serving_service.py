"""Model serving service for loading and scoring models."""

from pathlib import Path
import pickle
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
import pandas as pd
from khops.server.services.model_service import ModelService
from khops.db.models.model import Model


class ModelServingService:
    """Load registered models and run inference."""

    _model_cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, db: Session):
        self.db = db
        self.model_service = ModelService(db)

    async def get_model(
        self, name: str, version: Optional[str] = None, stage: Optional[str] = None
    ) -> Optional[Model]:
        if version:
            return self.db.query(Model).filter(Model.name == name, Model.version == version).first()

        query = self.db.query(Model).filter(Model.name == name)
        if stage:
            query = query.filter(Model.stage == stage)

        return query.order_by(Model.created_at.desc()).first()

    def load_model(self, model: Model) -> Any:
        if not model.path:
            raise ValueError("Model path is not set for this registered model")

        model_path = Path(model.path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model artifact not found: {model_path}")

        cache_key = str(model_path.resolve())
        file_mtime = model_path.stat().st_mtime
        cached = self._model_cache.get(cache_key)
        if cached and cached.get("mtime") == file_mtime:
            return cached["model"]

        with open(model_path, "rb") as f:
            loaded = pickle.load(f)

        self._model_cache[cache_key] = {
            "model": loaded,
            "mtime": file_mtime,
        }
        return loaded

    def get_model_metadata(self, model: Model) -> Dict[str, Any]:
        return {
            "model_name": model.name,
            "version": model.version,
            "stage": model.stage,
            "path": model.path,
            "metrics": model.metrics,
            "meta": model.meta,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

    def predict(self, model: Any, features: List[Dict[str, Any]]) -> List[Any]:
        if not hasattr(model, "predict"):
            raise ValueError("Loaded model does not support prediction")

        df = pd.DataFrame(features)
        if df.empty:
            return []

        predictions = model.predict(df)
        return predictions.tolist()
