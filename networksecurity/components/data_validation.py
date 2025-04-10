import os
import sys
import pandas as pd
from typing import Dict
from scipy.stats import ks_2samp
from networksecurity.logging.logger import logging  
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact 
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH 
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file


def extract_schema_columns(schema: Dict) -> Dict:
    """
    Extracts and flattens schema columns into a dictionary.

    Args:
        schema (dict): Schema configuration containing column information.

    Returns:
        dict: A dictionary mapping column names to their data types.

    Raises:
        NetworkSecurityException: If the schema format is invalid.
    """
    try:
        logging.info("Extracting schema columns.")
        return {list(column.keys())[0]: list(column.values())[0] for column in schema["columns"]}
    except Exception as e:
        logging.error(f"Exception occurred in extract_schema_columns: {e}")
        raise NetworkSecurityException(f"Invalid schema format: {e}", sys)


class DataValidation:
    """
    DataValidation handles the verification and correction of input data against a predefined schema,
    ensuring high data quality and consistency.

    Attributes:
        data_ingestion_artifact (DataIngestionArtifact): Object containing data ingestion details.
        data_validation_config (DataValidationConfig): Configuration for data validation processes.
    """

    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        """
        Initializes DataValidation with data ingestion artifacts and validation configurations.

        Args:
            data_ingestion_artifact (DataIngestionArtifact): Data ingestion details.
            data_validation_config (DataValidationConfig): Configuration for data validation.
        """
        try:
            logging.info("Initializing DataValidation class.")
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            self._schema_columns = extract_schema_columns(self._schema_config)
        except Exception as e:
            logging.error(f"Error initializing DataValidation: {e}")
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """
        Reads data from a CSV file into a DataFrame.

        Args:
            file_path (str): Path to the CSV file.

        Returns:
            pd.DataFrame: Loaded data as a DataFrame.

        Raises:
            NetworkSecurityException: If the file cannot be read.
        """
        try:
            logging.info(f"Reading data from file: {file_path}")
            return pd.read_csv(file_path)
        except Exception as e:
            logging.error(f"Error reading data from {file_path}: {e}")
            raise NetworkSecurityException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        """
        Validates if the DataFrame has the correct number of columns based on the schema.

        Args:
            dataframe (pd.DataFrame): DataFrame to validate.

        Returns:
            bool: True if the DataFrame matches the schema, False otherwise.
        """
        try:
            logging.info("Validating number of columns in DataFrame.")
            required_columns = set(self._schema_columns.keys())
            actual_columns = set(dataframe.columns)

            logging.info(f"Required columns: {required_columns}")
            logging.info(f"Actual columns: {actual_columns}")

            extra_columns = actual_columns - required_columns
            if extra_columns:
                logging.warning(f"Extra columns found: {extra_columns}")
                dataframe.drop(columns=list(extra_columns), inplace=True)

            missing_columns = required_columns - actual_columns
            if missing_columns:
                logging.error(f"Missing columns: {missing_columns}")
                return False

            return len(dataframe.columns) == len(required_columns)
        except Exception as e:
            logging.error(f"Error validating number of columns: {e}")
            raise NetworkSecurityException(e, sys)

    def validate_column_data_types(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Validates and corrects column data types based on the schema.

        Args:
            dataframe (pd.DataFrame): DataFrame to validate.

        Returns:
            pd.DataFrame: DataFrame with corrected data types.
        """
        try:
            logging.info("Validating and correcting column data types.")
            for column, expected_dtype in self._schema_columns.items():
                if column in dataframe.columns:
                    try:
                        dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce')
                        dataframe[column] = dataframe[column].astype(expected_dtype)
                        logging.info(f"Column {column} converted to {expected_dtype}")
                    except Exception as e:
                        logging.error(f"Failed to convert column {column} to {expected_dtype}: {e}")
                        raise NetworkSecurityException(
                            f"Failed to convert column {column} to {expected_dtype}. Error: {e}", sys
                        )
                else:
                    logging.error(f"Column {column} is missing in the DataFrame")
                    raise NetworkSecurityException(
                        f"Column {column} is not present in the DataFrame as expected by the schema.", sys
                    )
            return dataframe
        except Exception as e:
            logging.error(f"Error validating column data types: {e}")
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold=0.05) -> bool:
        """
        Detects dataset drift by comparing column distributions between two DataFrames.

        Args:
            base_df (pd.DataFrame): Baseline DataFrame.
            current_df (pd.DataFrame): Current DataFrame.
            threshold (float): P-value threshold for drift detection.

        Returns:
            bool: True if no drift is detected, False otherwise.
        """
        try:
            logging.info("Detecting dataset drift.")
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                is_found = is_same_dist.pvalue < threshold
                report[column] = {
                    "p_value": float(is_same_dist.pvalue),
                    "drift_status": is_found
                }
                logging.info(f"Column {column}: p-value={is_same_dist.pvalue}, Drift detected={is_found}")
                if is_found:
                    logging.warning(f"Drift detected in column: {column}")
                    status = False

            drift_report_file_path = self.data_validation_config.drift_report_file_path
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
            logging.info(f"Drift detection report saved at: {drift_report_file_path}")
            return status
        except Exception as e:
            logging.error(f"Error detecting dataset drift: {e}")
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        Initiates the data validation process, including column validation, data type validation, and drift detection.

        Returns:
            DataValidationArtifact: Artifact containing validation results.
        """
        try:
            logging.info("Starting data validation process.")
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_dataframe = self.read_data(train_file_path)
            test_dataframe = self.read_data(test_file_path)

            if not self.validate_number_of_columns(train_dataframe):
                raise NetworkSecurityException("Train data has incorrect number of columns.", sys)
            if not self.validate_number_of_columns(test_dataframe):
                raise NetworkSecurityException("Test data has incorrect number of columns.", sys)

            train_dataframe = self.validate_column_data_types(train_dataframe)
            test_dataframe = self.validate_column_data_types(test_dataframe)

            status = self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)

            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)
            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            logging.info("Data validation process completed successfully.")
            return data_validation_artifact
        except Exception as e:
            logging.error(f"Error during data validation process: {e}")
            raise NetworkSecurityException(e, sys)
