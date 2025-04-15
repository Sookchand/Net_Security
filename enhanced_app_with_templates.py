from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import uvicorn
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
import random
import pickle
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model drift helper functions
def get_latest_model_drift_report() -> Optional[Dict[str, Any]]:
    """Get the latest model drift report"""
    try:
        # Check if sample report exists
        report_path = os.path.join("app", "static", "model_drift_report.json")
        logger.info(f"Looking for model drift report at: {report_path}")
        logger.info(f"File exists: {os.path.exists(report_path)}")

        if os.path.exists(report_path):
            try:
                with open(report_path, "r") as f:
                    report_data = json.load(f)
                    logger.info(f"Successfully loaded model drift report")
                    return report_data
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing model drift report JSON: {e}")
                # Return a minimal valid report
                return {
                    "timestamp": datetime.now().isoformat(),
                    "baseline_model_path": "unknown",
                    "current_model_path": "unknown",
                    "drift_detected": False,
                    "text_report_path": "",
                    "message": f"Error parsing report: {str(e)}"
                }

        # If no report exists, return None
        logger.warning("No model drift report found")
        return None
    except Exception as e:
        logger.error(f"Error getting latest model drift report: {e}")
        # Return a minimal valid report instead of None
        return {
            "timestamp": datetime.now().isoformat(),
            "baseline_model_path": "unknown",
            "current_model_path": "unknown",
            "drift_detected": False,
            "text_report_path": "",
            "message": f"Error: {str(e)}"
        }

def generate_data_drift_text_report(data_drift_report):
    """Generate a text-based data drift report"""
    try:
        # Create report header
        report = [
            "====================================================",
            "               DATA DRIFT REPORT                 ",
            "====================================================",
            f"Report generated: {data_drift_report['timestamp']}",
            f"Drift threshold: {data_drift_report['threshold']}",
            "====================================================",
            ""
        ]

        # Add drift summary
        report.append("DRIFT SUMMARY:")
        report.append("-" * 50)
        if data_drift_report["drift_detected"]:
            report.append("WARNING: DATA DRIFT DETECTED")
            report.append("")
            report.append("The following features show significant drift:")

            for feature in data_drift_report["features_with_drift"]:
                drift_score = data_drift_report["drift_scores"].get(feature, 0)
                report.append(f"  - {feature}: {drift_score:.4f}")
        else:
            report.append("NO SIGNIFICANT DATA DRIFT DETECTED")
            report.append("")
            report.append("All features are within acceptable thresholds.")

        report.append("-" * 50)
        report.append("")

        # Add recommendations
        report.append("RECOMMENDATIONS:")
        report.append("-" * 50)
        if data_drift_report["drift_detected"]:
            report.append("1. Investigate the cause of data distribution changes")
            report.append("2. Consider retraining the model with more recent data")
            report.append("3. Review feature engineering and preprocessing steps")
            report.append("4. Monitor the affected features more closely")
        else:
            report.append("1. Continue monitoring data distributions")
            report.append("2. No immediate action required")

        report.append("-" * 50)

        # Join report lines
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Error generating data drift text report: {e}")
        return f"Error generating data drift text report: {str(e)}"

def generate_sample_model_drift_report():
    """Generate a sample model drift report for demonstration purposes"""
    try:
        # Create sample visualizations
        images_dir = os.path.join("app", "static", "images", "model_drift")
        os.makedirs(images_dir, exist_ok=True)

        # Run the sample image generation script if it exists
        script_path = os.path.join(images_dir, "generate_sample_images.py")
        if os.path.exists(script_path):
            import subprocess
            subprocess.run([sys.executable, script_path], cwd=images_dir)
            logger.info("Generated sample model drift images")

        # Create sample report
        report = {
            "timestamp": datetime.now().isoformat(),
            "baseline_model_path": "final_model/model.pkl",
            "current_model_path": "Artifacts/04_15_2025_11_30_00/model_trainer/trained_model/model.pkl",
            "baseline_metrics": {
                "accuracy": 0.92,
                "precision": 0.89,
                "recall": 0.87,
                "f1": 0.88,
                "auc": 0.95,
                "classification_report": {
                    "0": {"precision": 0.94, "recall": 0.92, "f1-score": 0.93, "support": 450},
                    "1": {"precision": 0.90, "recall": 0.92, "f1-score": 0.91, "support": 380},
                    "2": {"precision": 0.88, "recall": 0.86, "f1-score": 0.87, "support": 320},
                    "3": {"precision": 0.85, "recall": 0.84, "f1-score": 0.84, "support": 230},
                    "accuracy": 0.92,
                    "macro avg": {"precision": 0.89, "recall": 0.88, "f1-score": 0.89, "support": 1380},
                    "weighted avg": {"precision": 0.90, "recall": 0.92, "f1-score": 0.91, "support": 1380}
                },
                "confusion_matrix": [
                    [450, 30, 15, 5],
                    [25, 380, 10, 5],
                    [10, 15, 320, 5],
                    [5, 5, 10, 230]
                ]
            },
            "current_metrics": {
                "accuracy": 0.90,
                "precision": 0.86,
                "recall": 0.85,
                "f1": 0.85,
                "auc": 0.94,
                "classification_report": {
                    "0": {"precision": 0.92, "recall": 0.90, "f1-score": 0.91, "support": 450},
                    "1": {"precision": 0.88, "recall": 0.90, "f1-score": 0.89, "support": 380},
                    "2": {"precision": 0.85, "recall": 0.84, "f1-score": 0.84, "support": 320},
                    "3": {"precision": 0.82, "recall": 0.81, "f1-score": 0.81, "support": 230},
                    "accuracy": 0.90,
                    "macro avg": {"precision": 0.87, "recall": 0.86, "f1-score": 0.86, "support": 1380},
                    "weighted avg": {"precision": 0.88, "recall": 0.90, "f1-score": 0.89, "support": 1380}
                },
                "confusion_matrix": [
                    [440, 35, 20, 5],
                    [30, 370, 15, 5],
                    [15, 20, 310, 5],
                    [10, 5, 15, 220]
                ]
            },
            "metric_differences": {
                "accuracy": -0.02,
                "precision": -0.03,
                "recall": -0.02,
                "f1": -0.03,
                "auc": -0.01
            },
            "drift_detected": True,
            "drift_details": {
                "accuracy": {
                    "difference": -0.02,
                    "is_significant": False,
                    "is_degradation": True,
                    "status": "stable"
                },
                "precision": {
                    "difference": -0.03,
                    "is_significant": False,
                    "is_degradation": True,
                    "status": "stable"
                },
                "recall": {
                    "difference": -0.02,
                    "is_significant": False,
                    "is_degradation": True,
                    "status": "stable"
                },
                "f1": {
                    "difference": -0.03,
                    "is_significant": False,
                    "is_degradation": True,
                    "status": "stable"
                },
                "auc": {
                    "difference": -0.01,
                    "is_significant": False,
                    "is_degradation": True,
                    "status": "stable"
                }
            }
        }

        # Save report
        report_path = os.path.join("app", "static", "model_drift_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Generated sample model drift report at {report_path}")
        return report
    except Exception as e:
        logger.error(f"Error generating sample model drift report: {e}")
        raise

# FastAPI app setup
app = FastAPI(title="Network Security API")
origins = ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Sample attack types
ATTACK_TYPES = ["Normal", "DoS", "Probe", "R2L", "U2R"]

# Root endpoint for health checks
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    """Render the prediction page"""
    return templates.TemplateResponse("predict.html", {"request": request})

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Make predictions on network traffic data
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        with open("temp_upload.csv", "wb") as f:
            f.write(contents)

        # Load the data
        df = pd.read_csv("temp_upload.csv")

        # Generate simulated predictions
        predictions = []
        for _ in range(len(df)):
            # Simulate predictions with a bias towards Normal
            attack_type = random.choices(
                ATTACK_TYPES,
                weights=[0.7, 0.1, 0.1, 0.05, 0.05],
                k=1
            )[0]
            predictions.append(attack_type)

        # Add predictions to the dataframe
        df["predicted_attack"] = predictions

        # Count attack types
        attack_counts = df["predicted_attack"].value_counts().to_dict()

        # Calculate statistics
        total_records = len(df)
        total_attacks = sum(count for attack_type, count in attack_counts.items() if attack_type != "Normal")
        attack_percentage = (total_attacks / total_records) * 100 if total_records > 0 else 0

        # Generate a threat score (0-100)
        threat_score = min(100, int(attack_percentage * 1.5))

        # Create a summary
        if threat_score < 10:
            summary = "No significant threats detected in the network traffic."
        elif threat_score < 30:
            summary = "Low level of potential threats detected. Routine monitoring recommended."
        elif threat_score < 60:
            summary = "Moderate level of threats detected. Investigation recommended."
        else:
            summary = "High level of threats detected! Immediate investigation required."

        # Create recommendations based on threat score
        recommendations = []
        if threat_score > 0:
            recommendations.append("Review security logs for suspicious activities")
        if threat_score > 20:
            recommendations.append("Update firewall rules to block suspicious IP addresses")
        if threat_score > 40:
            recommendations.append("Implement additional network monitoring")
        if threat_score > 60:
            recommendations.append("Isolate affected systems for further investigation")
        if threat_score > 80:
            recommendations.append("Engage security incident response team immediately")

        # Create response
        response = {
            "status": "success",
            "prediction_summary": {
                "total_records": total_records,
                "total_attacks": total_attacks,
                "attack_percentage": round(attack_percentage, 2),
                "threat_score": threat_score,
                "attack_distribution": attack_counts
            },
            "analysis": {
                "summary": summary,
                "recommendations": recommendations
            },
            "data_preview": df.head(10).to_dict(orient="records")
        }

        return response

    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/predict-sample")
async def predict_sample():
    """
    Make predictions on sample data
    """
    try:
        # Create sample data
        data = {
            "duration": np.random.randint(1, 100, 100),
            "protocol_type": np.random.choice(["tcp", "udp", "icmp"], 100),
            "service": np.random.choice(["http", "ftp", "smtp", "ssh"], 100),
            "flag": np.random.choice(["SF", "REJ", "S0"], 100),
            "src_bytes": np.random.randint(100, 10000, 100),
            "dst_bytes": np.random.randint(100, 10000, 100),
        }

        df = pd.DataFrame(data)

        # Generate simulated predictions
        predictions = []
        for _ in range(len(df)):
            # Simulate predictions with a bias towards Normal
            attack_type = random.choices(
                ATTACK_TYPES,
                weights=[0.7, 0.1, 0.1, 0.05, 0.05],
                k=1
            )[0]
            predictions.append(attack_type)

        # Add predictions to the dataframe
        df["predicted_attack"] = predictions

        # Count attack types
        attack_counts = df["predicted_attack"].value_counts().to_dict()

        # Calculate statistics
        total_records = len(df)
        total_attacks = sum(count for attack_type, count in attack_counts.items() if attack_type != "Normal")
        attack_percentage = (total_attacks / total_records) * 100 if total_records > 0 else 0

        # Generate a threat score (0-100)
        threat_score = min(100, int(attack_percentage * 1.5))

        # Create a summary
        if threat_score < 10:
            summary = "No significant threats detected in the network traffic."
        elif threat_score < 30:
            summary = "Low level of potential threats detected. Routine monitoring recommended."
        elif threat_score < 60:
            summary = "Moderate level of threats detected. Investigation recommended."
        else:
            summary = "High level of threats detected! Immediate investigation required."

        # Create recommendations based on threat score
        recommendations = []
        if threat_score > 0:
            recommendations.append("Review security logs for suspicious activities")
        if threat_score > 20:
            recommendations.append("Update firewall rules to block suspicious IP addresses")
        if threat_score > 40:
            recommendations.append("Implement additional network monitoring")
        if threat_score > 60:
            recommendations.append("Isolate affected systems for further investigation")
        if threat_score > 80:
            recommendations.append("Engage security incident response team immediately")

        # Create response
        response = {
            "status": "success",
            "prediction_summary": {
                "total_records": total_records,
                "total_attacks": total_attacks,
                "attack_percentage": round(attack_percentage, 2),
                "threat_score": threat_score,
                "attack_distribution": attack_counts
            },
            "analysis": {
                "summary": summary,
                "recommendations": recommendations
            },
            "data_preview": df.head(10).to_dict(orient="records")
        }

        return response

    except Exception as e:
        logger.error(f"Error in sample prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing sample data: {str(e)}")

@app.get("/text-analysis", response_class=HTMLResponse)
async def text_analysis_page(request: Request):
    """Render the email & text threat analysis page"""
    return templates.TemplateResponse("text_analysis.html", {"request": request})

@app.post("/analyze-text")
async def analyze_text(request: Request):
    """Analyze text content for security threats"""
    try:
        # Parse the request body
        body = await request.json()
        text_content = body.get("text_content")

        if not text_content:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Text content is required"
                }
            )

        # Check for common phishing indicators
        phishing_score = 0
        malware_score = 0
        social_engineering_score = 0
        spam_score = 0
        scam_score = 0

        # Simple keyword-based analysis
        phishing_keywords = ["verify your account", "confirm your identity", "update your information",
                            "click here", "login to your account", "unusual activity", "suspended"]

        malware_keywords = ["attachment", "download", "execute", "invoice", "doc file", "zip file",
                           "enable macros", "enable content"]

        social_engineering_keywords = ["urgent", "immediate action", "limited time", "act now",
                                      "important notice", "security alert", "problem with your account"]

        spam_keywords = ["offer", "free", "discount", "save money", "best price", "buy now",
                        "limited offer", "exclusive deal"]

        scam_keywords = ["lottery", "winner", "inheritance", "million dollars", "prince", "overseas",
                        "transaction", "wire transfer", "western union"]

        # Calculate scores based on keyword matches
        for keyword in phishing_keywords:
            if keyword.lower() in text_content.lower():
                phishing_score += 20

        for keyword in malware_keywords:
            if keyword.lower() in text_content.lower():
                malware_score += 20

        for keyword in social_engineering_keywords:
            if keyword.lower() in text_content.lower():
                social_engineering_score += 15

        for keyword in spam_keywords:
            if keyword.lower() in text_content.lower():
                spam_score += 10

        for keyword in scam_keywords:
            if keyword.lower() in text_content.lower():
                scam_score += 25

        # Cap scores at 100
        phishing_score = min(100, phishing_score)
        malware_score = min(100, malware_score)
        social_engineering_score = min(100, social_engineering_score)
        spam_score = min(100, spam_score)
        scam_score = min(100, scam_score)

        # Calculate overall threat score
        threat_score = int((phishing_score * 0.3) + (malware_score * 0.3) +
                          (social_engineering_score * 0.2) + (spam_score * 0.1) + (scam_score * 0.1))

        # Determine threat level
        if threat_score < 20:
            threat_level = "Safe"
            summary = "The content appears to be safe with no significant security threats detected."
        elif threat_score < 40:
            threat_level = "Low Risk"
            summary = "The content has some minor indicators of suspicious activity but is likely safe."
        elif threat_score < 60:
            threat_level = "Medium Risk"
            summary = "The content contains several suspicious elements that warrant caution."
        elif threat_score < 80:
            threat_level = "High Risk"
            summary = "The content contains multiple indicators of malicious intent. Exercise extreme caution."
        else:
            threat_level = "Critical Risk"
            summary = "The content is highly likely to be malicious. Do not interact with it."

        # Generate detailed summary
        detailed_summary = f"Analysis indicates this is a {threat_level.lower()} message. "

        if phishing_score > 50:
            detailed_summary += "It contains multiple phishing indicators attempting to steal credentials or personal information. "

        if malware_score > 50:
            detailed_summary += "It likely contains or references malicious attachments or downloads. "

        if social_engineering_score > 50:
            detailed_summary += "It uses social engineering tactics to manipulate the recipient. "

        if spam_score > 50:
            detailed_summary += "It has characteristics of unsolicited commercial content. "

        if scam_score > 50:
            detailed_summary += "It shows patterns consistent with common scams. "

        # Generate threats list
        threats = []
        if phishing_score > 30:
            threats.append({
                "type": "Phishing",
                "description": "Attempts to steal sensitive information by impersonating a trustworthy entity"
            })

        if malware_score > 30:
            threats.append({
                "type": "Malware",
                "description": "May contain or link to malicious software that can harm your system"
            })

        if social_engineering_score > 30:
            threats.append({
                "type": "Social Engineering",
                "description": "Uses psychological manipulation to trick users into making security mistakes"
            })

        if spam_score > 50:
            threats.append({
                "type": "Spam",
                "description": "Unsolicited bulk message, typically for commercial purposes"
            })

        if scam_score > 30:
            threats.append({
                "type": "Scam",
                "description": "Fraudulent scheme designed to trick people out of money or information"
            })

        # Generate recommendations
        recommendations = ["Do not click on any links in the message"]

        if phishing_score > 30:
            recommendations.append("Do not provide any personal information or credentials")

        if malware_score > 30:
            recommendations.append("Do not download or open any attachments")

        if threat_score > 50:
            recommendations.append("Report this message to your IT security team")

        if threat_score > 70:
            recommendations.append("Delete this message immediately")

        # Create analysis result
        analysis = {
            "threat_score": threat_score,
            "summary": summary,
            "detailed_summary": detailed_summary,
            "threats": threats,
            "threat_categories": {
                "Phishing": phishing_score,
                "Malware": malware_score,
                "Social Engineering": social_engineering_score,
                "Spam": spam_score,
                "Scam": scam_score
            },
            "recommendations": recommendations
        }

        return {
            "status": "success",
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error analyzing text: {str(e)}"
            }
        )

@app.get("/architecture", response_class=HTMLResponse)
async def architecture(request: Request):
    """Render the system architecture page"""
    return templates.TemplateResponse("architecture.html", {"request": request})

@app.get("/drift-reports", response_class=HTMLResponse)
async def drift_reports_page(request: Request):
    """Render the combined drift reports page"""
    try:
        # Get model drift report
        model_drift_report = get_latest_model_drift_report()

        # Get model drift text report
        model_drift_text = ""
        if model_drift_report and "text_report_path" in model_drift_report and os.path.exists(model_drift_report["text_report_path"]):
            try:
                with open(model_drift_report["text_report_path"], "r", encoding="utf-8") as f:
                    model_drift_text = f.read()
            except Exception as e:
                logger.error(f"Error reading model drift text report: {e}")
                model_drift_text = f"Error reading model drift text report: {str(e)}"

        # Get data drift report (simulated for now)
        data_drift_report = {
            "timestamp": datetime.now().isoformat(),
            "drift_detected": True,
            "features_with_drift": ["feature1", "feature2", "feature3"],
            "drift_scores": {"feature1": 0.8, "feature2": 0.6, "feature3": 0.7},
            "threshold": 0.5
        }

        # Generate data drift text report
        data_drift_text = generate_data_drift_text_report(data_drift_report)

        # Debug logging
        logger.info(f"Model drift report: {model_drift_report is not None}")
        logger.info(f"Data drift report: {data_drift_report is not None}")

        return templates.TemplateResponse("drift_reports.html", {
            "request": request,
            "model_drift_report": model_drift_report,
            "model_drift_text": model_drift_text,
            "data_drift_report": data_drift_report,
            "data_drift_text": data_drift_text,
            "show_visualizations": os.environ.get('SHOW_VISUALIZATIONS', 'True').lower() == 'true'
        })
    except Exception as e:
        logger.error(f"Error rendering drift reports page: {e}")
        # Return a simple error page
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>An error occurred while rendering the drift reports page: {str(e)}</p><p>Check the server logs for more details.</p></body></html>",
            status_code=500
        )

@app.get("/model-drift", response_class=HTMLResponse)
async def model_drift_page(request: Request):
    """Render the model drift analysis page"""
    try:
        # Check if there's a drift report available
        drift_report = get_latest_model_drift_report()

        # Get the text report if available
        text_report = ""
        if drift_report and "text_report_path" in drift_report and os.path.exists(drift_report["text_report_path"]):
            try:
                with open(drift_report["text_report_path"], "r", encoding="utf-8") as f:
                    text_report = f.read()
            except Exception as e:
                logger.error(f"Error reading text report: {e}")
                text_report = f"Error reading text report: {str(e)}"

        # Debug logging
        logger.info(f"Drift report: {drift_report is not None}")
        logger.info(f"Text report length: {len(text_report)}")
        logger.info(f"Show visualizations: {os.environ.get('SHOW_VISUALIZATIONS', 'True').lower() == 'true'}")

        return templates.TemplateResponse("model_drift.html", {
            "request": request,
            "drift_report": drift_report,
            "text_report": text_report,
            "show_visualizations": os.environ.get('SHOW_VISUALIZATIONS', 'True').lower() == 'true'
        })
    except Exception as e:
        logger.error(f"Error rendering model drift page: {e}")
        # Return a simple error page
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>An error occurred while rendering the model drift page: {str(e)}</p><p>Check the server logs for more details.</p></body></html>",
            status_code=500
        )

@app.post("/api/model-drift/generate")
async def generate_model_drift_report(background_tasks: BackgroundTasks):
    """Generate a new model drift report"""
    try:
        # This would normally call your actual model drift detection code
        # For demo purposes, we'll generate sample visualizations
        background_tasks.add_task(generate_sample_model_drift_report)

        return {"status": "success", "message": "Model drift report generation started"}
    except Exception as e:
        logger.error(f"Error generating model drift report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model-drift/latest")
async def get_latest_model_drift_report_api():
    """Get the latest model drift report"""
    try:
        drift_report = get_latest_model_drift_report()
        if not drift_report:
            raise HTTPException(status_code=404, detail="No model drift report found")

        return drift_report
    except Exception as e:
        logger.error(f"Error getting latest model drift report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model-drift/text")
async def get_model_drift_text_report():
    """Get the model drift text report"""
    try:
        drift_report = get_latest_model_drift_report()
        if not drift_report or "text_report_path" not in drift_report or not os.path.exists(drift_report["text_report_path"]):
            raise HTTPException(status_code=404, detail="No model drift text report found")

        with open(drift_report["text_report_path"], "r") as f:
            text_report = f.read()

        return {"status": "success", "text_report": text_report}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model drift text report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model-drift/export")
async def export_model_drift_report():
    """Export the model drift report as PDF"""
    try:
        # This would normally generate a PDF report
        # For demo purposes, we'll return a sample file
        return {"status": "success", "message": "PDF export not implemented yet"}
    except Exception as e:
        logger.error(f"Error exporting model drift report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("enhanced_app_with_templates:app", host="0.0.0.0", port=8000, reload=True)
