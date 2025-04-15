from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class DriftEvent(BaseModel):
    """Model for a data drift detection event"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = "drift_detected"
    timestamp: datetime = Field(default_factory=datetime.now)
    drift_score: float
    features: List[str]
    severity: str
    additional_data: Optional[Dict] = None

class AttackEvent(BaseModel):
    """Model for a detected attack event"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = "attack_detected"
    timestamp: datetime = Field(default_factory=datetime.now)
    attack_type: str
    source_ip: str
    destination_ip: str
    protocol: str
    confidence: float
    affected_systems: Optional[List[str]] = None
    additional_data: Optional[Dict] = None

class SecurityEvent(BaseModel):
    """Generic security event model that can be either a drift or attack event"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    # Common fields
    severity: Optional[str] = None
    # Drift-specific fields
    drift_score: Optional[float] = None
    features: Optional[List[str]] = None
    # Attack-specific fields
    attack_type: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    protocol: Optional[str] = None
    confidence: Optional[float] = None
    affected_systems: Optional[List[str]] = None
    # Additional data
    additional_data: Optional[Dict] = None
