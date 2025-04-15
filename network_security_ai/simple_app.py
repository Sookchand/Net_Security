from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import os
import uvicorn
from dotenv import load_dotenv

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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/sample/drift")
async def get_sample_drift():
    """Get a sample drift event with insights"""
    # Create a sample drift event
    sample_event = {
        "event_id": "sample-drift-001",
        "event_type": "drift_detected",
        "drift_score": 0.35,
        "features": ["packet_size", "connection_duration", "protocol_distribution"],
        "severity": "Medium"
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
        "technical_details": ""
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
        "attack_type": "DDoS",
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.5",
        "protocol": "TCP",
        "confidence": 0.92,
        "affected_systems": ["web-server-01", "load-balancer-02"]
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
        "technical_details": ""
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
    
    return {
        "event": sample_event,
        "insights": insights
    }

@app.get("/health")
async def health_check():
    """Check the health of the API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("simple_app:app", host="0.0.0.0", port=8000, reload=True)