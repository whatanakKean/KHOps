"""Training Pipeline Builder

High-level API for building ML training pipelines with sensible defaults.
Users can customize each step easily without needing to understand the full configuration.

Usage Example:
    builder = TrainingPipelineBuilder("my_classification_model")
    builder.load_data("data/train.csv", target="churn")
    builder.add_preprocessing(handle_outliers=True, feature_selection=True)
    builder.add_model("random_forest", n_estimators=100, max_depth=10)
    builder.add_model("xgboost", learning_rate=0.1)
    builder.set_evaluation("classification", primary_metric="f1")
    builder.set_ranking_top_k(5, method="weighted_score", weights={"f1": 0.6, "auc": 0.4})
    builder.enable_api_serving(port=8001)
    pipeline_config = builder.build()

    # Save to YAML for later use
    builder.save_to_yaml("pipelines/my_pipeline.yaml")
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import yaml

from .training_steps import (
    DEFAULT_MODELS,
    APIServingConfig,
    BatchServingConfig,
    ClassificationMetric,
    DataConfig,
    DataSourceType,
    EvaluationConfig,
    ModelConfig,
    ModelType,
    PreprocessingConfig,
    RankingConfig,
    RankingMethod,
    RegressionMetric,
    ServingConfig,
    ServingType,
    TrainingPipelineConfig,
    ValidationMethod,
    get_default_classification_pipeline,
    get_default_regression_pipeline,
    get_ensemble_pipeline,
)


class TrainingPipelineBuilder:
    """Builder for constructing training pipelines with fluent interface"""

    def __init__(self, name: str, description: str = ""):
        """
        Initialize the training pipeline builder.

        Args:
            name: Pipeline name
            description: Pipeline description
        """
        self.name = name
        self.description = description
        self._data_config: Optional[DataConfig] = None
        self._preprocessing_config = PreprocessingConfig()
        self._models: List[ModelConfig] = []
        self._evaluation_config: Optional[EvaluationConfig] = None
        self._ranking_config = RankingConfig()
        self._serving_config = ServingConfig()

    # ========================================================================
    # DATA CONFIGURATION
    # ========================================================================

    def load_data(
        self,
        source_path: str,
        target_column: str,
        source_type: Union[str, DataSourceType] = "csv",
        feature_columns: Optional[List[str]] = None,
        test_size: float = 0.2,
        validation_size: float = 0.1,
        stratified: bool = True,
        random_state: int = 42,
    ) -> "TrainingPipelineBuilder":
        """
        Configure data source and target variable.

        Args:
            source_path: Path or connection string to data
            target_column: Target variable name
            source_type: Data source type (csv, parquet, database, s3, api)
            feature_columns: List of features to use (all if None)
            test_size: Test set fraction
            validation_size: Validation set fraction
            stratified: Use stratified split for classification
            random_state: Random seed

        Returns:
            Self for method chaining
        """
        if isinstance(source_type, str):
            source_type = DataSourceType(source_type)

        self._data_config = DataConfig(
            source_type=source_type,
            source_path=source_path,
            target_column=target_column,
            feature_columns=feature_columns,
            test_size=test_size,
            validation_size=validation_size,
            stratified=stratified,
            random_state=random_state,
        )
        return self

    # ========================================================================
    # PREPROCESSING CONFIGURATION
    # ========================================================================

    def add_preprocessing(
        self,
        handle_missing: bool = True,
        missing_strategy: Literal["mean", "median", "mode", "drop"] = "mean",
        remove_duplicates: bool = True,
        handle_outliers: bool = False,
        outlier_method: Literal["iqr", "zscore", "isolation_forest"] = "iqr",
        encode_categorical: bool = True,
        encoding_method: Literal["onehot", "label", "target", "ordinal"] = "onehot",
        scale_features: bool = True,
        scaler_type: Literal["standard", "minmax", "robust", "none"] = "standard",
        feature_selection: bool = False,
        feature_selection_method: Literal["variance", "mutual_info", "correlation"] = "variance",
        n_features_to_select: Optional[int] = None,
    ) -> "TrainingPipelineBuilder":
        """
        Configure preprocessing steps.

        Args:
            handle_missing: Handle missing values
            missing_strategy: Strategy for missing values
            remove_duplicates: Remove duplicate rows
            handle_outliers: Detect and remove outliers
            outlier_method: Outlier detection method
            encode_categorical: Encode categorical variables
            encoding_method: Categorical encoding method
            scale_features: Normalize/scale numerical features
            scaler_type: Feature scaling method
            feature_selection: Select important features
            feature_selection_method: Feature selection method
            n_features_to_select: Target number of features

        Returns:
            Self for method chaining
        """
        self._preprocessing_config = PreprocessingConfig(
            handle_missing=handle_missing,
            missing_strategy=missing_strategy,
            remove_duplicates=remove_duplicates,
            handle_outliers=handle_outliers,
            outlier_method=outlier_method,
            encode_categorical=encode_categorical,
            encoding_method=encoding_method,
            scale_features=scale_features,
            scaler_type=scaler_type,
            feature_selection=feature_selection,
            feature_selection_method=feature_selection_method,
            n_features_to_select=n_features_to_select,
        )
        return self

    # ========================================================================
    # MODEL CONFIGURATION
    # ========================================================================

    def add_model(
        self, model_type: Union[str, ModelType], model_id: Optional[str] = None, **hyperparameters
    ) -> "TrainingPipelineBuilder":
        """
        Add a model to train.

        Args:
            model_type: Model type (e.g., 'random_forest', 'xgboost', 'lightgbm')
            model_id: Unique model identifier (auto-generated if None)
            **hyperparameters: Model-specific hyperparameters

        Returns:
            Self for method chaining

        Examples:
            builder.add_model("random_forest", n_estimators=100, max_depth=10)
            builder.add_model("xgboost", learning_rate=0.1, max_depth=6)
        """
        if isinstance(model_type, str):
            model_type = ModelType(model_type)

        model_id = model_id or f"{model_type.value}_{len(self._models) + 1}"

        model = ModelConfig(
            id=model_id,
            model_type=model_type,
            hyperparameters=hyperparameters,
        )
        self._models.append(model)
        return self

    def add_default_models(
        self,
        ensemble: bool = False,
    ) -> "TrainingPipelineBuilder":
        """
        Add recommended default models.

        Args:
            ensemble: If True, add more models for ensemble. If False, add top performers.

        Returns:
            Self for method chaining
        """
        if ensemble:
            self._models.extend(
                [
                    DEFAULT_MODELS["rf_default"],
                    DEFAULT_MODELS["xgb_default"],
                    DEFAULT_MODELS["lgb_default"],
                    DEFAULT_MODELS["cb_default"],
                ]
            )
        else:
            self._models.extend(
                [
                    DEFAULT_MODELS["rf_default"],
                    DEFAULT_MODELS["xgb_default"],
                ]
            )
        return self

    def clear_models(self) -> "TrainingPipelineBuilder":
        """Reset the models list"""
        self._models = []
        return self

    # ========================================================================
    # EVALUATION CONFIGURATION
    # ========================================================================

    def set_evaluation(
        self,
        task_type: Literal["classification", "regression"] = "classification",
        primary_metric: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        validation_method: Literal[
            "holdout", "k_fold", "stratified_k_fold", "time_series", "leave_one_out"
        ] = "k_fold",
        n_splits: int = 5,
        threshold_optimization: bool = False,
    ) -> "TrainingPipelineBuilder":
        """
        Configure evaluation metrics and validation strategy.

        Args:
            task_type: Machine learning task ('classification' or 'regression')
            primary_metric: Primary metric for model selection
            metrics: List of metrics to compute
            validation_method: Cross-validation method
            n_splits: Number of folds
            threshold_optimization: Optimize threshold (classification only)

        Returns:
            Self for method chaining
        """
        if task_type == "classification":
            if not metrics:
                metrics = ["accuracy", "f1", "auc_roc"]
            if not primary_metric:
                primary_metric = "f1"
            classification_metrics = [ClassificationMetric(m) for m in metrics]
            self._evaluation_config = EvaluationConfig(
                task_type="classification",
                classification_metrics=classification_metrics,
                validation_method=ValidationMethod(validation_method),
                n_splits=n_splits,
                primary_metric=primary_metric,
                threshold_optimization=threshold_optimization,
            )
        else:
            if not metrics:
                metrics = ["rmse", "mae", "r2"]
            if not primary_metric:
                primary_metric = "r2"
            regression_metrics = [RegressionMetric(m) for m in metrics]
            self._evaluation_config = EvaluationConfig(
                task_type="regression",
                regression_metrics=regression_metrics,
                validation_method=ValidationMethod(validation_method),
                n_splits=n_splits,
                primary_metric=primary_metric,
            )
        return self

    # ========================================================================
    # RANKING CONFIGURATION
    # ========================================================================

    def set_ranking_top_k(
        self,
        k: int = 1,
        method: Literal[
            "best_primary_metric", "weighted_score", "pareto_frontier", "ensemble"
        ] = "best_primary_metric",
        metric_weights: Optional[Dict[str, float]] = None,
        ensemble_method: Optional[Literal["voting", "stacking", "blending"]] = None,
        ensemble_voting_strategy: Literal["hard", "soft"] = "soft",
    ) -> "TrainingPipelineBuilder":
        """
        Configure model ranking and selection strategy.

        Args:
            k: Number of top models to select
            method: Ranking method
            metric_weights: Metric weights for weighted scoring
            ensemble_method: Ensemble method if using ensemble ranking
            ensemble_voting_strategy: Voting strategy

        Returns:
            Self for method chaining

        Examples:
            # Select best single model
            builder.set_ranking_top_k(1)

            # Select top 3 models by weighted score
            builder.set_ranking_top_k(
                k=3,
                method="weighted_score",
                metric_weights={"f1": 0.6, "auc_roc": 0.3, "speed": 0.1}
            )

            # Ensemble top 5 models
            builder.set_ranking_top_k(
                k=5,
                method="ensemble",
                ensemble_method="voting"
            )
        """
        self._ranking_config = RankingConfig(
            ranking_method=RankingMethod(method),
            metric_weights=metric_weights or {},
            select_top_k=k,
            ensemble_method=ensemble_method,
            ensemble_voting_strategy=ensemble_voting_strategy,
            save_top_k_models=k > 1,
        )
        return self

    # ========================================================================
    # SERVING CONFIGURATION
    # ========================================================================

    def enable_api_serving(
        self,
        port: int = 8001,
        max_workers: int = 4,
        request_timeout: int = 30,
        batch_prediction_timeout: int = 60,
    ) -> "TrainingPipelineBuilder":
        """
        Enable API serving for trained model.

        Args:
            port: API server port
            max_workers: Number of worker processes
            request_timeout: Individual request timeout
            batch_prediction_timeout: Batch prediction timeout

        Returns:
            Self for method chaining
        """
        self._serving_config.serving_type = ServingType.API
        self._serving_config.api = APIServingConfig(
            enabled=True,
            port=port,
            max_workers=max_workers,
            request_timeout=request_timeout,
            batch_prediction_timeout=batch_prediction_timeout,
        )
        return self

    def enable_batch_serving(
        self,
        schedule: str = "daily",
        input_format: Literal["csv", "parquet", "json"] = "csv",
        output_format: Literal["csv", "parquet", "json"] = "csv",
        max_batch_size: int = 10000,
    ) -> "TrainingPipelineBuilder":
        """
        Enable batch serving for trained model.

        Args:
            schedule: Batch schedule (e.g., 'daily', 'hourly')
            input_format: Input data format
            output_format: Output format
            max_batch_size: Maximum rows per batch

        Returns:
            Self for method chaining
        """
        self._serving_config.serving_type = ServingType.BATCH
        self._serving_config.batch = BatchServingConfig(
            enabled=True,
            schedule=schedule,
            input_format=input_format,
            output_format=output_format,
            max_batch_size=max_batch_size,
        )
        return self

    def enable_monitoring(self, enable: bool = True) -> "TrainingPipelineBuilder":
        """Enable/disable prediction monitoring"""
        self._serving_config.enable_monitoring = enable
        return self

    def enable_drift_detection(self, enable: bool = True) -> "TrainingPipelineBuilder":
        """Enable/disable data drift detection"""
        self._serving_config.enable_drift_detection = enable
        return self

    # ========================================================================
    # BUILD & PERSISTENCE
    # ========================================================================

    def build(self) -> TrainingPipelineConfig:
        """
        Build and return the training pipeline configuration.

        Returns:
            TrainingPipelineConfig: Complete pipeline configuration

        Raises:
            ValueError: If required configuration is missing
        """
        if not self._data_config:
            raise ValueError("Data configuration is required. Call load_data() first.")

        if not self._models:
            raise ValueError(
                "At least one model is required. Call add_model() or add_default_models()."
            )

        if not self._evaluation_config:
            # Default to classification if not set
            self.set_evaluation("classification")

        return TrainingPipelineConfig(
            name=self.name,
            description=self.description,
            data=self._data_config,
            preprocessing=self._preprocessing_config,
            models=self._models,
            evaluation=self._evaluation_config,
            ranking=self._ranking_config,
            serving=self._serving_config,
        )

    def save_to_yaml(self, output_path: Union[str, Path]) -> None:
        """
        Save pipeline configuration to YAML file.

        Args:
            output_path: Path to save YAML file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        pipeline_config = self.build()
        config_dict = pipeline_config.model_dump(exclude_none=True)

        with open(output_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

        print(f"✓ Pipeline saved to {output_path}")

    def save_to_json(self, output_path: Union[str, Path]) -> None:
        """
        Save pipeline configuration to JSON file.

        Args:
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        pipeline_config = self.build()
        config_dict = pipeline_config.model_dump(exclude_none=True)

        with open(output_path, "w") as f:
            json.dump(config_dict, f, indent=2)

        print(f"✓ Pipeline saved to {output_path}")

    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return self.build().model_dump(exclude_none=True)

    def to_json_str(self) -> str:
        """Get configuration as JSON string"""
        config = self.build()
        return config.model_dump_json(indent=2, exclude_none=True)


# ============================================================================
# PRESET BUILDERS
# ============================================================================


class ClassificationPipelineBuilder(TrainingPipelineBuilder):
    """Pre-configured builder for classification tasks"""

    def __init__(self, name: str, description: str = "", binary: bool = True):
        super().__init__(name, description)
        self._binary = binary
        # Set default classification evaluation
        self.set_evaluation("classification")


class RegressionPipelineBuilder(TrainingPipelineBuilder):
    """Pre-configured builder for regression tasks"""

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        # Set default regression evaluation
        self.set_evaluation("regression")


class EnsemblePipelineBuilder(TrainingPipelineBuilder):
    """Pre-configured builder for ensemble models"""

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        # Set default ensemble ranking
        self.set_ranking_top_k(k=5, method="ensemble", ensemble_method="voting")
