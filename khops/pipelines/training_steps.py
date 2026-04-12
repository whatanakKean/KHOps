"""Training Pipeline Steps Configuration

Comprehensive module defining all available steps for ML training pipelines.
Users can select and configure each step from the available options.

Structure:
    - Data Selection: Choose features/variables
    - Preprocessing: Data preparation and feature engineering
    - Model Training: Algorithm selection
    - Evaluation: Metrics and validation
    - Ranking: Model candidate comparison
    - Serving: Deployment method

All steps have sensible defaults. Users can override with custom configurations.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

# ============================================================================
# DATA STEP: Feature/Variable Selection
# ============================================================================


class DataSourceType(str, Enum):
    """Supported data sources"""

    CSV = "csv"
    PARQUET = "parquet"
    DATABASE = "database"
    S3 = "s3"
    API = "api"


class DataConfig(BaseModel):
    """Data selection and loading configuration"""

    source_type: DataSourceType = Field(default=DataSourceType.CSV, description="Data source type")
    source_path: str = Field(..., description="Path or connection string to data")
    target_column: str = Field(..., description="Target variable name (label)")
    feature_columns: Optional[List[str]] = Field(
        default=None, description="List of feature columns to use. If None, uses all except target"
    )
    test_size: float = Field(default=0.2, ge=0.0, le=1.0, description="Test set fraction")
    validation_size: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Validation set fraction"
    )
    random_state: int = Field(default=42, description="Random seed for reproducibility")
    stratified: bool = Field(
        default=True, description="Use stratified split for classification tasks"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source_type": "csv",
                "source_path": "data/training_data.csv",
                "target_column": "target",
                "feature_columns": ["age", "income", "credit_score"],
                "test_size": 0.2,
                "validation_size": 0.1,
                "random_state": 42,
                "stratified": True,
            }
        }


# ============================================================================
# PREPROCESSING STEP: Data Preparation & Feature Engineering
# ============================================================================


class ScalerType(str, Enum):
    """Feature scaling methods"""

    STANDARD = "standard"  # StandardScaler
    MIN_MAX = "minmax"  # MinMaxScaler
    ROBUST = "robust"  # RobustScaler
    NONE = "none"


class ImputationStrategy(str, Enum):
    """Missing value handling"""

    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    DROP = "drop"
    FORWARD_FILL = "forward_fill"


class EncodingMethod(str, Enum):
    """Categorical encoding methods"""

    ONE_HOT = "onehot"
    LABEL = "label"
    TARGET = "target"
    ORDINAL = "ordinal"


class PreprocessingStep(BaseModel):
    """Individual preprocessing step configuration"""

    name: str = Field(..., description="Step identifier (e.g., 'handle_missing')")
    step_type: str = Field(..., description="Type of preprocessing (e.g., 'imputation', 'scaling')")
    enabled: bool = Field(default=True, description="Enable/disable this step")
    params: Dict[str, Any] = Field(default_factory=dict, description="Step-specific parameters")


class PreprocessingConfig(BaseModel):
    """Complete preprocessing configuration"""

    handle_missing: bool = Field(default=True, description="Handle missing values")
    missing_strategy: ImputationStrategy = Field(default=ImputationStrategy.MEAN)

    remove_duplicates: bool = Field(default=True, description="Remove duplicate rows")

    handle_outliers: bool = Field(default=False, description="Detect and handle outliers")
    outlier_method: Literal["iqr", "zscore", "isolation_forest"] = Field(
        default="iqr", description="Outlier detection method"
    )

    encode_categorical: bool = Field(default=True, description="Encode categorical variables")
    encoding_method: EncodingMethod = Field(default=EncodingMethod.ONE_HOT)

    scale_features: bool = Field(default=True, description="Scale numerical features")
    scaler_type: ScalerType = Field(default=ScalerType.STANDARD)

    feature_selection: bool = Field(default=False, description="Select most important features")
    feature_selection_method: Literal["variance", "mutual_info", "correlation"] = Field(
        default="variance"
    )
    n_features_to_select: Optional[int] = Field(
        default=None, description="Number of features to keep"
    )

    custom_steps: List[PreprocessingStep] = Field(
        default_factory=list, description="Custom preprocessing steps"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "handle_missing": True,
                "missing_strategy": "mean",
                "remove_duplicates": True,
                "handle_outliers": False,
                "encode_categorical": True,
                "encoding_method": "onehot",
                "scale_features": True,
                "scaler_type": "standard",
                "feature_selection": False,
                "custom_steps": [],
            }
        }


# ============================================================================
# MODEL STEP: Algorithm Selection
# ============================================================================


class ModelType(str, Enum):
    """Supported model types"""

    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    SVM = "svm"
    KNN = "knn"
    NEURAL_NETWORK = "neural_network"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CATBOOST = "catboost"


class ModelConfig(BaseModel):
    """Model training configuration"""

    id: str = Field(..., description="Unique model identifier")
    model_type: ModelType = Field(..., description="Algorithm/model type")
    hyperparameters: Dict[str, Any] = Field(
        default_factory=dict, description="Algorithm-specific hyperparameters"
    )
    random_state: int = Field(default=42, description="Random seed")
    n_jobs: Optional[int] = Field(default=-1, description="Number of parallel jobs (-1 = all CPUs)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "rf_v1",
                    "model_type": "random_forest",
                    "hyperparameters": {
                        "n_estimators": 100,
                        "max_depth": 10,
                        "min_samples_split": 5,
                    },
                    "random_state": 42,
                    "n_jobs": -1,
                },
                {
                    "id": "xgb_v1",
                    "model_type": "xgboost",
                    "hyperparameters": {
                        "n_estimators": 100,
                        "learning_rate": 0.1,
                        "max_depth": 6,
                        "subsample": 0.8,
                    },
                    "random_state": 42,
                    "n_jobs": -1,
                },
            ]
        }


# Default model configurations (sensible starting points)
DEFAULT_MODELS = {
    "rf_default": ModelConfig(
        id="rf_default",
        model_type=ModelType.RANDOM_FOREST,
        hyperparameters={
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
        },
    ),
    "xgb_default": ModelConfig(
        id="xgb_default",
        model_type=ModelType.XGBOOST,
        hyperparameters={
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
        },
    ),
    "lgb_default": ModelConfig(
        id="lgb_default",
        model_type=ModelType.LIGHTGBM,
        hyperparameters={
            "n_estimators": 100,
            "learning_rate": 0.1,
            "num_leaves": 31,
            "feature_fraction": 0.8,
            "bagging_fraction": 0.8,
        },
    ),
    "cb_default": ModelConfig(
        id="cb_default",
        model_type=ModelType.CATBOOST,
        hyperparameters={"iterations": 100, "learning_rate": 0.1, "depth": 6, "subsample": 0.8},
    ),
    "lr_default": ModelConfig(
        id="lr_default",
        model_type=ModelType.LOGISTIC_REGRESSION,
        hyperparameters={"max_iter": 1000, "random_state": 42},
    ),
}


# ============================================================================
# EVALUATION STEP: Metrics & Validation
# ============================================================================


class ClassificationMetric(str, Enum):
    """Classification evaluation metrics"""

    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1 = "f1"
    AUC_ROC = "auc_roc"
    AUC_PR = "auc_pr"
    CONFUSION_MATRIX = "confusion_matrix"
    COHEN_KAPPA = "cohen_kappa"


class RegressionMetric(str, Enum):
    """Regression evaluation metrics"""

    MSE = "mse"
    RMSE = "rmse"
    MAE = "mae"
    MAPE = "mape"
    R2 = "r2"
    ADJUSTED_R2 = "adjusted_r2"


class ValidationMethod(str, Enum):
    """Cross-validation methods"""

    HOLDOUT = "holdout"
    K_FOLD = "k_fold"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    TIME_SERIES = "time_series"
    LEAVE_ONE_OUT = "leave_one_out"


class EvaluationConfig(BaseModel):
    """Evaluation and validation configuration"""

    task_type: Literal["classification", "regression"] = Field(
        default="classification", description="Machine learning task type"
    )

    classification_metrics: List[ClassificationMetric] = Field(
        default=[
            ClassificationMetric.ACCURACY,
            ClassificationMetric.F1,
            ClassificationMetric.AUC_ROC,
        ],
        description="Metrics for classification tasks",
    )

    regression_metrics: List[RegressionMetric] = Field(
        default=[RegressionMetric.RMSE, RegressionMetric.MAE, RegressionMetric.R2],
        description="Metrics for regression tasks",
    )

    validation_method: ValidationMethod = Field(
        default=ValidationMethod.K_FOLD, description="Cross-validation strategy"
    )

    n_splits: int = Field(default=5, ge=2, description="Number of folds for k-fold validation")

    primary_metric: str = Field(default="f1", description="Primary metric for model selection")

    threshold_optimization: bool = Field(
        default=False, description="Optimize classification threshold for primary metric"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "task_type": "classification",
                    "classification_metrics": ["accuracy", "f1", "auc_roc"],
                    "validation_method": "k_fold",
                    "n_splits": 5,
                    "primary_metric": "f1",
                },
                {
                    "task_type": "regression",
                    "regression_metrics": ["rmse", "mae", "r2"],
                    "validation_method": "k_fold",
                    "n_splits": 5,
                    "primary_metric": "r2",
                },
            ]
        }


# ============================================================================
# RANKING STEP: Model Comparison & Selection
# ============================================================================


class RankingMethod(str, Enum):
    """Model ranking/comparison methods"""

    BEST_PRIMARY_METRIC = "best_primary_metric"
    WEIGHTED_SCORE = "weighted_score"
    PARETO_FRONTIER = "pareto_frontier"
    ENSEMBLE = "ensemble"


class RankingConfig(BaseModel):
    """Model candidate ranking and selection configuration"""

    ranking_method: RankingMethod = Field(
        default=RankingMethod.BEST_PRIMARY_METRIC, description="Method for ranking candidate models"
    )

    metric_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Weights for weighted scoring (e.g., {'f1': 0.5, 'auc_roc': 0.3, 'speed': 0.2})",
    )

    select_top_k: int = Field(default=1, ge=1, description="Number of top models to select")

    ensemble_method: Optional[Literal["voting", "stacking", "blending"]] = Field(
        default=None, description="Ensemble method if ranking_method is 'ensemble'"
    )

    ensemble_voting_strategy: Optional[Literal["hard", "soft"]] = Field(
        default="soft", description="Voting strategy for ensemble"
    )

    save_top_k_models: bool = Field(
        default=True, description="Save all top-k models or only selected model"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {"ranking_method": "best_primary_metric", "select_top_k": 1},
                {
                    "ranking_method": "weighted_score",
                    "metric_weights": {"f1": 0.5, "auc_roc": 0.3, "inference_speed": 0.2},
                    "select_top_k": 3,
                },
                {
                    "ranking_method": "ensemble",
                    "ensemble_method": "voting",
                    "ensemble_voting_strategy": "soft",
                    "select_top_k": 5,
                },
            ]
        }


# ============================================================================
# SERVING STEP: Model Deployment
# ============================================================================


class ServingType(str, Enum):
    """Serving/deployment methods"""

    API = "api"
    BATCH = "batch"
    STREAMING = "streaming"
    EDGE = "edge"


class APIServingConfig(BaseModel):
    """API serving configuration"""

    enabled: bool = Field(default=True, description="Enable API serving")
    port: int = Field(default=8001, ge=1024, le=65535, description="API server port")
    max_workers: int = Field(default=4, ge=1, description="Number of worker processes")
    request_timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    batch_prediction_timeout: int = Field(default=60, ge=1, description="Batch prediction timeout")


class BatchServingConfig(BaseModel):
    """Batch serving configuration"""

    enabled: bool = Field(default=False, description="Enable batch serving")
    schedule: str = Field(default="daily", description="Batch schedule (e.g., 'daily', 'hourly')")
    input_format: Literal["csv", "parquet", "json"] = Field(
        default="csv", description="Input data format"
    )
    output_format: Literal["csv", "parquet", "json"] = Field(
        default="csv", description="Output format"
    )
    max_batch_size: int = Field(default=10000, ge=1, description="Maximum rows per batch")


class ServingConfig(BaseModel):
    """Complete serving/deployment configuration"""

    serving_type: ServingType = Field(default=ServingType.API, description="Primary serving method")

    api: APIServingConfig = Field(
        default_factory=APIServingConfig, description="API serving settings"
    )
    batch: BatchServingConfig = Field(
        default_factory=BatchServingConfig, description="Batch serving settings"
    )

    model_cache_ttl: int = Field(default=3600, ge=1, description="Model cache TTL in seconds")

    enable_monitoring: bool = Field(default=True, description="Enable predictions monitoring")
    enable_drift_detection: bool = Field(default=True, description="Enable data drift detection")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "serving_type": "api",
                    "api": {"enabled": True, "port": 8001, "max_workers": 4, "request_timeout": 30},
                    "batch": {"enabled": False},
                    "model_cache_ttl": 3600,
                    "enable_monitoring": True,
                },
                {
                    "serving_type": "batch",
                    "api": {"enabled": False},
                    "batch": {
                        "enabled": True,
                        "schedule": "daily",
                        "input_format": "parquet",
                        "output_format": "parquet",
                    },
                },
            ]
        }


# ============================================================================
# COMPLETE TRAINING PIPELINE CONFIGURATION
# ============================================================================


class TrainingPipelineConfig(BaseModel):
    """Complete training pipeline configuration combining all steps"""

    name: str = Field(..., min_length=1, max_length=255, description="Pipeline name")
    description: str = Field(default="", max_length=1000, description="Pipeline description")
    version: str = Field(default="1.0", pattern=r"^\d+\.\d+$", description="Pipeline version")

    # Training steps
    data: DataConfig = Field(..., description="Data selection configuration")
    preprocessing: PreprocessingConfig = Field(
        default_factory=PreprocessingConfig, description="Data preprocessing steps"
    )
    models: List[ModelConfig] = Field(..., min_items=1, description="Models to train and compare")
    evaluation: EvaluationConfig = Field(
        default_factory=EvaluationConfig, description="Evaluation metrics and validation"
    )
    ranking: RankingConfig = Field(
        default_factory=RankingConfig, description="Model ranking and selection strategy"
    )
    serving: ServingConfig = Field(
        default_factory=ServingConfig, description="Model serving/deployment configuration"
    )

    class Config:
        json_schema_extra = {
            "title": "ML Training Pipeline Configuration",
            "description": "Comprehensive training pipeline with all steps",
        }


# ============================================================================
# DEFAULT TRAINING PIPELINE TEMPLATES
# ============================================================================


def get_default_classification_pipeline() -> TrainingPipelineConfig:
    """Get default binary/multiclass classification pipeline"""
    return TrainingPipelineConfig(
        name="default-classification",
        description="Default classification pipeline with standard settings",
        version="1.0",
        data=DataConfig(
            source_type=DataSourceType.CSV,
            source_path="data/training_data.csv",
            target_column="target",
            test_size=0.2,
            validation_size=0.1,
            stratified=True,
        ),
        preprocessing=PreprocessingConfig(
            handle_missing=True,
            missing_strategy=ImputationStrategy.MEAN,
            remove_duplicates=True,
            encode_categorical=True,
            scale_features=True,
            scaler_type=ScalerType.STANDARD,
        ),
        models=[
            DEFAULT_MODELS["rf_default"],
            DEFAULT_MODELS["xgb_default"],
            DEFAULT_MODELS["lgb_default"],
        ],
        evaluation=EvaluationConfig(
            task_type="classification",
            classification_metrics=[
                ClassificationMetric.ACCURACY,
                ClassificationMetric.F1,
                ClassificationMetric.AUC_ROC,
            ],
            validation_method=ValidationMethod.K_FOLD,
            n_splits=5,
            primary_metric="f1",
        ),
        ranking=RankingConfig(ranking_method=RankingMethod.BEST_PRIMARY_METRIC, select_top_k=1),
        serving=ServingConfig(
            serving_type=ServingType.API, api=APIServingConfig(enabled=True, port=8001)
        ),
    )


def get_default_regression_pipeline() -> TrainingPipelineConfig:
    """Get default regression pipeline"""
    return TrainingPipelineConfig(
        name="default-regression",
        description="Default regression pipeline with standard settings",
        version="1.0",
        data=DataConfig(
            source_type=DataSourceType.CSV,
            source_path="data/training_data.csv",
            target_column="target",
            test_size=0.2,
            validation_size=0.1,
            stratified=False,
        ),
        preprocessing=PreprocessingConfig(
            handle_missing=True,
            missing_strategy=ImputationStrategy.MEAN,
            remove_duplicates=True,
            scale_features=True,
            scaler_type=ScalerType.STANDARD,
        ),
        models=[DEFAULT_MODELS["rf_default"], DEFAULT_MODELS["xgb_default"]],
        evaluation=EvaluationConfig(
            task_type="regression",
            regression_metrics=[RegressionMetric.RMSE, RegressionMetric.MAE, RegressionMetric.R2],
            validation_method=ValidationMethod.K_FOLD,
            n_splits=5,
            primary_metric="r2",
        ),
        ranking=RankingConfig(ranking_method=RankingMethod.BEST_PRIMARY_METRIC, select_top_k=1),
        serving=ServingConfig(
            serving_type=ServingType.API, api=APIServingConfig(enabled=True, port=8001)
        ),
    )


def get_ensemble_pipeline() -> TrainingPipelineConfig:
    """Get ensemble model training pipeline"""
    return TrainingPipelineConfig(
        name="ensemble-pipeline",
        description="Ensemble pipeline for multi-model approach",
        version="1.0",
        data=DataConfig(
            source_type=DataSourceType.CSV,
            source_path="data/training_data.csv",
            target_column="target",
            test_size=0.2,
            validation_size=0.1,
        ),
        models=[
            DEFAULT_MODELS["rf_default"],
            DEFAULT_MODELS["xgb_default"],
            DEFAULT_MODELS["lgb_default"],
            DEFAULT_MODELS["cb_default"],
        ],
        evaluation=EvaluationConfig(task_type="classification", primary_metric="f1"),
        ranking=RankingConfig(
            ranking_method=RankingMethod.ENSEMBLE,
            ensemble_method="voting",
            ensemble_voting_strategy="soft",
            select_top_k=5,
            save_top_k_models=True,
        ),
        serving=ServingConfig(
            serving_type=ServingType.API, api=APIServingConfig(enabled=True, max_workers=8)
        ),
    )
