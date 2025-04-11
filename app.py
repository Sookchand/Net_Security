import sys
import os

import certifi

ca = certifi.where()

from dotenv import load_dotenv

load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
# print(mongo_db_url)
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.entity.config_entity import TrainingPipelineConfig

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from uvicorn import run as app_run
from fastapi.responses import Response, StreamingResponse
from starlette.responses import RedirectResponse
import pandas as pd
import asyncio

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./templates")


@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


# Global variable to store progress messages


@app.get("/train")
async def train_route():
    try:
        # Create training pipeline config
        training_pipeline_config = TrainingPipelineConfig()
        
        # Initialize and run pipeline with config
        pipeline = TrainingPipeline(training_pipeline_config=training_pipeline_config)
        
        logging.info("Starting pipeline execution from API endpoint")
        model_trainer_artifact = pipeline.run_pipeline()
        
        return {"status": "Training completed successfully", "artifact": str(model_trainer_artifact)}
    except Exception as e:
        logging.error(f"Error in training route: {str(e)}")
        return {"error": str(e)}
    
# progress_messages = []

# @app.get("/train")
# async def train_route():
#     try:
#         global progress_messages
#         progress_messages.clear()  # Clear previous messages
#         progress_messages.append("Training initiated.")
#         train_pipeline = TrainingPipeline(progress_callback=progress_messages.append)
#         train_pipeline.run_pipeline()
#         progress_messages.append("Training completed successfully.")
#         return Response("Training is successful")
#     except Exception as e:
#         progress_messages.append(f"Error during training: {e}")
#         raise NetworkSecurityException(e, sys)


@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        # Validate file format
        if not file.filename.endswith(".csv"):
            return Response("Invalid file format. Please upload a CSV file.", status_code=400)

        # Load the uploaded file into a DataFrame
        df = pd.read_csv(file.file)

        # Check if model files exist
        if not os.path.exists("final_model/preprocessor.pkl") or not os.path.exists("final_model/model.pkl"):
            return Response("Model files are missing. Please train the model first.", status_code=500)

        # Load preprocessor and model
        preprocesor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)

        # Make predictions
        y_pred = network_model.predict(df)
        df["predicted_column"] = y_pred

        # Save predictions to a CSV file
        df.to_csv("prediction_output/output.csv", index=False)

        # Render predictions as an HTML table
        table_html = df.to_html(classes="table table-striped")
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})

    except Exception as e:
        logging.error(f"Error in prediction: {e}")
        return Response(f"An error occurred: {str(e)}", status_code=500)

if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)
    