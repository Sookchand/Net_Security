from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import json
import csv
import random
import base64
import io
import datetime
from io import StringIO
from typing import Optional, List, Dict
from collections import Counter

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
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }
            .container {
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 20px;
                margin-bottom: 20px;
            }
            h1, h2 {
                color: #333;
            }
            h2 {
                margin-top: 20px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
            }
            /* Table styles */
            .table-container {
                margin-top: 30px;
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                font-size: 14px;
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
            /* Summary styles */
            .summary {
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .summary ul {
                list-style-type: none;
                padding-left: 0;
            }
            .summary li {
                margin-bottom: 5px;
                padding: 5px;
                border-radius: 3px;
            }
            .summary li:nth-child(odd) {
                background-color: rgba(0,0,0,0.05);
            }
            /* Chart styles */
            .chart-container {
                margin: 20px 0;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }
            .chart {
                display: flex;
                align-items: flex-end;
                justify-content: space-around;
                height: 250px;
                margin-top: 20px;
                padding-bottom: 30px;
                border-bottom: 1px solid #ddd;
            }
            .chart-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 60px;
            }
            .bar {
                width: 40px;
                background-color: #4CAF50;
                border-radius: 4px 4px 0 0;
                transition: height 0.5s ease;
            }
            .bar-label {
                margin-bottom: 5px;
                font-size: 12px;
                text-align: center;
                transform: rotate(-45deg);
                white-space: nowrap;
                position: absolute;
                bottom: 0;
            }
            .bar-value {
                margin-top: 5px;
                font-weight: bold;
            }
            /* Button styles */
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
            .back-button:hover {
                background-color: #45a049;
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
        content_str = content.decode('utf-8')
        csv_reader = csv.reader(StringIO(content_str))

        # Convert to list of lists
        data = list(csv_reader)
        headers = data[0] if data else []
        rows = data[1:10] if len(data) > 1 else []  # Get first 10 rows

        # Add prediction column
        import random
        attack_types = ["Normal", "DoS", "Probe", "R2L", "U2R"]

        if headers:
            headers.append("predicted_attack")

        for row in rows:
            row.append(random.choice(attack_types))

        # Count attack types for summary and chart
        all_predictions = [row[-1] for row in rows]  # Get all predictions
        prediction_counts = Counter(all_predictions)

        # Create summary text
        total_records = len(rows)
        summary_html = f"<div class='summary'><h2>Prediction Summary</h2>"
        summary_html += f"<p>Total records analyzed: {total_records}</p>"
        summary_html += "<ul>"
        for attack_type, count in prediction_counts.items():
            percentage = (count / total_records) * 100
            summary_html += f"<li>{attack_type}: {count} ({percentage:.1f}%)</li>"
        summary_html += "</ul></div>"

        # Create bar chart
        chart_html = "<div class='chart-container'><h2>Attack Distribution</h2>"
        chart_html += "<div class='chart'>"

        # Calculate the maximum count for scaling
        max_count = max(prediction_counts.values()) if prediction_counts else 1

        # Generate bars for each attack type
        for attack_type, count in prediction_counts.items():
            percentage = (count / total_records) * 100
            bar_height = (count / max_count) * 200  # Scale to max height of 200px
            chart_html += f"""
            <div class='chart-item'>
                <div class='bar-label'>{attack_type}</div>
                <div class='bar' style='height: {bar_height}px;' title='{count} records ({percentage:.1f}%)'></div>
                <div class='bar-value'>{count}</div>
            </div>"""

        chart_html += "</div></div>"

        # Create HTML table
        table_html = "<div class='table-container'><h2>Detailed Results</h2><table><tr>"
        for header in headers:
            table_html += f"<th>{header}</th>"
        table_html += "</tr>"

        for row in rows:
            table_html += "<tr>"
            for cell in row:
                table_html += f"<td>{cell}</td>"
            table_html += "</tr>"
        table_html += "</table></div>"

        # Combine all elements
        content_html = f"{summary_html}{chart_html}{table_html}"

        # Return the results
        return templates.TemplateResponse(
            "prediction_result.html",
            {"request": request, "table": content_html}
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
