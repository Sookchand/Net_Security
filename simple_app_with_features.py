from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
import json
import pandas as pd
from typing import Optional, List

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

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Create a simple HTML template for the home page
with open("templates/index.html", "w") as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Security API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .container {
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 20px;
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
            }
            button, input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover, input[type="submit"]:hover {
                background-color: #45a049;
            }
            .result {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <h1>Network Security API</h1>
        
        <div class="container">
            <h2>Train Model</h2>
            <p>Start the training process for the network security model.</p>
            <form action="/train" method="get">
                <input type="submit" value="Start Training">
            </form>
        </div>
        
        <div class="container">
            <h2>Make Predictions</h2>
            <p>Upload a CSV file to make predictions.</p>
            <form action="/predict" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".csv">
                <input type="submit" value="Upload and Predict">
            </form>
        </div>
        
        <div class="container">
            <h2>API Documentation</h2>
            <p>View the API documentation to learn more about the available endpoints.</p>
            <a href="/docs"><button>View API Docs</button></a>
        </div>
    </body>
    </html>
    """)

# Create a template for displaying prediction results
with open("templates/prediction_result.html", "w") as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Prediction Results</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .container {
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 20px;
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #4CAF50;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .back-button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 20px;
                text-decoration: none;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <h1>Prediction Results</h1>
        <div class="container">
            {{ table|safe }}
        </div>
        <a href="/" class="back-button">Back to Home</a>
    </body>
    </html>
    """)

# Templates setup
templates = Jinja2Templates(directory="templates")

class PredictionInput(BaseModel):
    data: List[dict]

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health_check():
    """Check system health"""
    return {"status": "healthy"}

@app.get("/train")
def train_route():
    """Train the network security model (simulated)"""
    # In a real implementation, this would start the training process
    # For now, we'll just return a success message
    return {
        "status": "success",
        "message": "Training process started. This is a simulation as the actual training components are not available in this simplified version."
    }

@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    """Make predictions on uploaded data (simulated)"""
    try:
        # Validate file format
        if not file.filename.endswith(".csv"):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid file format. Please upload a CSV file."
                }
            )

        # Read the CSV file
        content = await file.read()
        with open("temp.csv", "wb") as f:
            f.write(content)
        
        try:
            df = pd.read_csv("temp.csv")
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Error reading CSV file: {str(e)}"
                }
            )

        # In a real implementation, this would use the model to make predictions
        # For now, we'll just add a random prediction column
        import random
        attack_types = ["Normal", "DoS", "Probe", "R2L", "U2R"]
        df["predicted_attack"] = [random.choice(attack_types) for _ in range(len(df))]
        
        # Convert to HTML table
        table_html = df.head(10).to_html(classes="table table-striped")
        
        # Return the results
        return templates.TemplateResponse(
            "prediction_result.html",
            {"request": request, "table": table_html}
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
