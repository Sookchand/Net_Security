import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import(
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainArtifact,
)

from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME
from networksecurity.cloud.s3_syncer import S3Sync
from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR

class TrainingPipeline:
    def __init__(self, progress_callback=None):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = S3Sync() # Initialize S3Sync
        self.progress_callback = progress_callback or (lambda message: None)  # Default to no-op if no callback is provided

    def start_data_ingestion(self):
        try:
            self.progress_callback("Starting data ingestion...")
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            self.progress_callback("Data ingestion completed.")
            return data_ingestion_artifact
        except Exception as e:
            self.progress_callback(f"Error during data ingestion: {e}")
            raise NetworkSecurityException(e, sys)

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        try:
            self.progress_callback("Starting data validation...")
            data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact, data_validation_config=data_validation_config)
            data_validation_artifact = data_validation.initiate_data_validation()
            self.progress_callback("Data validation completed.")
            return data_validation_artifact
        except Exception as e:
            self.progress_callback(f"Error during data validation: {e}")
            raise NetworkSecurityException(e, sys)

    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact):
        try:
            self.progress_callback("Starting data transformation...")
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact, data_transformation_config=data_transformation_config)
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            self.progress_callback("Data transformation completed.")
            return data_transformation_artifact
        except Exception as e:
            self.progress_callback(f"Error during data transformation: {e}")
            raise NetworkSecurityException(e, sys)

    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainArtifact:
        try:
            self.progress_callback("Starting model training...")
            self.model_trainer_config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            model_trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifact, model_trainer_config=self.model_trainer_config)
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            self.progress_callback("Model training completed.")
            return model_trainer_artifact
        except Exception as e:
            self.progress_callback(f"Error during model training: {e}")
            raise NetworkSecurityException(e, sys)
    
    # Sync artifacts to S3    
    def sync_artifacts_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"  # Fixed URL
            logging.info(f"Syncing artifacts to S3 bucket: {aws_bucket_url}")
            self.s3_sync.sync_folder_to_s3(
                folder=self.training_pipeline_config.artifact_dir,
                aws_bucket_url=aws_bucket_url
            )
            logging.info("Artifacts synced to S3 successfully.")
        except Exception as e:
            logging.error(f"Error during S3 sync: {e}")
            self.progress_callback(f"Error during S3 sync: {e}")
            raise NetworkSecurityException(e, sys)
    
    # Sync saved model directory to S3    
    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"  # Fixed URL
            logging.info(f"Syncing saved model directory to S3 bucket: {aws_bucket_url}")
            self.s3_sync.sync_folder_to_s3(
                folder=SAVED_MODEL_DIR,
                aws_bucket_url=aws_bucket_url
            )
            logging.info("Saved model directory synced to S3 successfully.")
        except Exception as e:
            logging.error(f"Error during S3 sync: {e}")
            self.progress_callback(f"Error during S3 sync: {e}")
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self):
        try:
            self.progress_callback("Pipeline execution started.")
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact)
            self.progress_callback("Pipeline execution completed.")
            self.sync_artifacts_to_s3() # Sync artifacts to S3
            self.sync_saved_model_dir_to_s3() # Sync saved model directory to S3
            return model_trainer_artifact
        except Exception as e:
            self.progress_callback(f"Pipeline execution failed: {e}")
            raise NetworkSecurityException(e, sys)