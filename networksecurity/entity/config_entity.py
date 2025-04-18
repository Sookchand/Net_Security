from datetime import datetime
import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from networksecurity.constant import training_pipeline

# print(training_pipeline.PIPELINE_NAME)
# print(training_pipeline.ARTIFACT_DIR)

class TrainingPipelineConfig:
    def __init__(self, timestamp=datetime.now()):
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S")
        self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        self.model_dir = os.path.join("final_model")
        self.timestamp:str = timestamp

class DataIngestionConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        self.data_ingestion_dir:str=os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_INGESTION_DIR_NAME
        )
        self.feature_store_file_path: str = os.path.join(
                self.data_ingestion_dir,
                training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,
                training_pipeline.FILE_NAME
            )
        self.training_file_path: str = os.path.join(
                self.data_ingestion_dir,
                training_pipeline.DATA_INGESTION_INGESTED_DIR,
                training_pipeline.TRAIN_FILE_NAME
            )
        self.testing_file_path: str = os.path.join(
                self.data_ingestion_dir,
                training_pipeline.DATA_INGESTION_INGESTED_DIR,
                training_pipeline.TEST_FILE_NAME
            )
        self.train_test_split_ratio: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATION
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name: str = training_pipeline.DATA_INGESTION_DATABASE_NAME


class DataValidationConfig:
    def __init__(self, training_pipeline_config:TrainingPipelineConfig):
        self.data_validation_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_VALIDATION_DIR_NAME
            )
        self.valid_data_dir: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_VALID_DIR
            )
        self.invalid_data_dir: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_INVALID_DIR
            )
        self.valid_train_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.TRAIN_FILE_NAME
            )
        self.valid_test_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.TEST_FILE_NAME
            )
        self.invlaid_train_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.TRAIN_FILE_NAME
            )
        self.invlaid_test_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.TEST_FILE_NAME
            )
        self.drift_report_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME,
            )

class DataTransformationConfig:
    def __init__(self, training_pipeline_config:TrainingPipelineConfig):
        self.data_transformation_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_TRANSFORMATION_DIR_NAME,
            ) # Output: Artifacts/06_29_202
        self.transformed_train_file_path: str = os.path.join(
            self.data_transformation_dir,
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            training_pipeline.TRAIN_FILE_NAME.replace("csv", "npy")
            ) # Output: Artifacts/06_29_2021_12_00_00/data_transformation/transformed_data/train_data.npy
        self.transformed_test_file_path: str = os.path.join(
            self.data_transformation_dir,
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            training_pipeline.TEST_FILE_NAME.replace("csv", "npy")
            ) # Output: Artifacts/06_29_2021_12_00_00/data_transformation/transformed_data/test_data.npy
        self.transformed_object_file_path: str = os.path.join(
            self.data_transformation_dir,
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR,
            training_pipeline.PREPROCESSING_OBJECT_FILE_NAME,
            ) # Output: Artifacts/06_29_2021_12_00_00/data_transformation/transformed_object/preprocessing_object.pkl

class ModelTrainerConfig:
    def __init__(self, training_pipeline_config:TrainingPipelineConfig):
        self.model_training_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.MODEL_TRAINER_DIR_NAME
            ) # Output: Artifacts/06_29_2021_12_00_00/model_training
        self.trained_model_file_path: str = os.path.join(
            self.model_training_dir,
            training_pipeline.MODEL_TRAINER_TRAINED_MODEL_DIR,
            training_pipeline.MODEL_FILE_NAME
            ) # Output: Artifacts/06_29_2021_12_00_00/model_training/trained_model/trained_model.
        self.expected_accuracy: float = training_pipeline.MODEL_TRAINER_EXPECTED_SCORE # Output: 0.6
        self.overfitting_underfitting_threshold: float = training_pipeline.MODEL_TRAINER_OVER_FIITING_UNDER_FITTING_THRESHOLD # Output: 0.85


class ModelDriftConfig:
    def __init__(self, training_pipeline_config:TrainingPipelineConfig):
        self.model_drift_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.MODEL_DRIFT_DIR_NAME
            ) # Output: Artifacts/06_29_2021_12_00_00/model_drift
        self.baseline_model_path: str = os.path.join(
            training_pipeline_config.model_dir,
            training_pipeline.MODEL_FILE_NAME
            ) # Output: final_model/model.pkl
        self.current_model_path: str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.MODEL_TRAINER_DIR_NAME,
            training_pipeline.MODEL_TRAINER_TRAINED_MODEL_DIR,
            training_pipeline.MODEL_FILE_NAME
            ) # Output: Artifacts/06_29_2021_12_00_00/model_training/trained_model/model.pkl
        self.drift_report_dir: str = os.path.join(
            self.model_drift_dir,
            training_pipeline.MODEL_DRIFT_REPORT_DIR
            ) # Output: Artifacts/06_29_2021_12_00_00/model_drift/reports
        self.drift_threshold: float = training_pipeline.MODEL_DRIFT_THRESHOLD # Output: 0.05
        self.visualization_dir: str = os.path.join(
            self.model_drift_dir,
            training_pipeline.MODEL_DRIFT_VISUALIZATION_DIR
            ) # Output: Artifacts/06_29_2021_12_00_00/model_drift/visualizations


