import os
import sys
import pandas as pd
from typing import Dict, Any

from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.entity.config_entity import ModelDriftConfig
from networksecurity.entity.artifact_entity import DataValidationArtifact, ModelTrainerArtifact, ModelDriftArtifact
from networksecurity.components.model_drift import ModelDriftDetector
from networksecurity.utils.main_utils.utils import load_numpy_array_data, load_object, save_object, write_yaml_file

class ModelDrift:
    """
    ModelDrift component detects and reports drift in model performance over time.

    This class compares the performance of a baseline model with a current model
    to identify potential degradation or drift in model effectiveness.
    """

    def __init__(
        self,
        model_drift_config: ModelDriftConfig,
        data_validation_artifact: DataValidationArtifact,
        model_trainer_artifact: ModelTrainerArtifact
    ):
        """
        Initialize the ModelDrift component.

        Args:
            model_drift_config (ModelDriftConfig): Configuration for model drift detection
            data_validation_artifact (DataValidationArtifact): Artifact from data validation
            model_trainer_artifact (ModelTrainerArtifact): Artifact from model training
        """
        try:
            logging.info("Initializing ModelDrift component")
            self.model_drift_config = model_drift_config
            self.data_validation_artifact = data_validation_artifact
            self.model_trainer_artifact = model_trainer_artifact

            # Create directories
            os.makedirs(self.model_drift_config.model_drift_dir, exist_ok=True)
            os.makedirs(self.model_drift_config.drift_report_dir, exist_ok=True)
            os.makedirs(self.model_drift_config.visualization_dir, exist_ok=True)

            # Copy visualization files to static directory for web access
            self.web_visualization_dir = os.path.join("app", "static", "images", "model_drift")
            os.makedirs(self.web_visualization_dir, exist_ok=True)

            logging.info("ModelDrift component initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing ModelDrift component: {e}")
            raise NetworkSecurityException(e, sys)

    def initiate_model_drift_detection(self) -> ModelDriftArtifact:
        """
        Initiate the model drift detection process.

        Returns:
            ModelDriftArtifact: Artifact containing model drift detection results
        """
        try:
            logging.info("Starting model drift detection")

            # Check if baseline model exists
            if not os.path.exists(self.model_drift_config.baseline_model_path):
                logging.info("Baseline model not found. Using current model as baseline.")
                # Copy current model to baseline location
                baseline_model_dir = os.path.dirname(self.model_drift_config.baseline_model_path)
                os.makedirs(baseline_model_dir, exist_ok=True)
                save_object(
                    file_path=self.model_drift_config.baseline_model_path,
                    obj=load_object(file_path=self.model_trainer_artifact.trained_model_file_path)
                )
                logging.info(f"Current model saved as baseline at {self.model_drift_config.baseline_model_path}")

                # No drift to detect yet
                model_drift_artifact = ModelDriftArtifact(
                    drift_detected=False,
                    drift_report_file_path=None,
                    visualization_dir=self.model_drift_config.visualization_dir,
                    message="Baseline model created. No drift detection performed."
                )
                return model_drift_artifact

            # Load validation data
            train_data = pd.read_csv(self.data_validation_artifact.valid_train_file_path)
            test_data = pd.read_csv(self.data_validation_artifact.valid_test_file_path)

            # Separate features and target
            X_train = train_data.drop(columns=["Result"])
            y_train = train_data["Result"]
            X_test = test_data.drop(columns=["Result"])
            y_test = test_data["Result"]

            # Initialize model drift detector
            model_drift_detector = ModelDriftDetector(
                baseline_model_path=self.model_drift_config.baseline_model_path,
                current_model_path=self.model_trainer_artifact.trained_model_file_path,
                report_dir=self.model_drift_config.drift_report_dir,
                threshold=self.model_drift_config.drift_threshold
            )

            # Detect model drift
            drift_report = model_drift_detector.detect_model_drift(
                X_baseline=X_test,  # Use test data for both to ensure fair comparison
                y_baseline=y_test,
                X_current=X_test,
                y_current=y_test
            )

            # Copy visualization files to web directory
            for viz_path in drift_report.get("visualization_paths", []):
                if os.path.exists(viz_path):
                    viz_filename = os.path.basename(viz_path)
                    web_viz_path = os.path.join(self.web_visualization_dir, viz_filename)
                    import shutil
                    shutil.copy2(viz_path, web_viz_path)
                    logging.info(f"Copied visualization to web directory: {web_viz_path}")

            # Create model drift artifact
            model_drift_artifact = ModelDriftArtifact(
                drift_detected=drift_report["drift_detected"],
                drift_report_file_path=drift_report.get('json_report_path', ''),
                drift_text_report_file_path=drift_report.get('text_report_path', ''),
                visualization_dir=self.model_drift_config.visualization_dir,
                visualization_paths=drift_report.get('visualization_paths', []),
                message="Model drift detection completed successfully."
            )

            logging.info(f"Model drift detection completed. Drift detected: {drift_report['drift_detected']}")
            return model_drift_artifact

        except Exception as e:
            logging.error(f"Error in model drift detection: {e}")
            raise NetworkSecurityException(e, sys)
