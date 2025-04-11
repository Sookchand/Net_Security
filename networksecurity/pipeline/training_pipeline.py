import os
import sys
import subprocess
from datetime import datetime

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME
from networksecurity.cloud.s3_syncer import S3Sync
from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR

from networksecurity.entity.config_entity import (
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
    ModelTrainerArtifact,
)


class TrainingPipeline:
    def __init__(self, training_pipeline_config):
        """
        Initialize the training pipeline with configuration
        """
        if not training_pipeline_config:
            raise ValueError("Training pipeline config cannot be None")
        
        self.training_pipeline_config = training_pipeline_config
        self.s3_sync = S3Sync()
        logging.info(f"Training Pipeline initialized with config: {training_pipeline_config}")
        
    def start_data_ingestion(self):
        """
        Start the data ingestion process
        """
        try:
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data ingestion phase")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"Data ingestion completed successfully. Artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            logging.error(f"Error in data ingestion: {str(e)}")
            raise NetworkSecurityException(e, sys)
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        """
        Start the data validation process
        """
        try:
            logging.info("Starting data validation phase")
            data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=data_validation_config
            )
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info("Data validation completed successfully")
            return data_validation_artifact
        except Exception as e:
            logging.error(f"Error in data validation: {str(e)}")
            raise NetworkSecurityException(e, sys)
        
    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact):
        """
        Start the data transformation process
        """
        try:
            logging.info("Starting data transformation phase")
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(
                data_validation_artifact=data_validation_artifact,
                data_transformation_config=data_transformation_config
            )
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info("Data transformation completed successfully")
            return data_transformation_artifact
        except Exception as e:
            logging.error(f"Error in data transformation: {str(e)}")
            raise NetworkSecurityException(e, sys)
        
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        """
        Start the model training process
        """
        try:
            logging.info("Starting model training phase")
            self.model_trainer_config = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            model_trainer = ModelTrainer(
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=self.model_trainer_config
            )
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info("Model training completed successfully")
            return model_trainer_artifact
        except Exception as e:
            logging.error(f"Error in model training: {str(e)}")
            raise NetworkSecurityException(e, sys)
        
    def sync_artifact_dir_to_s3(self):
        """
        Sync artifacts to S3 after training completion
        """
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            logging.info(f"Starting sync of artifact directory to S3 bucket: {aws_bucket_url}")
            
            artifact_dir = self.training_pipeline_config.artifact_dir
            
            # Check if artifact directory exists after training
            if not os.path.exists(artifact_dir):
                logging.error(f"Artifact directory not found after training: {artifact_dir}")
                return False
                
            # Log directory structure and contents
            logging.info(f"Artifact directory found at: {artifact_dir}")
            for root, dirs, files in os.walk(artifact_dir):
                logging.info(f"\nDirectory: {root}")
                if dirs:
                    logging.info(f"Subdirectories: {dirs}")
                if files:
                    logging.info(f"Files: {files}")
            
            # Execute sync command
            command = f"aws s3 sync {artifact_dir} {aws_bucket_url}"
            logging.info(f"Executing AWS S3 sync command: {command}")
            
            process = subprocess.run(command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                logging.info("Successfully synced artifacts to S3")
                return True
            else:
                logging.error(f"Failed to sync artifacts to S3. Error: {process.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"Error syncing artifact directory to S3: {str(e)}")
            raise NetworkSecurityException(e, sys)

    def sync_model_to_s3(self):
        """
        Sync final model to S3 after training completion
        """
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            logging.info(f"Starting sync of final model directory to S3 bucket: {aws_bucket_url}")
            
            # Use the correct path from your constants
            model_dir = "final_model"  # Update this to match where your model is actually saved
            
            # Create directory if it doesn't exist
            os.makedirs(model_dir, exist_ok=True)
            
            if not os.path.exists(model_dir):
                logging.error(f"Model directory not found: {model_dir}")
                return False
                
            # Log model directory contents
            logging.info(f"Model directory found at: {model_dir}")
            for root, dirs, files in os.walk(model_dir):
                logging.info(f"\nDirectory: {root}")
                if dirs:
                    logging.info(f"Subdirectories: {dirs}")
                if files:
                    logging.info(f"Files: {files}")
            
            # Execute sync command
            command = f"aws s3 sync {model_dir} {aws_bucket_url}"
            logging.info(f"Executing AWS S3 sync command: {command}")
            
            process = subprocess.run(command, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                logging.info(f"Successfully synced final model to S3")
                if process.stdout:
                    logging.info(f"Sync output: {process.stdout}")
                return True
            else:
                logging.error(f"Failed to sync final model to S3. Error: {process.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"Error syncing final model directory to S3: {str(e)}")
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self):
        """
        Execute the complete training pipeline
        """
        try:
            logging.info("Starting training pipeline execution")
            
            # Execute pipeline steps
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact)
            
            # Sync artifacts and model to S3
            logging.info("Starting S3 sync operations")
            self.sync_artifact_dir_to_s3()
            self.sync_model_to_s3()  # Changed method name to match implementation
            
            logging.info("Training pipeline completed successfully!")
            return model_trainer_artifact
        except Exception as e:
            logging.error(f"Error in training pipeline: {str(e)}")
            raise NetworkSecurityException(e, sys)