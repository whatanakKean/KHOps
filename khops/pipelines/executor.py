"""Pipeline execution engine."""

from __future__ import annotations

import pickle
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    mean_squared_error,
    r2_score,
)

from khops.pipelines.dag import DAG
from khops.pipelines.models import PipelineConfig, NodeType
from khops.pipelines.models import Node
from khops.utils.artifacts import (
    build_experiment_metadata,
    build_model_artifact_metadata,
    get_data_artifact_dir,
    get_model_artifact_dir,
    save_data_profile,
    save_json_artifact,
)

logger = logging.getLogger(__name__)


class PipelineExecutionError(Exception):
    """Raised when pipeline execution fails."""

    pass


class PipelineExecutor:
    """Execute validated pipeline configurations."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.dag = DAG(config)
        self.logs: list[str] = []
        self.context: dict[str, Any] = {}

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
        experiment_meta = build_experiment_metadata(
            pipeline_name=self.config.name,
            pipeline_version=self.config.version,
            pipeline_definition=self.config.model_dump(),
            metrics=aggregated_metrics,
            artifact_lineage=self._collect_artifact_lineage(),
            parameters={
                node_id: node_output.get("params")
                for node_id, node_output in self.context.items()
                if isinstance(node_output, dict)
            },
        )

        experiment_meta["nodes_executed"] = len(self.context)
        experiment_meta["completed_at"] = datetime.utcnow().isoformat()

        return {
            "status": "success",
            "logs": "\n".join(self.logs),
            "meta": experiment_meta,
            "context": summary,
        }

    def _execute_node(self, node: Node) -> Dict[str, Any]:
        if node.type == NodeType.DATA:
            output = self._run_data_node(node)
        elif node.type == NodeType.TRAINING:
            output = self._run_training_node(node)
        elif node.type == NodeType.EVALUATION:
            output = self._run_evaluation_node(node)
        else:
            raise PipelineExecutionError(f"Unsupported node type: {node.type}")

        output["node_id"] = node.id
        output["node_type"] = node.type.value
        output["params"] = node.params or {}

        return output

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

        data_artifact_dir = get_data_artifact_dir(node.id)
        data_profile_files = save_data_profile(df, data_artifact_dir, filename=f"{node.id}_profile")

        return {
            "dataframe": df,
            "row_count": len(df),
            "columns": df.columns.tolist(),
            "artifact_dir": str(data_artifact_dir),
            "data_profile": {
                "csv": str(data_profile_files["csv"]),
                "json": str(data_profile_files["json"]),
                "html": str(data_profile_files["html"]) if data_profile_files["html"] else None,
            },
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

        artifact_dir = model_path.parent
        model_profile_path = save_json_artifact(
            {
                "algorithm": algorithm,
                "metrics": metrics,
                "row_count": len(dataframe),
                "saved_at": datetime.utcnow().isoformat(),
                "model_path": str(model_path),
            },
            artifact_dir / "model_profile.json",
        )

        artifact_metadata = build_model_artifact_metadata(
            model_path=model_path,
            data_profile_path=None,
            extra={
                "pipeline_name": self.config.name,
                "pipeline_version": self.config.version,
                "algorithm": algorithm,
                "saved_at": datetime.utcnow().isoformat(),
                "model_profile": str(model_profile_path),
            },
        )

        return {
            "trained": True,
            "algorithm": algorithm,
            "model_path": str(model_path),
            "metrics": metrics,
            "row_count": len(dataframe),
            "artifact_dir": str(artifact_dir),
            "model_profile": str(model_profile_path),
            "artifact_metadata": artifact_metadata,
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

        return {
            "evaluated": True,
            "metrics": metrics,
            "target": target,
            "metric_names": metrics_requested,
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
        artifact_dir = get_model_artifact_dir(
            self.config.name,
            datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        )
        model_path = (
            artifact_dir
            / f"{self.config.name}_{algorithm}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pkl"
        )
        with open(model_path, "wb") as model_file:
            pickle.dump(model, model_file)
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
                    "artifact_dir": node_output.get("artifact_dir"),
                    "model_path": node_output.get("model_path"),
                    "data_profile": node_output.get("data_profile"),
                    "params": node_output.get("params"),
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

    def _collect_artifact_lineage(self) -> list[Dict[str, Any]]:
        lineage: list[Dict[str, Any]] = []
        for node_id, node_output in self.context.items():
            if not isinstance(node_output, dict):
                continue

            artifact_entry: Dict[str, Any] = {
                "node_id": node_id,
                "node_type": node_output.get("node_type"),
                "artifact_dir": node_output.get("artifact_dir"),
                "model_path": node_output.get("model_path"),
                "data_profile": node_output.get("data_profile"),
                "metrics": node_output.get("metrics"),
                "params": node_output.get("params"),
            }

            if any(
                artifact_entry.get(key) for key in ["artifact_dir", "model_path", "data_profile"]
            ):
                lineage.append(artifact_entry)

        return lineage
