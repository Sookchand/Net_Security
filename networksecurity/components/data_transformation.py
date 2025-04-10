import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import TARGET_COLUMN
from networksecurity.entity.artifact_entity import DataValidationArtifact
from networksecurity.entity.artifact_entity import DataTransformationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS 

class DataTransformation:
    """
    The DataTransformation class performs data preprocessing tasks such as imputation, 
    validation, and conversion to prepare data for training and testing machine learning models.

    Attributes:
        data_validation_artifact (DataValidationArtifact): Object containing validation data.
        data_transformation_config (DataTransformationConfig): Configuration for data transformation.
    """
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        """
        Initializes the DataTransformation class.

        Args:
            data_validation_artifact (DataValidationArtifact): Validation data artifact.
            data_transformation_config (DataTransformationConfig): Configuration for transformation.
        """
        try:
            logging.info("Initializing DataTransformation class.")
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
        except Exception as e:
            logging.error(f"Error initializing DataTransformation class: {e}")
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """
        Reads data from a CSV file into a DataFrame.

        Args:
            file_path (str): Path to the CSV file.

        Returns:
            pd.DataFrame: Loaded data.

        Raises:
            NetworkSecurityException: If the file cannot be read.
        """
        try:
            logging.info(f"Reading data from file: {file_path}")
            return pd.read_csv(file_path)
        except Exception as e:
            logging.error(f"Error reading data from {file_path}: {e}")
            raise NetworkSecurityException(e, sys)
        
    def get_data_transformer_object(self) -> Pipeline:
        """
        Initializes a data transformer object, including a KNN Imputer pipeline.

        Returns:
            Pipeline: Preprocessor object configured with KNNImputer.
        """
        try:
            logging.info("Initializing KNN Imputer pipeline.")
            imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"KNNImputer initialized with parameters: {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
            processor = Pipeline([("imputer", imputer)])
            return processor
        except Exception as e:
            logging.error(f"Error initializing KNN Imputer pipeline: {e}")
            raise NetworkSecurityException(e, sys)

    def validate_and_convert_data_types(self, dataframe: pd.DataFrame, schema: dict) -> pd.DataFrame:
        """
        Validates and converts column data types based on a schema.

        Args:
            dataframe (pd.DataFrame): DataFrame to validate.
            schema (dict): Dictionary mapping column names to expected data types.

        Returns:
            pd.DataFrame: DataFrame with validated and converted data types.

        Raises:
            NetworkSecurityException: If a column fails validation or conversion.
        """
        try:
            logging.info("Validating and converting data types.")
            for column, expected_dtype in schema.items():
                if column in dataframe.columns:
                    try:
                        dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce')
                        dataframe[column] = dataframe[column].astype(expected_dtype)
                        logging.info(f"Column {column} successfully converted to {expected_dtype}.")
                    except ValueError as e:
                        logging.error(f"Error converting column {column} to {expected_dtype}: {e}")
                        raise NetworkSecurityException(f"Column {column} has incorrect data type. "
                                                       f"Expected: {expected_dtype}, Found: {dataframe[column].dtype}. "
                                                       f"Error: {e}", sys)
            return dataframe
        except Exception as e:
            logging.error(f"Error validating and converting data types: {e}")
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """
        Initiates the data transformation process.

        Returns:
            DataTransformationArtifact: Artifact containing transformed data paths and preprocessor object.
        """
        logging.info("Starting data transformation process.")
        try:
            # Load train and test data
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)
            logging.info(f"Train DataFrame shape: {train_df.shape}")
            logging.info(f"Test DataFrame shape: {test_df.shape}")

            # Separate features and target for training data
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN].replace(-1, 0)

            # Separate features and target for testing data
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN].replace(-1, 0)

            # Define schema for data type validation
            schema = {
                "column1": np.float64,
                "column2": np.float64,
                # Add other columns and expected data types
            }
            input_feature_train_df = self.validate_and_convert_data_types(input_feature_train_df, schema)
            input_feature_test_df = self.validate_and_convert_data_types(input_feature_test_df, schema)
            logging.info("Data type validation and conversion complete.")

            # Preprocess data
            preprocessor = self.get_data_transformer_object()
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)

            # Combine features and target into arrays
            train_arr = np.c_[transformed_input_train_feature, target_feature_train_df.values]
            test_arr = np.c_[transformed_input_test_feature, target_feature_test_df.values]

            # Save transformed data and preprocessor object
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)
            logging.info("Transformed data and preprocessor object saved successfully.")

            save_object("final_model/preprocessor.pkl", preprocessor_object)  # Save the preprocessor object
            logging.info("Preprocessor object saved successfully.")
            
            # Create transformation artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            logging.info("Data transformation process completed successfully.")
            return data_transformation_artifact
        except Exception as e:
            logging.error(f"Error during data transformation process: {e}")
            raise NetworkSecurityException(e, sys)
