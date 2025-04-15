from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import json
from datetime import datetime

from .api.routes import router as api_router
from .config import DEBUG, ALLOWED_ORIGINS, SAMPLE_EVENTS_PATH

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Network Security AI Platform",
    description="AI-powered security insights with Gemini and RAG",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(api_router, prefix="/api")

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

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting Network Security AI Platform")
    
    # Create sample events file if it doesn't exist
    if not os.path.exists(SAMPLE_EVENTS_PATH):
        logger.info(f"Creating sample events file at {SAMPLE_EVENTS_PATH}")
        os.makedirs(os.path.dirname(SAMPLE_EVENTS_PATH), exist_ok=True)
        
        # Create sample events
        sample_events = [
            {
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
            },
            {
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
        ]
        
        with open(SAMPLE_EVENTS_PATH, 'w') as f:
            json.dump(sample_events, f, indent=2)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Shutting down Network Security AI Platform")
    
    # Save the knowledge base if it exists
    from .api.dependencies import get_knowledge_base
    try:
        knowledge_base = get_knowledge_base()
        index_path = os.path.join("data/vector_db", "faiss_index")
        documents_path = os.path.join("data/vector_db", "documents.json")
        knowledge_base.save(index_path, documents_path)
        logger.info(f"Saved knowledge base to {index_path} and {documents_path}")
    except Exception as e:
        logger.error(f"Error saving knowledge base: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    from .config import HOST, PORT
    
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=DEBUG)
