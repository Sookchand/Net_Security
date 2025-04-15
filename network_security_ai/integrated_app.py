from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import os
import sys
import uvicorn
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import json
import logging
from datetime import datetime
import uuid
import subprocess
import importlib.util
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Create FastAPI app
app = FastAPI(title="Network Security AI Platform")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Global variables to store conversation state
conversations = {}

# Add Net_Security path to sys.path if it's not already there
net_security_path = os.path.abspath("../Net_Security")
if net_security_path not in sys.path:
    sys.path.append(net_security_path)

# Try to import NetworkModel from Net_Security
try:
    from networksecurity.utils.ml_utils.model.estimator import NetworkModel
    from networksecurity.utils.main_utils.utils import load_object
    from networksecurity.pipeline.training_pipeline import TrainingPipeline
    from networksecurity.entity.config_entity import TrainingPipelineConfig
    NET_SECURITY_AVAILABLE = True
    logger.info("Successfully imported Net_Security modules")
except ImportError as e:
    logger.warning(f"Could not import Net_Security modules: {e}")
    NET_SECURITY_AVAILABLE = False

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/insights/{event_id}", response_class=HTMLResponse)
async def insights(request: Request, event_id: str):
    """Render the insights page for a specific event"""
    return templates.TemplateResponse(
        "insights.html", 
        {
            "request": request,
            "event_id": event_id
        }
    )

@app.get("/api/sample/drift")
async def get_sample_drift():
    """Get a sample drift event with insights"""
    # Create a sample drift event
    sample_event = {
        "event_id": "sample-drift-001",
        "event_type": "drift_detected",
        "timestamp": datetime.now().isoformat(),
        "drift_score": 0.35,
        "features": ["packet_size", "connection_duration", "protocol_distribution"],
        "severity": "Medium",
        "additional_data": {
            "baseline_period": "2023-05-01 to 2023-05-07",
            "current_period": "2023-05-08 to 2023-05-14"
        }
    }
    
    # Generate insights using Gemini
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    prompt = f"""
    As a cybersecurity expert, analyze this security event:
    
    Event Type: {sample_event['event_type']}
    Drift Score: {sample_event['drift_score']}
    Affected Features: {', '.join(sample_event['features'])}
    Severity: {sample_event['severity']}
    
    Please provide your analysis in the following format:
    
    EXPLANATION:
    [A concise explanation of what this security event indicates]
    
    SEVERITY:
    [Severity assessment (Critical/High/Medium/Low) and potential impact]
    
    RECOMMENDATIONS:
    1. [First recommended action]
    2. [Second recommended action]
    3. [Third recommended action]
    
    TECHNICAL_DETAILS:
    [Technical details relevant for security analysts]
    """
    
    response = model.generate_content(prompt)
    
    # Parse the response
    text = response.text
    insights = {
        "explanation": "",
        "severity": sample_event["severity"],
        "recommendations": [],
        "technical_details": "",
        "conversation_id": str(uuid.uuid4())  # Generate a conversation ID
    }
    
    current_section = None
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith("EXPLANATION:"):
            current_section = "explanation"
        elif line.startswith("SEVERITY:"):
            current_section = "severity"
        elif line.startswith("RECOMMENDATIONS:"):
            current_section = "recommendations"
        elif line.startswith("TECHNICAL_DETAILS:"):
            current_section = "technical_details"
        elif current_section and line and not line.startswith("EXPLANATION") and not line.startswith("SEVERITY") and not line.startswith("RECOMMENDATIONS") and not line.startswith("TECHNICAL_DETAILS"):
            if current_section == "recommendations":
                if any(line.startswith(prefix) for prefix in ("1.", "2.", "3.", "4.", "5.", "•", "-", "*")):
                    insights["recommendations"].append(line[line.find(" ")+1:].strip() if " " in line else line)
            else:
                insights[current_section] += line + " "
    
    # Store the conversation
    conversations[insights["conversation_id"]] = {
        "event": sample_event,
        "insights": insights,
        "messages": [
            {"role": "system", "content": f"Analyzing drift event with score {sample_event['drift_score']}"},
            {"role": "assistant", "content": insights["explanation"]}
        ]
    }
    
    return {
        "event": sample_event,
        "insights": insights
    }

@app.get("/api/sample/attack")
async def get_sample_attack():
    """Get a sample attack event with insights"""
    # Create a sample attack event
    sample_event = {
        "event_id": "sample-attack-001",
        "event_type": "attack_detected",
        "timestamp": datetime.now().isoformat(),
        "attack_type": "DDoS",
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.5",
        "protocol": "TCP",
        "confidence": 0.92,
        "affected_systems": ["web-server-01", "load-balancer-02"],
        "additional_data": {
            "packets_per_second": 15000,
            "bandwidth_usage": "2.3 Gbps",
            "attack_signature": "SYN flood pattern"
        }
    }
    
    # Generate insights using Gemini
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    prompt = f"""
    As a cybersecurity expert, analyze this security event:
    
    Event Type: {sample_event['event_type']}
    Attack Type: {sample_event['attack_type']}
    Source IP: {sample_event['source_ip']}
    Destination IP: {sample_event['destination_ip']}
    Protocol: {sample_event['protocol']}
    Confidence: {sample_event['confidence']}
    Affected Systems: {', '.join(sample_event['affected_systems'])}
    
    Please provide your analysis in the following format:
    
    EXPLANATION:
    [A concise explanation of what this security event indicates]
    
    SEVERITY:
    [Severity assessment (Critical/High/Medium/Low) and potential impact]
    
    RECOMMENDATIONS:
    1. [First recommended action]
    2. [Second recommended action]
    3. [Third recommended action]
    
    TECHNICAL_DETAILS:
    [Technical details relevant for security analysts]
    """
    
    response = model.generate_content(prompt)
    
    # Parse the response
    text = response.text
    insights = {
        "explanation": "",
        "severity": "High",
        "recommendations": [],
        "technical_details": "",
        "conversation_id": str(uuid.uuid4())  # Generate a conversation ID
    }
    
    current_section = None
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith("EXPLANATION:"):
            current_section = "explanation"
        elif line.startswith("SEVERITY:"):
            current_section = "severity"
        elif line.startswith("RECOMMENDATIONS:"):
            current_section = "recommendations"
        elif line.startswith("TECHNICAL_DETAILS:"):
            current_section = "technical_details"
        elif current_section and line and not line.startswith("EXPLANATION") and not line.startswith("SEVERITY") and not line.startswith("RECOMMENDATIONS") and not line.startswith("TECHNICAL_DETAILS"):
            if current_section == "recommendations":
                if any(line.startswith(prefix) for prefix in ("1.", "2.", "3.", "4.", "5.", "•", "-", "*")):
                    insights["recommendations"].append(line[line.find(" ")+1:].strip() if " " in line else line)
            else:
                insights[current_section] += line + " "
    
    # Store the conversation
    conversations[insights["conversation_id"]] = {
        "event": sample_event,
        "insights": insights,
        "messages": [
            {"role": "system", "content": f"Analyzing {sample_event['attack_type']} attack from {sample_event['source_ip']} to {sample_event['destination_ip']}"},
            {"role": "assistant", "content": insights["explanation"]}
        ]
    }
    
    return {
        "event": sample_event,
        "insights": insights
    }

@app.post("/api/conversation/question")
async def ask_question(request: Request):
    """Ask a follow-up question in a conversation"""
    try:
        # Parse the request body
        body = await request.json()
        conversation_id = body.get("conversation_id")
        question = body.get("question")
        
        if not conversation_id or not question:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Conversation ID and question are required"
                }
            )
        
        if conversation_id not in conversations:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "Conversation not found"
                }
            )
        
        # Get the conversation
        conversation = conversations[conversation_id]
        
        # Add the question to the conversation history
        conversation["messages"].append({"role": "user", "content": question})
        
        # Generate a response using Gemini
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        
        # Prepare the prompt
        event = conversation["event"]
        insights = conversation["insights"]
        
        prompt = f"""
        As a cybersecurity expert, answer this follow-up question about a security event:
        
        Original Security Event:
        {json.dumps(event, indent=2)}
        
        My initial analysis:
        {insights["explanation"]}
        
        Technical details:
        {insights["technical_details"]}
        
        Follow-up Question:
        {question}
        
        Provide a detailed and accurate response focusing specifically on answering the question.
        """
        
        response = model.generate_content(prompt)
        
        # Add the response to the conversation history
        conversation["messages"].append({"role": "assistant", "content": response.text})
        
        return {
            "conversation_id": conversation_id,
            "response": response.text
        }
        
    except Exception as e:
        logger.error(f"Error asking question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error asking question: {str(e)}"
            }
        )

@app.get("/train")
async def train_route():
    """Train the network security model"""
    if not NET_SECURITY_AVAILABLE:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Net_Security modules are not available. Please make sure the Net_Security project is properly installed."
            }
        )
    
    try:
        # Create a training pipeline
        training_pipeline_config = TrainingPipelineConfig()
        pipeline = TrainingPipeline(training_pipeline_config=training_pipeline_config)
        
        # Run the pipeline in a separate process to avoid blocking
        subprocess.Popen([sys.executable, "-c", 
            "import sys; sys.path.append('../Net_Security'); "
            "from networksecurity.pipeline.training_pipeline import TrainingPipeline; "
            "from networksecurity.entity.config_entity import TrainingPipelineConfig; "
            "pipeline = TrainingPipeline(training_pipeline_config=TrainingPipelineConfig()); "
            "pipeline.run_pipeline()"
        ])
        
        return {
            "status": "success",
            "message": "Training process started in the background. This may take some time to complete."
        }
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error starting training: {str(e)}"
            }
        )

@app.get("/predict-form", response_class=HTMLResponse)
async def predict_form(request: Request):
    """Render the prediction form"""
    return templates.TemplateResponse(
        "predict_form.html",
        {"request": request}
    )

@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    """Make predictions on uploaded data"""
    if not NET_SECURITY_AVAILABLE:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Net_Security modules are not available. Please make sure the Net_Security project is properly installed."
            }
        )
    
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
            contents = await file.read()
            with open("temp_upload.csv", "wb") as f:
                f.write(contents)
            df = pd.read_csv("temp_upload.csv")
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Error reading CSV file: {str(e)}"
                }
            )
        
        # Check if model exists
        if not os.path.exists("final_model/model.pkl") or not os.path.exists("final_model/preprocessor.pkl"):
            # Use simulated predictions if model doesn't exist
            attack_types = ["Normal", "DoS", "Probe", "R2L", "U2R"]
            df["predicted_attack"] = [random.choice(attack_types) for _ in range(len(df))]
            
            # Save predictions
            output_path = "prediction_output/output.csv"
            df.to_csv(output_path, index=False)
            
            # Generate insights for the predictions
            attack_counts = df["predicted_attack"].value_counts().to_dict()
            total_attacks = sum(count for attack, count in attack_counts.items() if attack != "Normal")
            total_records = len(df)
            
            # Generate insights using Gemini
            model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
            prompt = f"""
            As a cybersecurity expert, analyze these network security prediction results:
            
            Total records analyzed: {total_records}
            Attack distribution: {attack_counts}
            
            Please provide your analysis in the following format:
            
            SUMMARY:
            [A concise summary of the prediction results]
            
            INSIGHTS:
            [Key insights from the prediction results]
            
            RECOMMENDATIONS:
            1. [First recommended action]
            2. [Second recommended action]
            3. [Third recommended action]
            """
            
            response = model.generate_content(prompt)
            
            # Parse the response
            text = response.text
            analysis = {
                "summary": "",
                "insights": "",
                "recommendations": []
            }
            
            current_section = None
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith("SUMMARY:"):
                    current_section = "summary"
                elif line.startswith("INSIGHTS:"):
                    current_section = "insights"
                elif line.startswith("RECOMMENDATIONS:"):
                    current_section = "recommendations"
                elif current_section and line and not line.startswith("SUMMARY") and not line.startswith("INSIGHTS") and not line.startswith("RECOMMENDATIONS"):
                    if current_section == "recommendations":
                        if any(line.startswith(prefix) for prefix in ("1.", "2.", "3.", "4.", "5.", "•", "-", "*")):
                            analysis["recommendations"].append(line[line.find(" ")+1:].strip() if " " in line else line)
                    else:
                        analysis[current_section] += line + " "
            
            # Convert to HTML table
            table_html = df.head(10).to_html(classes="table table-striped")
            
            # Return the results
            return templates.TemplateResponse(
                "prediction_result.html",
                {
                    "request": request, 
                    "table": table_html,
                    "analysis": analysis,
                    "attack_counts": attack_counts,
                    "total_attacks": total_attacks,
                    "total_records": total_records,
                    "simulated": True
                }
            )
        
        # Load model and make predictions
        try:
            preprocessor = load_object("final_model/preprocessor.pkl")
            final_model = load_object("final_model/model.pkl")
            network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
            
            # Generate predictions
            y_pred = network_model.predict(df)
            df["predicted_attack"] = y_pred
            
            # Save predictions
            output_path = "prediction_output/output.csv"
            df.to_csv(output_path, index=False)
            
            # Generate insights for the predictions
            attack_counts = df["predicted_attack"].value_counts().to_dict()
            total_attacks = sum(count for attack, count in attack_counts.items() if attack != "Normal")
            total_records = len(df)
            
            # Generate insights using Gemini
            model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
            prompt = f"""
            As a cybersecurity expert, analyze these network security prediction results:
            
            Total records analyzed: {total_records}
            Attack distribution: {attack_counts}
            
            Please provide your analysis in the following format:
            
            SUMMARY:
            [A concise summary of the prediction results]
            
            INSIGHTS:
            [Key insights from the prediction results]
            
            RECOMMENDATIONS:
            1. [First recommended action]
            2. [Second recommended action]
            3. [Third recommended action]
            """
            
            response = model.generate_content(prompt)
            
            # Parse the response
            text = response.text
            analysis = {
                "summary": "",
                "insights": "",
                "recommendations": []
            }
            
            current_section = None
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith("SUMMARY:"):
                    current_section = "summary"
                elif line.startswith("INSIGHTS:"):
                    current_section = "insights"
                elif line.startswith("RECOMMENDATIONS:"):
                    current_section = "recommendations"
                elif current_section and line and not line.startswith("SUMMARY") and not line.startswith("INSIGHTS") and not line.startswith("RECOMMENDATIONS"):
                    if current_section == "recommendations":
                        if any(line.startswith(prefix) for prefix in ("1.", "2.", "3.", "4.", "5.", "•", "-", "*")):
                            analysis["recommendations"].append(line[line.find(" ")+1:].strip() if " " in line else line)
                    else:
                        analysis[current_section] += line + " "
            
            # Convert to HTML table
            table_html = df.head(10).to_html(classes="table table-striped")
            
            # Return the results
            return templates.TemplateResponse(
                "prediction_result.html",
                {
                    "request": request, 
                    "table": table_html,
                    "analysis": analysis,
                    "attack_counts": attack_counts,
                    "total_attacks": total_attacks,
                    "total_records": total_records,
                    "simulated": False
                }
            )
            
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error making predictions: {str(e)}"
                }
            )
            
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )

@app.get("/health")
async def health_check():
    """Check the health of the API"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run("integrated_app:app", host="0.0.0.0", port=8000, reload=True)
