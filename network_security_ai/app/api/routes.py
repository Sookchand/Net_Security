from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List, Any, Optional
import json
import logging
import numpy as np
from datetime import datetime

from ..models.security_event import SecurityEvent, DriftEvent, AttackEvent
from ..models.insights import SecurityInsight, InteractiveQuestion, InteractiveResponse
from ..services.insights_service import SecurityInsightsService
from ..services.drift_detector import DriftDetector
from .dependencies import get_insights_service, get_drift_detector

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/events/drift", response_model=Dict[str, Any])
async def detect_drift(
    drift_event: DriftEvent,
    drift_detector: DriftDetector = Depends(get_drift_detector),
    insights_service: SecurityInsightsService = Depends(get_insights_service)
):
    """Detect drift in network traffic and generate insights"""
    try:
        # Convert the event to a dictionary
        event_dict = drift_event.dict()
        
        # Generate insights
        insights = await insights_service.generate_insights(event_dict)
        
        # Return the event and insights
        return {
            "event": event_dict,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Error processing drift event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing drift event: {str(e)}")

@router.post("/events/attack", response_model=Dict[str, Any])
async def process_attack(
    attack_event: AttackEvent,
    insights_service: SecurityInsightsService = Depends(get_insights_service)
):
    """Process an attack event and generate insights"""
    try:
        # Convert the event to a dictionary
        event_dict = attack_event.dict()
        
        # Generate insights
        insights = await insights_service.generate_insights(event_dict)
        
        # Return the event and insights
        return {
            "event": event_dict,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Error processing attack event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing attack event: {str(e)}")

@router.post("/events", response_model=Dict[str, Any])
async def process_security_event(
    security_event: SecurityEvent,
    insights_service: SecurityInsightsService = Depends(get_insights_service)
):
    """Process a generic security event and generate insights"""
    try:
        # Convert the event to a dictionary
        event_dict = security_event.dict()
        
        # Generate insights
        insights = await insights_service.generate_insights(event_dict)
        
        # Return the event and insights
        return {
            "event": event_dict,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Error processing security event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing security event: {str(e)}")

@router.post("/conversation/start", response_model=Dict[str, Any])
async def start_conversation(
    security_event: SecurityEvent,
    insights_service: SecurityInsightsService = Depends(get_insights_service)
):
    """Start a new conversation about a security event"""
    try:
        # Convert the event to a dictionary
        event_dict = security_event.dict()
        
        # Start a conversation
        conversation = await insights_service.start_conversation(event_dict)
        
        return conversation
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting conversation: {str(e)}")

@router.post("/conversation/question", response_model=Dict[str, Any])
async def ask_question(
    question: InteractiveQuestion,
    insights_service: SecurityInsightsService = Depends(get_insights_service)
):
    """Ask a follow-up question in a conversation"""
    try:
        if not question.conversation_id:
            raise HTTPException(status_code=400, detail="Conversation ID is required")
        
        # Ask the question
        response = await insights_service.ask_followup_question(
            question.conversation_id,
            question.question
        )
        
        return response
    except Exception as e:
        logger.error(f"Error asking question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error asking question: {str(e)}")

@router.get("/sample/drift", response_model=Dict[str, Any])
async def get_sample_drift_event(
    insights_service: SecurityInsightsService = Depends(get_insights_service)
):
    """Get a sample drift event with insights"""
    try:
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
        
        # Generate insights
        insights = await insights_service.generate_insights(sample_event)
        
        # Return the event and insights
        return {
            "event": sample_event,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Error generating sample drift event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating sample drift event: {str(e)}")

@router.get("/sample/attack", response_model=Dict[str, Any])
async def get_sample_attack_event(
    insights_service: SecurityInsightsService = Depends(get_insights_service)
):
    """Get a sample attack event with insights"""
    try:
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
        
        # Generate insights
        insights = await insights_service.generate_insights(sample_event)
        
        # Return the event and insights
        return {
            "event": sample_event,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Error generating sample attack event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating sample attack event: {str(e)}")

@router.get("/health")
async def health_check():
    """Check the health of the API"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
