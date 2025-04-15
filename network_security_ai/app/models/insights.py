from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class SecurityInsight(BaseModel):
    """Model for security insights generated from security events"""
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    explanation: str
    severity: str
    recommendations: List[str]
    technical_details: str
    similar_events: Optional[List[Dict]] = None
    
class InteractiveQuestion(BaseModel):
    """Model for interactive questions about security events"""
    question: str
    conversation_id: Optional[str] = None
    
class InteractiveResponse(BaseModel):
    """Model for responses to interactive questions"""
    conversation_id: str
    response: str
    charts: Optional[List[Dict]] = None
    
class ActionRecommendation(BaseModel):
    """Model for recommended automated actions"""
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    description: str
    parameters: Dict
    severity: str
    confidence: float
    requires_approval: bool = True
