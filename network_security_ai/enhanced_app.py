from fastapi import FastAPI, Request, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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
import glob
from typing import List, Dict, Any, Optional

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
    from networksecurity.utils.main_utils.utils import load_object, save_object
    from networksecurity.pipeline.training_pipeline import TrainingPipeline
    from networksecurity.entity.config_entity import TrainingPipelineConfig
    NET_SECURITY_AVAILABLE = True
    logger.info("Successfully imported Net_Security modules")
except ImportError as e:
    logger.warning(f"Could not import Net_Security modules: {e}")
    NET_SECURITY_AVAILABLE = False

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("data/sample_data", exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/results", exist_ok=True)
os.makedirs("final_model", exist_ok=True)

# Create sample data if it doesn't exist
def create_sample_data():
    """Create sample data files for demonstration"""
    if not os.path.exists("data/sample_data/normal_traffic.csv"):
        # Create sample normal traffic data
        normal_data = pd.DataFrame({
            'duration': np.random.randint(1, 100, 100),
            'protocol_type': np.random.choice(['tcp', 'udp', 'icmp'], 100),
            'service': np.random.choice(['http', 'ftp', 'smtp', 'ssh'], 100),
            'flag': np.random.choice(['SF', 'REJ', 'S0'], 100),
            'src_bytes': np.random.randint(100, 10000, 100),
            'dst_bytes': np.random.randint(100, 10000, 100),
        })
        normal_data.to_csv("data/sample_data/normal_traffic.csv", index=False)

    if not os.path.exists("data/sample_data/attack_traffic.csv"):
        # Create sample attack traffic data
        attack_data = pd.DataFrame({
            'duration': np.random.randint(1, 100, 100),
            'protocol_type': np.random.choice(['tcp', 'udp', 'icmp'], 100),
            'service': np.random.choice(['http', 'ftp', 'smtp', 'ssh'], 100),
            'flag': np.random.choice(['SF', 'REJ', 'S0'], 100),
            'src_bytes': np.random.randint(10000, 100000, 100),
            'dst_bytes': np.random.randint(10000, 100000, 100),
        })
        attack_data.to_csv("data/sample_data/attack_traffic.csv", index=False)

    if not os.path.exists("data/sample_data/mixed_traffic.csv"):
        # Create sample mixed traffic data
        mixed_data = pd.DataFrame({
            'duration': np.random.randint(1, 100, 100),
            'protocol_type': np.random.choice(['tcp', 'udp', 'icmp'], 100),
            'service': np.random.choice(['http', 'ftp', 'smtp', 'ssh'], 100),
            'flag': np.random.choice(['SF', 'REJ', 'S0'], 100),
            'src_bytes': np.random.randint(100, 100000, 100),
            'dst_bytes': np.random.randint(100, 100000, 100),
        })
        mixed_data.to_csv("data/sample_data/mixed_traffic.csv", index=False)

# Create sample data
create_sample_data()

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

@app.get("/architecture", response_class=HTMLResponse)
async def architecture(request: Request):
    """Render the system architecture page"""
    return templates.TemplateResponse("architecture.html", {"request": request})

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

        # Generate analysis using Gemini
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

        # Prepare the prompt
        prompt = f"""
        As a cybersecurity expert, analyze the following email or text content for potential security threats:

        ```
        {text_content}
        ```

        Please provide your analysis in the following JSON format:

        ```json
        {{
            "threat_score": [0-100 score indicating overall threat level],
            "summary": "[One-sentence summary of the threat assessment]",
            "detailed_summary": "[Detailed paragraph explaining the analysis]",
            "threats": [
                {{
                    "type": "[Threat type, e.g., Phishing, Malware, Social Engineering]",
                    "description": "[Description of the specific threat]"
                }}
            ],
            "threat_categories": {{
                "Phishing": [0-100 score],
                "Malware": [0-100 score],
                "Social Engineering": [0-100 score],
                "Spam": [0-100 score],
                "Scam": [0-100 score]
            }},
            "recommendations": [
                "[First recommendation]",
                "[Second recommendation]",
                "[Third recommendation]"
            ]
        }}
        ```

        Only return the JSON object, nothing else.
        """

        response = model.generate_content(prompt)

        # Extract the JSON from the response
        response_text = response.text

        # Find JSON content between triple backticks if present
        import re
        json_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', response_text)

        if json_match:
            json_str = json_match.group(1)
        else:
            # If no backticks, try to parse the whole response
            json_str = response_text

        # Parse the JSON
        try:
            analysis = json.loads(json_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, create a basic structure
            analysis = {
                "threat_score": 0,
                "summary": "Unable to parse analysis results",
                "detailed_summary": "The system was unable to generate a proper analysis of the provided content.",
                "threats": [],
                "threat_categories": {
                    "Phishing": 0,
                    "Malware": 0,
                    "Social Engineering": 0,
                    "Spam": 0,
                    "Scam": 0
                },
                "recommendations": [
                    "Try again with different content",
                    "Contact support if the issue persists"
                ]
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

@app.post("/analyze-email-file")
async def analyze_email_file(email_file: UploadFile = File(...)):
    """Analyze an email file for security threats"""
    try:
        # Read the file content
        content = await email_file.read()
        text_content = content.decode("utf-8", errors="ignore")

        # Generate analysis using Gemini
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

        # Prepare the prompt
        prompt = f"""
        As a cybersecurity expert, analyze the following email content for potential security threats:

        ```
        {text_content}
        ```

        Please provide your analysis in the following JSON format:

        ```json
        {{
            "threat_score": [0-100 score indicating overall threat level],
            "summary": "[One-sentence summary of the threat assessment]",
            "detailed_summary": "[Detailed paragraph explaining the analysis]",
            "threats": [
                {{
                    "type": "[Threat type, e.g., Phishing, Malware, Social Engineering]",
                    "description": "[Description of the specific threat]"
                }}
            ],
            "threat_categories": {{
                "Phishing": [0-100 score],
                "Malware": [0-100 score],
                "Social Engineering": [0-100 score],
                "Spam": [0-100 score],
                "Scam": [0-100 score]
            }},
            "recommendations": [
                "[First recommendation]",
                "[Second recommendation]",
                "[Third recommendation]"
            ]
        }}
        ```

        Only return the JSON object, nothing else.
        """

        response = model.generate_content(prompt)

        # Extract the JSON from the response
        response_text = response.text

        # Find JSON content between triple backticks if present
        import re
        json_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', response_text)

        if json_match:
            json_str = json_match.group(1)
        else:
            # If no backticks, try to parse the whole response
            json_str = response_text

        # Parse the JSON
        try:
            analysis = json.loads(json_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, create a basic structure
            analysis = {
                "threat_score": 0,
                "summary": "Unable to parse analysis results",
                "detailed_summary": "The system was unable to generate a proper analysis of the provided content.",
                "threats": [],
                "threat_categories": {
                    "Phishing": 0,
                    "Malware": 0,
                    "Social Engineering": 0,
                    "Spam": 0,
                    "Scam": 0
                },
                "recommendations": [
                    "Try again with different content",
                    "Contact support if the issue persists"
                ]
            }

        return {
            "status": "success",
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Error analyzing email file: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error analyzing email file: {str(e)}"
            }
        )

@app.post("/ask-about-text-analysis")
async def ask_about_text_analysis(request: Request):
    """Answer questions about text analysis results"""
    try:
        # Parse the request body
        body = await request.json()
        question = body.get("question")

        if not question:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Question is required"
                }
            )

        # Generate a response using Gemini
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

        # Prepare the prompt
        prompt = f"""
        As a cybersecurity expert, answer this question about email or text security analysis:

        Question: {question}

        Provide a detailed and accurate response focusing specifically on answering the question about email security, phishing, malware, or other text-based security threats.
        """

        response = model.generate_content(prompt)

        return {
            "answer": response.text
        }

    except Exception as e:
        logger.error(f"Error answering text analysis question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error answering question: {str(e)}"
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

@app.get("/train", response_class=HTMLResponse)
async def train_page(request: Request):
    """Render the training page"""
    return templates.TemplateResponse("train.html", {"request": request})

@app.post("/start-training")
async def start_training():
    """Start the model training process"""
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

@app.get("/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    """Render the prediction page"""
    return templates.TemplateResponse("predict_form.html", {"request": request})

@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    """Make predictions on uploaded data"""
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

        # Save the uploaded file
        file_path = f"data/uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Load the data
        df = pd.read_csv(file_path)

        # Generate predictions
        result = await generate_predictions(df, file.filename)

        return templates.TemplateResponse(
            "prediction_result.html",
            {
                "request": request,
                **result
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

@app.get("/predict-sample/{sample_id}")
async def predict_sample(request: Request, sample_id: int):
    """Make predictions on a sample dataset"""
    try:
        # Map sample ID to file
        sample_files = {
            1: "data/sample_data/normal_traffic.csv",
            2: "data/sample_data/attack_traffic.csv",
            3: "data/sample_data/mixed_traffic.csv"
        }

        if sample_id not in sample_files:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid sample ID"
                }
            )

        # Load the sample data
        file_path = sample_files[sample_id]
        df = pd.read_csv(file_path)

        # Generate predictions
        result = await generate_predictions(df, os.path.basename(file_path))

        return templates.TemplateResponse(
            "prediction_result.html",
            {
                "request": request,
                **result
            }
        )

    except Exception as e:
        logger.error(f"Error in sample prediction: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )

@app.post("/predict-from-directory")
async def predict_from_directory(request: Request):
    """Make predictions on all CSV files in a directory"""
    form_data = await request.form()
    directory = form_data.get("directory")

    if not directory or not os.path.isdir(directory):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": f"Invalid directory: {directory}"
            }
        )

    try:
        # Find all CSV files in the directory
        csv_files = glob.glob(os.path.join(directory, "*.csv"))

        if not csv_files:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"No CSV files found in directory: {directory}"
                }
            )

        # Process the first file for now (could be extended to process all files)
        file_path = csv_files[0]
        df = pd.read_csv(file_path)

        # Generate predictions
        result = await generate_predictions(df, os.path.basename(file_path))

        return templates.TemplateResponse(
            "prediction_result.html",
            {
                "request": request,
                **result
            }
        )

    except Exception as e:
        logger.error(f"Error in directory prediction: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )

@app.post("/ask-about-prediction")
async def ask_about_prediction(request: Request):
    """Answer questions about prediction results"""
    try:
        # Parse the request body
        body = await request.json()
        question = body.get("question")
        attack_counts = body.get("attack_counts", {})
        total_records = body.get("total_records", 0)
        total_attacks = body.get("total_attacks", 0)

        if not question:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Question is required"
                }
            )

        # Generate a response using Gemini
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

        # Prepare the prompt
        prompt = f"""
        As a cybersecurity expert, answer this question about network security prediction results:

        Prediction Results:
        - Total records analyzed: {total_records}
        - Attack distribution: {json.dumps(attack_counts)}
        - Total potential attacks: {total_attacks}

        Question:
        {question}

        Provide a detailed and accurate response focusing specifically on answering the question.
        """

        response = model.generate_content(prompt)

        return {
            "answer": response.text
        }

    except Exception as e:
        logger.error(f"Error answering prediction question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error answering question: {str(e)}"
            }
        )

async def generate_predictions(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
    """Generate predictions and insights for a dataframe"""
    # Check if model exists
    if NET_SECURITY_AVAILABLE and os.path.exists("final_model/model.pkl") and os.path.exists("final_model/preprocessor.pkl"):
        try:
            # Load model and preprocessor
            preprocessor = load_object("final_model/preprocessor.pkl")
            final_model = load_object("final_model/model.pkl")
            network_model = NetworkModel(preprocessor=preprocessor, model=final_model)

            # Generate predictions
            y_pred = network_model.predict(df)
            df["predicted_attack"] = y_pred
            simulated = False
        except Exception as e:
            logger.warning(f"Error using trained model: {str(e)}. Using simulated predictions.")
            # Use simulated predictions if model fails
            attack_types = ["Normal", "DoS", "Probe", "R2L", "U2R"]
            df["predicted_attack"] = np.random.choice(attack_types, size=len(df), p=[0.7, 0.1, 0.1, 0.05, 0.05])
            simulated = True
    else:
        # Use simulated predictions if model doesn't exist
        attack_types = ["Normal", "DoS", "Probe", "R2L", "U2R"]
        df["predicted_attack"] = np.random.choice(attack_types, size=len(df), p=[0.7, 0.1, 0.1, 0.05, 0.05])
        simulated = True

    # Save predictions
    output_path = f"data/results/prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
    Attack distribution: {json.dumps(attack_counts)}

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

    return {
        "table": table_html,
        "analysis": analysis,
        "attack_counts": attack_counts,
        "total_attacks": total_attacks,
        "total_records": total_records,
        "simulated": simulated,
        "filename": filename
    }

@app.get("/health")
async def health_check():
    """Check the health of the API"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run("enhanced_app:app", host="0.0.0.0", port=8000, reload=True)
