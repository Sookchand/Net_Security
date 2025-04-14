import sys
import os
import certifi
from dotenv import load_dotenv
import pymongo
import pandas as pd
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, JSONResponse
from starlette.responses import RedirectResponse
from uvicorn import run as app_run

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.entity.config_entity import TrainingPipelineConfig
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.constant.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME
)

# Environment and MongoDB setup
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
ca = certifi.where()

# Initialize MongoDB client
client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

# Initialize ECR client
try:
    ecr_client = boto3.client('ecr', region_name=os.getenv('AWS_REGION'))
except Exception as e:
    logging.error(f"Failed to initialize ECR client: {str(e)}")
    ecr_client = None

# FastAPI app setup
app = FastAPI(title="Network Security API")
origins = ["*"]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates setup
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["system"])
async def health_check():
    """Check system health including ECR and MongoDB connections"""
    health_status = {
        "status": "checking",
        "mongo": "unknown",
        "ecr": "unknown",
        "model_files": {
            "preprocessor": os.path.exists("final_model/preprocessor.pkl"),
            "model": os.path.exists("final_model/model.pkl")
        }
    }
    
    # Check MongoDB
    try:
        client.server_info()
        health_status["mongo"] = "connected"
    except Exception as e:
        health_status["mongo"] = f"error: {str(e)}"
        logging.error(f"MongoDB connection error: {str(e)}")

    # Check ECR
    try:
        if ecr_client:
            ecr_client.describe_repositories(
                repositoryNames=[os.getenv('ECR_REPOSITORY_NAME')]
            )
            health_status["ecr"] = "connected"
    except Exception as e:
        health_status["ecr"] = f"error: {str(e)}"
        logging.error(f"ECR connection error: {str(e)}")

    health_status["status"] = "healthy" if all(
        x == "connected" for x in [health_status["mongo"], health_status["ecr"]]
    ) else "unhealthy"
    
    return health_status

@app.get("/train", tags=["training"])
async def train_route():
    """Train the network security model"""
    try:
        training_pipeline_config = TrainingPipelineConfig()
        pipeline = TrainingPipeline(training_pipeline_config=training_pipeline_config)
        
        logging.info("Starting pipeline execution from API endpoint")
        model_trainer_artifact = pipeline.run_pipeline()
        
        return {
            "status": "success",
            "message": "Training completed successfully",
            "artifact": str(model_trainer_artifact)
        }
    except Exception as e:
        logging.error(f"Error in training route: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/predict", tags=["prediction"])
async def predict_route(request: Request, file: UploadFile = File(...)):
    """Make predictions on uploaded data"""
    try:
        # Create required directories
        os.makedirs("final_model", exist_ok=True)
        os.makedirs("prediction_output", exist_ok=True)

        # Validate file format
        if not file.filename.endswith(".csv"):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid file format. Please upload a CSV file."
                }
            )

        # Load and validate data
        try:
            df = pd.read_csv(file.file)
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Error reading CSV file: {str(e)}"
                }
            )

        # Check model files
        model_files = ["preprocessor.pkl", "model.pkl"]
        missing_files = [f for f in model_files if not os.path.exists(f"final_model/{f}")]
        if missing_files:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Missing model files: {', '.join(missing_files)}. Please train the model first."
                }
            )

        # Load model and make predictions
        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)

        # Generate predictions
        y_pred = network_model.predict(df)
        df["predicted_column"] = y_pred

        # Save predictions
        output_path = "prediction_output/output.csv"
        df.to_csv(output_path, index=False)

        # Return results
        table_html = df.to_html(classes="table table-striped")
        return templates.TemplateResponse(
            "table.html",
            {"request": request, "table": table_html}
        )

    except Exception as e:
        logging.error(f"Error in prediction: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )

if __name__ == "__main__":
    try:
        host = os.getenv("HOST", "0.0.0.0/0")
        port = int(os.getenv("PORT", 8000))
        logging.info(f"Starting server on {host}:{port}")
        app_run(app, host=host, port=port)
    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")
        sys.exit(1)