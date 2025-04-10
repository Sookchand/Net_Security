from dotenv import load_dotenv
import os
import sys
import json

# Load the .env file
load_dotenv()

# Get the MongoDB URL from the environment variables
MONGO_BD_URL = os.getenv("MONGO_DB_URL")
if not MONGO_BD_URL:
    raise ValueError("MONGO_DB_URL is not set in the .env file or environment variables.")

import certifi
ca = certifi.where()

import numpy as np
import pandas as pd
import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkDataExtract():
    def __init__(self, mongo_url):
        try:
            logging.info("Initializing NetworkDataExtract class.")
            self.mongo_url = mongo_url  # Store the MongoDB URL as an instance variable
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def csv_to_json_convertor(self, file_path):
        try:
            logging.info(f"Converting CSV file at {file_path} to JSON format.")
            data = pd.read_csv(file_path)
            logging.info(f"CSV file loaded successfully. Shape of data: {data.shape}")
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            logging.info(f"CSV file successfully converted to JSON. Total records: {len(records)}")
            return records
        except Exception as e:
            logging.error(f"Error occurred while converting CSV to JSON: {e}")
            raise NetworkSecurityException(e, sys)
        
    def insert_data_mongodb(self, records, database, collection):
        try:
            logging.info(f"Connecting to MongoDB database: {database}, collection: {collection}")
            self.mongo_client = pymongo.MongoClient(self.mongo_url)  # Use the instance variable
            self.database = self.mongo_client[database]
            self.collection = self.database[collection]
            
            logging.info(f"Inserting {len(records)} records into MongoDB.")
            result = self.collection.insert_many(records)
            logging.info(f"Data successfully inserted into MongoDB. Inserted IDs: {result.inserted_ids}")
            return len(result.inserted_ids)
        except Exception as e:
            logging.error(f"Error occurred while inserting data into MongoDB: {e}")
            raise NetworkSecurityException(e, sys)

if __name__ == '__main__':
    try:
        logging.info("Starting the data processing script.")
        FILE_PATH = "Network_Data\\phisingData.csv"
        DATABASE = "SookchandAI"
        COLLECTION = "NetworkData"
        
        # Pass the MongoDB URL to the class constructor
        networkobj = NetworkDataExtract(mongo_url=MONGO_BD_URL)
        logging.info("Created NetworkDataExtract object.")
        
        records = networkobj.csv_to_json_convertor(file_path=FILE_PATH)
        logging.info(f"Records extracted: {len(records)}")
        
        no_of_records = networkobj.insert_data_mongodb(records, DATABASE, COLLECTION)
        logging.info(f"Number of records inserted into MongoDB: {no_of_records}")
        
        logging.info("Data processing completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred in the main script: {e}")
        raise NetworkSecurityException(e, sys)
    finally:
        try:
            if 'networkobj' in locals() and hasattr(networkobj, 'mongo_client'):
                networkobj.mongo_client.close()
                logging.info("MongoDB connection closed.")
        except Exception as e:
            logging.error(f"Error occurred while closing MongoDB connection: {e}")
            raise NetworkSecurityException(e, sys)