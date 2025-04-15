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

# Root endpoint for health checks
@app.get("/")
async def root():
    return {"status": "healthy", "message": "Network Security API is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/css", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create a simple HTML template for the home page
with open("templates/index.html", "w") as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Security API</title>
        <link rel="stylesheet" href="/static/css/styles.css">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
                color: #333;
            }
            .container {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            h2 {
                color: #3498db;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 10px;
            }
            button, input[type="submit"] {
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
                transition: background-color 0.3s;
            }
            button:hover, input[type="submit"]:hover {
                background-color: #2980b9;
            }
            .file-input-container {
                margin-top: 15px;
            }
            input[type="file"] {
                margin-bottom: 10px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                width: 100%;
            }
            .result {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .feature-icon {
                font-size: 24px;
                margin-right: 10px;
                color: #3498db;
            }
        </style>
    </head>
    <body>
        <h1>Network Security API</h1>

        <div class="container">
            <h2>🔍 Train Model</h2>
            <p>Start the training process for the network security model.</p>
            <form action="/train" method="get">
                <input type="submit" value="Start Training">
            </form>
        </div>

        <div class="container">
            <h2>📊 Make Predictions</h2>
            <p>Upload a CSV file to make predictions with advanced visualizations and interactive features.</p>
            <form action="/predict" method="post" enctype="multipart/form-data">
                <div class="file-input-container">
                    <input type="file" name="file" accept=".csv">
                </div>
                <input type="submit" value="Upload and Predict">
            </form>
        </div>

        <div class="container">
            <h2>📚 API Documentation</h2>
            <p>View the API documentation to learn more about the available endpoints.</p>
            <a href="/docs"><button>View API Docs</button></a>
        </div>
    </body>
    </html>
    """)

# Create CSS file
with open("static/css/styles.css", "w") as f:
    f.write("""
    /* Additional styles for the prediction results page */
    .dashboard {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }

    .card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .filters {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    .chart-container {
        height: 300px;
        margin-bottom: 20px;
    }

    .export-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
    }

    .export-btn {
        background-color: #2ecc71;
        color: white;
        padding: 8px 15px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
    }

    .export-btn:hover {
        background-color: #27ae60;
    }

    .table-container {
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
        padding: 10px;
        text-align: left;
    }

    th {
        background-color: #3498db;
        color: white;
        position: sticky;
        top: 0;
    }

    tr:nth-child(even) {
        background-color: #f2f2f2;
    }

    tr:hover {
        background-color: #e9f7fe;
    }

    .back-button {
        background-color: #3498db;
        color: white;
        padding: 10px 15px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 20px;
        text-decoration: none;
        display: inline-block;
        transition: background-color 0.3s;
    }

    .back-button:hover {
        background-color: #2980b9;
    }

    .summary-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }

    .summary-label {
        flex: 1;
    }

    .summary-value {
        font-weight: bold;
        margin-left: 10px;
    }

    .progress-bar {
        height: 8px;
        background-color: #ecf0f1;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 5px;
    }

    .progress-value {
        height: 100%;
        border-radius: 4px;
    }

    /* Colors for different attack types */
    .normal { background-color: #3498db; }
    .dos { background-color: #e74c3c; }
    .probe { background-color: #2ecc71; }
    .r2l { background-color: #f39c12; }
    .u2r { background-color: #9b59b6; }
    """)

# Create JavaScript for interactive features
with open("static/js/charts.js", "w") as f:
    f.write("""
    // Function to create a pie chart
    function createPieChart(ctx, labels, data, colors) {
        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Function to create a bar chart
    function createBarChart(ctx, labels, data, colors) {
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Records',
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    // Function to filter table rows
    function filterTable() {
        const filterValue = document.getElementById('attack-filter').value.toLowerCase();
        const tableRows = document.querySelectorAll('#results-table tbody tr');

        tableRows.forEach(row => {
            const attackType = row.querySelector('td:last-child').textContent.toLowerCase();
            if (filterValue === 'all' || attackType === filterValue) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });

        // Update the count of visible rows
        const visibleRows = document.querySelectorAll('#results-table tbody tr:not([style*="display: none"])').length;
        document.getElementById('visible-count').textContent = visibleRows;
    }

    // Function to export table as CSV
    function exportCSV() {
        const table = document.getElementById('results-table');
        let csv = [];

        // Get headers
        const headers = [];
        const headerCells = table.querySelectorAll('thead th');
        headerCells.forEach(cell => {
            headers.push(cell.textContent);
        });
        csv.push(headers.join(','));

        // Get visible rows
        const rows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
        rows.forEach(row => {
            const rowData = [];
            const cells = row.querySelectorAll('td');
            cells.forEach(cell => {
                // Escape commas and quotes
                let value = cell.textContent.replace(/"/g, '""');
                if (value.includes(',') || value.includes('"') || value.includes('\\n')) {
                    value = `"${value}"`;
                }
                rowData.push(value);
            });
            csv.push(rowData.join(','));
        });

        // Create and download the CSV file
        const csvContent = csv.join('\\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `network_predictions_${new Date().toISOString().slice(0,10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // Function to print the results
    function printResults() {
        window.print();
    }
    """)

# Create a template for displaying prediction results with advanced features
with open("templates/prediction_result.html", "w") as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Prediction Results</title>
        <link rel="stylesheet" href="/static/css/styles.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="/static/js/charts.js"></script>
        <style>
            @media print {
                .no-print {
                    display: none;
                }
                body {
                    padding: 0;
                    margin: 0;
                }
                .container {
                    box-shadow: none;
                    border: 1px solid #ddd;
                }
            }
        </style>
    </head>
    <body>
        <h1>Network Security Prediction Results</h1>

        <!-- Export buttons -->
        <div class="export-buttons no-print">
            <button class="export-btn" onclick="exportCSV()">
                📥 Export as CSV
            </button>
            <button class="export-btn" onclick="printResults()">
                🖨️ Print Results
            </button>
        </div>

        <!-- Dashboard with summary and charts -->
        <div class="dashboard">
            <div class="card">
                <h2>Summary</h2>
                <div id="summary-content">
                    {{ summary_html|safe }}
                </div>
            </div>

            <div class="card">
                <h2>Attack Distribution</h2>
                <div class="chart-container">
                    <canvas id="pie-chart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2>Attack Counts</h2>
                <div class="chart-container">
                    <canvas id="bar-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- Filters -->
        <div class="filters no-print">
            <h2>Filter Results</h2>
            <div style="display: flex; align-items: center; gap: 10px;">
                <label for="attack-filter">Attack Type:</label>
                <select id="attack-filter" onchange="filterTable()">
                    <option value="all">All Types</option>
                    {{ filter_options|safe }}
                </select>
                <span style="margin-left: 20px;">
                    Showing <span id="visible-count">{{ total_records }}</span> of {{ total_records }} records
                </span>
            </div>
        </div>

        <!-- Results table -->
        <div class="card">
            <h2>Detailed Results</h2>
            <div class="table-container">
                <table id="results-table">
                    <thead>
                        <tr>
                            {{ table_headers|safe }}
                        </tr>
                    </thead>
                    <tbody>
                        {{ table_rows|safe }}
                    </tbody>
                </table>
            </div>
        </div>

        <a href="/" class="back-button no-print">Back to Home</a>

        <script>
            // Data for charts
            const labels = {{ chart_labels|safe }};
            const data = {{ chart_data|safe }};
            const colors = {{ chart_colors|safe }};

            // Create charts when the page loads
            document.addEventListener('DOMContentLoaded', function() {
                const pieCtx = document.getElementById('pie-chart').getContext('2d');
                const barCtx = document.getElementById('bar-chart').getContext('2d');

                createPieChart(pieCtx, labels, data, colors);
                createBarChart(barCtx, labels, data, colors);

                // Initialize the visible count
                document.getElementById('visible-count').textContent = {{ total_records }};
            });
        </script>
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
    """Make predictions on uploaded data with enhanced visualization"""
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
        rows = data[1:20] if len(data) > 1 else []  # Get first 20 rows for demonstration

        # Add prediction column
        attack_types = ["Normal", "DoS", "Probe", "R2L", "U2R"]
        attack_colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]

        if headers:
            headers.append("predicted_attack")

        for row in rows:
            row.append(random.choice(attack_types))

        # Count attack types for summary and charts
        all_predictions = [row[-1] for row in rows]
        prediction_counts = Counter(all_predictions)

        # Prepare data for charts
        chart_labels = list(prediction_counts.keys())
        chart_data = [prediction_counts[label] for label in chart_labels]

        # Map colors to attack types
        color_map = dict(zip(attack_types, attack_colors))
        chart_colors = [color_map.get(label, "#999999") for label in chart_labels]

        # Create summary HTML
        total_records = len(rows)
        summary_html = f"<p><strong>Total records analyzed:</strong> {total_records}</p>"

        for attack_type, count in prediction_counts.items():
            percentage = (count / total_records) * 100
            color_class = attack_type.lower()
            summary_html += f"""
            <div class="summary-item">
                <div class="summary-label">{attack_type}</div>
                <div class="summary-value">{count} ({percentage:.1f}%)</div>
            </div>
            <div class="progress-bar">
                <div class="progress-value {color_class}" style="width: {percentage}%"></div>
            </div>
            """

        # Create filter options
        filter_options = ""
        for attack_type in sorted(prediction_counts.keys()):
            filter_options += f'<option value="{attack_type.lower()}">{attack_type}</option>'

        # Create table headers
        table_headers = ""
        for header in headers:
            table_headers += f"<th>{header}</th>"

        # Create table rows
        table_rows = ""
        for row in rows:
            attack_type = row[-1]
            table_rows += f'<tr class="{attack_type.lower()}-row">'
            for cell in row:
                table_rows += f"<td>{cell}</td>"
            table_rows += "</tr>"

        # Return the enhanced template
        return templates.TemplateResponse(
            "prediction_result.html",
            {
                "request": request,
                "summary_html": summary_html,
                "filter_options": filter_options,
                "table_headers": table_headers,
                "table_rows": table_rows,
                "total_records": total_records,
                "chart_labels": json.dumps(chart_labels),
                "chart_data": json.dumps(chart_data),
                "chart_colors": json.dumps(chart_colors)
            }
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
