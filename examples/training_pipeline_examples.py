"""
Training Pipeline Examples

Demonstrates various ways to create and configure ML training pipelines.
"""

from khops.pipelines.training_builder import (
    ClassificationPipelineBuilder,
    EnsemblePipelineBuilder,
    RegressionPipelineBuilder,
    TrainingPipelineBuilder,
)
from khops.pipelines.training_steps import (
    get_default_classification_pipeline,
    get_default_regression_pipeline,
    get_ensemble_pipeline,
)

# ============================================================================
# EXAMPLE 1: Binary Classification - Quick Start
# ============================================================================


def example_quick_classification():
    """Quick classification pipeline with minimal configuration"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Binary Classification - Quick Start")
    print("=" * 70)

    builder = ClassificationPipelineBuilder("customer_churn")
    builder.load_data(
        source_path="data/customers.csv",
        target_column="churn",
    )
    builder.add_default_models()
    builder.set_evaluation(task_type="classification", primary_metric="f1")

    config = builder.build()
    print(f"✓ Pipeline built: {config.name}")
    print(f"  Models: {[m.id for m in config.models]}")
    print(
        f"  Evaluation: {config.evaluation.task_type} - Primary: {config.evaluation.primary_metric}"
    )


# ============================================================================
# EXAMPLE 2: Detailed Classification with Custom Preprocessing
# ============================================================================


def example_detailed_classification():
    """Classification with detailed preprocessing and custom models"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Detailed Classification with Custom Preprocessing")
    print("=" * 70)

    builder = TrainingPipelineBuilder(
        name="credit_risk_model", description="Predict credit card default risk"
    )

    # Step 1: Data Configuration
    builder.load_data(
        source_path="s3://bank-data/customers.parquet",
        source_type="s3",
        target_column="default",
        feature_columns=["age", "income", "credit_score", "num_accounts"],
        test_size=0.2,
        validation_size=0.1,
        stratified=True,
        random_state=42,
    )

    # Step 2: Advanced Preprocessing
    builder.add_preprocessing(
        handle_missing=True,
        missing_strategy="median",
        remove_duplicates=True,
        handle_outliers=True,
        outlier_method="isolation_forest",
        encode_categorical=True,
        encoding_method="onehot",
        scale_features=True,
        scaler_type="robust",
        feature_selection=True,
        feature_selection_method="mutual_info",
        n_features_to_select=10,
    )

    # Step 3: Add Multiple Models with Custom Hyperparameters
    builder.add_model(
        "random_forest",
        model_id="rf_tuned",
        n_estimators=200,
        max_depth=15,
        min_samples_split=3,
        min_samples_leaf=1,
        max_features="sqrt",
    )

    builder.add_model(
        "xgboost",
        model_id="xgb_tuned",
        n_estimators=150,
        learning_rate=0.05,
        max_depth=8,
        subsample=0.9,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
    )

    builder.add_model(
        "lightgbm",
        model_id="lgb_tuned",
        n_estimators=150,
        learning_rate=0.05,
        num_leaves=50,
        feature_fraction=0.8,
        bagging_fraction=0.8,
        min_data_in_leaf=20,
    )

    # Step 4: Evaluation Configuration
    builder.set_evaluation(
        task_type="classification",
        metrics=["accuracy", "precision", "recall", "f1", "auc_roc"],
        primary_metric="auc_roc",
        validation_method="stratified_k_fold",
        n_splits=5,
        threshold_optimization=True,
    )

    # Step 5: Ranking Strategy - Select Top 3 by Weighted Score
    builder.set_ranking_top_k(
        k=3,
        method="weighted_score",
        metric_weights={
            "auc_roc": 0.5,  # Most important
            "f1": 0.3,  # Important for balance
            "precision": 0.2,  # Some weight to precision
        },
    )

    # Step 6: Serving Configuration
    builder.enable_api_serving(port=8001, max_workers=8, request_timeout=30)
    builder.enable_monitoring(enable=True)
    builder.enable_drift_detection(enable=True)

    # Build and save
    config = builder.build()
    builder.save_to_yaml("pipelines/credit_risk_model.yaml")
    builder.save_to_json("pipelines/credit_risk_model.json")

    print(f"✓ Pipeline: {config.name}")
    print(f"  Data: {config.data.source_path}")
    print(f"  Preprocessing: {7} steps configured")
    print(f"  Models: {len(config.models)} ({', '.join([m.id for m in config.models])})")
    print(f"  Top-k: {config.ranking.select_top_k} models by {config.ranking.ranking_method}")
    print(f"  Serving: {config.serving.serving_type} on port {config.serving.api.port}")


# ============================================================================
# EXAMPLE 3: Regression Pipeline
# ============================================================================


def example_regression():
    """Regression pipeline for continuous target prediction"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Regression Pipeline")
    print("=" * 70)

    builder = RegressionPipelineBuilder(
        name="house_price_predictor", description="Predict house prices from property features"
    )

    builder.load_data(
        source_path="data/housing.csv",
        target_column="price",
        feature_columns=["bedrooms", "bathrooms", "sqft", "age", "location"],
        test_size=0.2,
        validation_size=0.1,
        stratified=False,
    )

    # Preprocessing for regression
    builder.add_preprocessing(
        handle_missing=True,
        missing_strategy="median",
        handle_outliers=True,
        outlier_method="iqr",
        scale_features=True,
        scaler_type="standard",
        feature_selection=True,
        n_features_to_select=5,
    )

    # Add multiple models
    builder.add_model("random_forest", n_estimators=100, max_depth=15)
    builder.add_model("xgboost", n_estimators=100, learning_rate=0.1)
    builder.add_model("lightgbm", n_estimators=100, learning_rate=0.1)

    # Regression evaluation
    builder.set_evaluation(
        task_type="regression",
        metrics=["rmse", "mae", "r2"],
        primary_metric="r2",
        validation_method="k_fold",
        n_splits=5,
    )

    # Select single best model
    builder.set_ranking_top_k(k=1, method="best_primary_metric")

    builder.enable_api_serving(port=8001)

    config = builder.build()
    builder.save_to_yaml("pipelines/house_price.yaml")

    print(f"✓ Pipeline: {config.name}")
    print(f"  Task: {config.evaluation.task_type}")
    print(f"  Primary Metric: {config.evaluation.primary_metric}")
    print(f"  Models: {len(config.models)}")


# ============================================================================
# EXAMPLE 4: Ensemble Pipeline with Multiple Models
# ============================================================================


def example_ensemble():
    """Ensemble pipeline combining multiple models"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Ensemble Pipeline with Multiple Models")
    print("=" * 70)

    builder = EnsemblePipelineBuilder(
        name="fraud_detection_ensemble", description="Ensemble model for fraud detection"
    )

    builder.load_data(
        source_path="data/transactions.csv",
        target_column="is_fraud",
        test_size=0.2,
        validation_size=0.1,
        stratified=True,
    )

    builder.add_preprocessing(
        handle_missing=True,
        remove_duplicates=True,
        encode_categorical=True,
        scale_features=True,
        feature_selection=True,
    )

    # Add 5 diverse models for ensemble
    builder.add_model("random_forest", n_estimators=100, max_depth=12)
    builder.add_model("xgboost", n_estimators=100, learning_rate=0.1)
    builder.add_model("lightgbm", n_estimators=100, num_leaves=31)
    builder.add_model("catboost", iterations=100, depth=6)
    builder.add_model("logistic_regression", max_iter=1000)

    builder.set_evaluation("classification", primary_metric="f1")

    # Ensemble ranking with voting
    builder.set_ranking_top_k(
        k=5, method="ensemble", ensemble_method="voting", ensemble_voting_strategy="soft"
    )

    builder.enable_api_serving(max_workers=8)
    builder.enable_monitoring()
    builder.enable_drift_detection()

    config = builder.build()
    builder.save_to_yaml("pipelines/fraud_detection.yaml")

    print(f"✓ Pipeline: {config.name}")
    print(f"  Models: {len(config.models)} (for ensemble)")
    print(f"  Ensemble Method: {config.ranking.ensemble_method}")
    print(f"  Voting Strategy: {config.ranking.ensemble_voting_strategy}")


# ============================================================================
# EXAMPLE 5: Batch Serving Pipeline
# ============================================================================


def example_batch_serving():
    """Pipeline configured for batch prediction mode"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Batch Serving Pipeline")
    print("=" * 70)

    builder = TrainingPipelineBuilder(
        name="batch_recommendation_engine", description="Daily batch recommendations for users"
    )

    builder.load_data(
        source_path="s3://recommendation-data/user_behavior.parquet",
        source_type="s3",
        target_column="purchased",
        test_size=0.2,
    )

    builder.add_preprocessing(
        handle_missing=True, scale_features=True, feature_selection=True, n_features_to_select=20
    )

    builder.add_model("xgboost", n_estimators=100)

    builder.set_evaluation("classification", primary_metric="auc_roc")

    # Batch serving instead of API
    builder.enable_batch_serving(
        schedule="daily", input_format="parquet", output_format="parquet", max_batch_size=50000
    )

    config = builder.build()
    builder.save_to_yaml("pipelines/batch_recommendations.yaml")

    print(f"✓ Pipeline: {config.name}")
    print(f"  Serving Type: {config.serving.serving_type}")
    print(f"  Batch Schedule: {config.serving.batch.schedule}")
    print(f"  Input Format: {config.serving.batch.input_format}")


# ============================================================================
# EXAMPLE 6: Using Preset Defaults
# ============================================================================


def example_using_defaults():
    """Using built-in default pipeline configurations"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Using Built-in Default Configurations")
    print("=" * 70)

    # Default classification pipeline
    default_clf = get_default_classification_pipeline()
    print(f"✓ Default Classification: {default_clf.name}")
    print(f"  Models: {[m.id for m in default_clf.models]}")

    # Default regression pipeline
    default_reg = get_default_regression_pipeline()
    print(f"✓ Default Regression: {default_reg.name}")
    print(f"  Models: {[m.id for m in default_reg.models]}")

    # Default ensemble pipeline
    default_ens = get_ensemble_pipeline()
    print(f"✓ Default Ensemble: {default_ens.name}")
    print(f"  Models: {[m.id for m in default_ens.models]}")
    print(f"  Ensemble Method: {default_ens.ranking.ensemble_method}")


# ============================================================================
# EXAMPLE 7: Advanced - Custom Metric Weighting
# ============================================================================


def example_custom_metric_weighting():
    """Advanced example with custom metric weighting for business requirements"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Advanced - Custom Metric Weighting")
    print("=" * 70)

    builder = ClassificationPipelineBuilder(
        name="medical_diagnosis",
        description="Medical test diagnosis with high recall (minimize false negatives)",
    )

    builder.load_data(source_path="data/medical_tests.csv", target_column="disease", test_size=0.2)

    builder.add_preprocessing(handle_missing=True, scale_features=True, feature_selection=True)

    builder.add_model("random_forest", max_depth=10)
    builder.add_model("xgboost", learning_rate=0.1)
    builder.add_model("neural_network", hidden_layers=[128, 64])

    builder.set_evaluation(
        task_type="classification",
        metrics=["accuracy", "precision", "recall", "f1", "auc_roc"],
        primary_metric="recall",  # Minimize false negatives!
    )

    # Weight metrics to prioritize recall and precision
    builder.set_ranking_top_k(
        k=2,
        method="weighted_score",
        metric_weights={
            "recall": 0.5,  # Most critical - catch all cases
            "precision": 0.3,  # Important - reduce false alarms
            "auc_roc": 0.2,  # General performance
        },
    )

    config = builder.build()
    print(f"✓ Pipeline: {config.name}")
    print(f"  Primary Metric: {config.evaluation.primary_metric}")
    print(f"  Ranking Strategy: weighted_score")
    print(f"  Metric Weights: {config.ranking.metric_weights}")


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# COMPREHENSIVE TRAINING PIPELINE EXAMPLES")
    print("#" * 70)

    example_quick_classification()
    example_detailed_classification()
    example_regression()
    example_ensemble()
    example_batch_serving()
    example_using_defaults()
    example_custom_metric_weighting()

    print("\n" + "#" * 70)
    print("# ALL EXAMPLES COMPLETED")
    print("#" * 70 + "\n")
