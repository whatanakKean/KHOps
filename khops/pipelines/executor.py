"""Pipeline execution engine."""

from __future__ import annotations

import json
import logging
import os
import pickle
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from khops.core.config import settings
from khops.pipelines.dag import DAG
from khops.pipelines.models import Node, NodeType, PipelineConfig

logger = logging.getLogger(__name__)


class PipelineExecutionError(Exception):
    """Raised when pipeline execution fails."""

    pass


class ExecutionContext:
    """Context object containing pipeline execution results."""

    def __init__(self, status: str, logs: str, meta: Dict[str, Any], context: Dict[str, Any]):
        self.status = status
        self.logs = logs
        self.meta = meta
        self.context = context

    def __repr__(self):
        return f"ExecutionContext(status='{self.status}', nodes_executed={self.meta.get('nodes_executed', 0)})"


class PipelineExecutor:
    """Execute validated pipeline configurations."""

    def __init__(self, config: PipelineConfig, run_id: Optional[int] = None):
        self.config = config
        self.dag = DAG(config)
        self.logs: list[str] = []
        self.context: dict[str, Any] = {}
        self.run_id = run_id
        self.artifact_dir = self._init_artifact_dir()

    def _init_artifact_dir(self) -> Path:
        base_artifact_dir = Path(settings.STORAGE_PATH or "./data/artifacts")
        run_name = (
            f"run_{self.run_id}"
            if self.run_id is not None
            else f"run_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )
        artifact_dir = base_artifact_dir / "runs" / run_name
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "data" / "raw").mkdir(parents=True, exist_ok=True)
        (artifact_dir / "data" / "preprocessed").mkdir(parents=True, exist_ok=True)
        (artifact_dir / "data" / "eda").mkdir(parents=True, exist_ok=True)
        (artifact_dir / "models").mkdir(parents=True, exist_ok=True)
        (artifact_dir / "evaluation").mkdir(parents=True, exist_ok=True)
        (artifact_dir / "logs").mkdir(parents=True, exist_ok=True)
        return artifact_dir

    def _save_dataframe(self, df: pd.DataFrame, filename: str, subdir: str) -> Path:
        file_path = self.artifact_dir / subdir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=False)
        return file_path

    def _save_json(self, data: Any, filename: str, subdir: str) -> Path:
        file_path = self.artifact_dir / subdir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        return file_path

    def _copy_raw_source(self, source: str, node_id: str) -> Optional[Path]:
        source_path = Path(source)
        if not source_path.exists():
            return None
        dest = (
            self.artifact_dir / "data" / "raw" / f"{source_path.stem}_{node_id}{source_path.suffix}"
        )
        shutil.copy2(source_path, dest)
        return dest

    def _generate_eda(self, df: pd.DataFrame) -> dict[str, Any]:
        preview = df.head(5).replace({pd.NA: None}).to_dict(orient="records")
        summary = df.describe(include="all").fillna("").to_dict()
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "preview": preview,
            "summary": summary,
        }

    def _gather_artifact_paths(self) -> list[str]:
        artifact_files: list[str] = []
        for root, _, files in os.walk(self.artifact_dir):
            for filename in files:
                artifact_files.append(
                    str(Path(root).joinpath(filename).relative_to(self.artifact_dir))
                )
        return artifact_files

    def _save_execution_logs(self) -> Path:
        file_path = self.artifact_dir / "logs" / "execution_logs.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs))
        return file_path

    def log(self, message: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        self.logs.append(f"{timestamp} - {message}")
        logger.info(message)

    def execute(self) -> Dict[str, Any]:
        self.log(f"Starting pipeline execution: {self.config.name}")
        execution_order = self.dag.get_execution_order()

        for level in execution_order:
            for node_id in level:
                node = self.config.get_node_by_id(node_id)
                self.log(f"Executing node {node.id} ({node.type})")
                try:
                    result = self._execute_node(node)
                    self.context[node.id] = result
                    self.log(f"Completed node {node.id}")
                except Exception as exc:
                    error_message = str(exc)
                    self.log(f"Failed node {node.id}: {error_message}")
                    raise PipelineExecutionError(error_message)

        self.log(f"Pipeline execution completed: {self.config.name}")
        summary = self._summarize_context()
        aggregated_metrics = self._aggregate_metrics(summary)

        self._save_json(summary, "run_summary.json", "")
        self._save_execution_logs()

        result = {
            "status": "success",
            "logs": "\n".join(self.logs),
            "meta": {
                "pipeline_name": self.config.name,
                "nodes_executed": len(self.context),
                "completed_at": datetime.utcnow().isoformat(),
                "metrics": aggregated_metrics,
                "artifact_dir": str(self.artifact_dir),
                "artifact_paths": self._gather_artifact_paths(),
            },
            "context": summary,
        }

        return ExecutionContext(**result)

    def _execute_node(self, node: Node) -> Dict[str, Any]:
        if node.type == NodeType.DATA:
            return self._run_data_node(node)
        if node.type == NodeType.TRAINING:
            return self._run_training_node(node)
        if node.type == NodeType.EVALUATION:
            return self._run_evaluation_node(node)

        raise PipelineExecutionError(f"Unsupported node type: {node.type}")

    def _run_data_node(self, node: Node) -> Dict[str, Any]:
        params = node.params
        source = params.get("source")
        operations = params.get("operations", []) or []
        df = pd.DataFrame()

        if source:
            source_path = Path(source)
            if source_path.exists():
                self.log(f"Loading data from source: {source}")
                if source_path.suffix.lower() == ".csv":
                    df = pd.read_csv(source_path)
                elif source_path.suffix.lower() in {".json", ".ndjson"}:
                    df = pd.read_json(source_path)
                else:
                    raise PipelineExecutionError(
                        f"Unsupported data source type: {source_path.suffix}"
                    )
            else:
                self.log(f"Source file not found: {source}. Trying upstream data if available.")
                df = self._get_parent_dataframe(node.id) or pd.DataFrame()
        else:
            df = self._get_parent_dataframe(node.id)
            if df is not None:
                self.log(f"Loaded upstream data for node {node.id}")
            else:
                self.log("No source provided for data node; using empty dataset.")
                df = pd.DataFrame()

        raw_data_path = None
        if source:
            raw_data_path = self._copy_raw_source(source, node.id)
            if raw_data_path:
                self.log(f"Saved raw data artifact for node {node.id}: {raw_data_path}")

        for operation in operations:
            if operation == "drop_nulls":
                df = df.dropna()
                self.log("Applied operation: drop_nulls")
            elif operation == "normalize":
                numeric_columns = df.select_dtypes(include=["number"]).columns
                for column in numeric_columns:
                    values = df[column].astype(float)
                    if values.max() != values.min():
                        df[column] = (values - values.min()) / (values.max() - values.min())
                self.log("Applied operation: normalize")
            elif operation == "encode":
                df = pd.get_dummies(df)
                self.log("Applied operation: encode")
            elif operation == "fill_missing":
                df = df.fillna(0)
                self.log("Applied operation: fill_missing")
            else:
                self.log(f"Unknown data operation '{operation}' ignored")

        preprocessed_path = None
        eda_path = None
        if not df.empty:
            preprocessed_path = self._save_dataframe(
                df, f"{node.id}_preprocessed.csv", "data/preprocessed"
            )
            self.log(f"Saved preprocessed data artifact for node {node.id}: {preprocessed_path}")
            eda = self._generate_eda(df)
            eda_path = self._save_json(eda, f"{node.id}_eda.json", "data/eda")
            self.log(f"Saved EDA artifact for node {node.id}: {eda_path}")

        return {
            "dataframe": df,
            "row_count": len(df),
            "columns": df.columns.tolist(),
            "raw_data_path": str(raw_data_path) if raw_data_path else None,
            "preprocessed_data_path": str(preprocessed_path) if preprocessed_path else None,
            "eda_path": str(eda_path) if eda_path else None,
        }

    def _run_training_node(self, node: Node) -> Dict[str, Any]:
        params = node.params
        dataframe = self._get_parent_dataframe(node.id)
        algorithm = str(params.get("algorithm", "random_forest")).lower()
        target = params.get("target")

        if dataframe is None or dataframe.empty:
            self.log("No valid training data found. Skipping training node.")
            return {"trained": False, "algorithm": algorithm}

        if not target or target not in dataframe.columns:
            self.log(
                "Training target not supplied or not found in the dataset. Skipping model fit."
            )
            return {"trained": False, "algorithm": algorithm, "row_count": len(dataframe)}

        X = dataframe.drop(columns=[target])
        y = dataframe[target]

        if X.empty:
            self.log("Training dataset has no features after removing target. Skipping training.")
            return {"trained": False, "algorithm": algorithm, "row_count": len(dataframe)}

        model = self._build_model(algorithm, y)
        if model is None:
            self.log(f"Unsupported algorithm '{algorithm}'. Skipping training.")
            return {"trained": False, "algorithm": algorithm}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        model.fit(X_train, y_train)
        self.log(f"Model trained with algorithm: {algorithm}")

        predictions = model.predict(X_test)
        metrics = self._compute_metrics(y_test, predictions, target)
        model_path = self._save_model(model, algorithm)
        metrics_path = self._save_json(metrics, f"{node.id}_training_metrics.json", "evaluation")
        self.log(f"Saved training metrics artifact for node {node.id}: {metrics_path}")

        return {
            "trained": True,
            "algorithm": algorithm,
            "model_path": str(model_path),
            "metrics": metrics,
            "metrics_path": str(metrics_path),
            "row_count": len(dataframe),
        }

    def _run_evaluation_node(self, node: Node) -> Dict[str, Any]:
        params = node.params
        dataframe = self._get_parent_dataframe(node.id)
        if dataframe is None or dataframe.empty:
            self.log("No data found for evaluation. Skipping evaluation node.")
            return {"evaluated": False}

        target = params.get("target")
        metrics_requested = params.get("metrics", []) or []
        model_output = self._get_parent_model_output(node.id)

        if target and target not in dataframe.columns:
            self.log(
                f"Evaluation target '{target}' not found in the dataset. Skipping metric computation."
            )
            return {"evaluated": False, "metrics": {}}

        if not target:
            self.log("No target supplied for evaluation. Skipping metric computation.")
            return {"evaluated": False, "metrics": {}}

        if model_output is None or not model_output.get("trained"):
            self.log("No trained model available for evaluation. Returning baseline metrics.")
            return {"evaluated": False, "metrics": {}}

        model_path = model_output.get("model_path")
        if not model_path:
            self.log("No model path available for evaluation. Skipping evaluation.")
            return {"evaluated": False, "metrics": {}}

        try:
            model = self._load_model(Path(model_path))
        except Exception as exc:
            self.log(f"Failed to load model for evaluation: {exc}")
            return {"evaluated": False, "metrics": {}}

        X = dataframe.drop(columns=[target])
        y_true = dataframe[target]

        if X.empty or y_true.empty:
            self.log("Evaluation dataset is empty. Skipping evaluation.")
            return {"evaluated": False, "metrics": {}}

        predictions = model.predict(X)
        metrics = self._compute_metrics(y_true, predictions, target, metrics_requested)
        self.log("Evaluation metrics computed.")
        evaluation_path = self._save_json(
            metrics, f"{node.id}_evaluation_metrics.json", "evaluation"
        )
        self.log(f"Saved evaluation artifact for node {node.id}: {evaluation_path}")

        return {
            "evaluated": True,
            "metrics": metrics,
            "target": target,
            "metric_names": metrics_requested,
            "evaluation_path": str(evaluation_path),
        }

    def _get_parent_dataframe(self, node_id: str) -> Optional[pd.DataFrame]:
        predecessors = self.config.get_predecessors(node_id)
        frames = []
        for predecessor in predecessors:
            output = self.context.get(predecessor, {})
            if isinstance(output, dict) and output.get("dataframe") is not None:
                frames.append(output["dataframe"])

        if not frames:
            # Fallback: use any available dataframe from the entire execution context
            for output in self.context.values():
                if isinstance(output, dict) and output.get("dataframe") is not None:
                    frames.append(output["dataframe"])

        if not frames:
            return None

        try:
            return pd.concat(frames, ignore_index=True)
        except ValueError:
            return frames[0]

    def _get_parent_model_output(self, node_id: str) -> Optional[Dict[str, Any]]:
        predecessors = self.config.get_predecessors(node_id)
        for predecessor in predecessors:
            output = self.context.get(predecessor)
            if isinstance(output, dict) and output.get("trained"):
                return output
        for output in self.context.values():
            if isinstance(output, dict) and output.get("trained"):
                return output
        return None

    def _build_model(self, algorithm: str, y: pd.Series):
        regression_algorithms = {
            "linear_regression",
            "linear",
            "random_forest_regressor",
            "rf_reg",
            "rf",
        }
        classification_algorithms = {
            "logistic_regression",
            "logistic",
            "random_forest",
            "rf",
            "decision_tree",
            "dt",
        }

        if algorithm in classification_algorithms:
            return (
                RandomForestClassifier(random_state=42)
                if algorithm in {"random_forest", "rf"}
                else LogisticRegression(max_iter=500)
            )
        if algorithm in regression_algorithms:
            return (
                RandomForestRegressor(random_state=42)
                if algorithm in {"random_forest_regressor", "rf_reg"}
                else LinearRegression()
            )

        return None

    def _compute_metrics(
        self,
        y_true: pd.Series,
        y_pred: Any,
        target: str,
        requested_metrics: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        requested_metrics = requested_metrics or []
        is_classification = y_true.dtype == object or y_true.nunique() <= 10
        metrics = {}

        if not requested_metrics:
            requested_metrics = ["accuracy"] if is_classification else ["mse"]

        for metric in requested_metrics:
            key = metric.lower()
            if key == "accuracy" and is_classification:
                metrics[key] = float(accuracy_score(y_true, y_pred))
            elif key == "precision" and is_classification:
                metrics[key] = float(
                    precision_score(y_true, y_pred, average="macro", zero_division=0)
                )
            elif key == "recall" and is_classification:
                metrics[key] = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
            elif key == "mse":
                metrics[key] = float(mean_squared_error(y_true, y_pred))
            elif key == "r2":
                metrics[key] = float(r2_score(y_true, y_pred))
            else:
                metrics[key] = None

        return metrics

    def _save_model(self, model: Any, algorithm: str) -> Path:
        model_dir = self.artifact_dir / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = (
            model_dir
            / f"{self.config.name}_{algorithm}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pkl"
        )
        with open(model_path, "wb") as model_file:
            pickle.dump(model, model_file)
        model_path = model_path.resolve()
        self.log(f"Saved model to {model_path}")
        return model_path

    def _load_model(self, path: Path):
        with open(path, "rb") as model_file:
            return pickle.load(model_file)

    def _summarize_context(self) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        for node_id, node_output in self.context.items():
            if isinstance(node_output, dict):
                summary[node_id] = {
                    "trained": node_output.get("trained", False),
                    "row_count": node_output.get("row_count"),
                    "columns": node_output.get("columns"),
                    "metrics": node_output.get("metrics"),
                }
        return summary

    def _aggregate_metrics(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        aggregated: Dict[str, Any] = {}
        for node_data in summary.values():
            metrics = node_data.get("metrics")
            if isinstance(metrics, dict):
                for name, value in metrics.items():
                    if value is None:
                        continue
                    if name not in aggregated:
                        aggregated[name] = value
                    elif isinstance(value, (int, float)) and isinstance(
                        aggregated[name], (int, float)
                    ):
                        # For now keep the latest metric value if there are duplicates
                        aggregated[name] = value
        return aggregated
