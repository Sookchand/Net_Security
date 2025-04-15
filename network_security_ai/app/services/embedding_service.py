from sentence_transformers import SentenceTransformer
import numpy as np
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings for security events"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with the embedding model"""
        try:
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Embedding service initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        try:
            embeddings = self.embedding_model.encode(texts)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_security_event_embedding(self, security_event: Dict[str, Any]) -> np.ndarray:
        """Generate an embedding for a security event"""
        try:
            # Prepare text representation of the security event
            text = self._security_event_to_text(security_event)
            
            # Generate embedding
            embedding = self.embedding_model.encode([text])[0]
            
            logger.info(f"Generated embedding for security event of type {security_event.get('event_type')}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating security event embedding: {str(e)}")
            raise
    
    def _security_event_to_text(self, security_event: Dict[str, Any]) -> str:
        """Convert a security event to a text representation"""
        text_parts = []
        
        # Add event type
        if "event_type" in security_event:
            text_parts.append(f"Event Type: {security_event['event_type']}")
        
        # Add attack-specific information if available
        if "attack_type" in security_event:
            text_parts.append(f"Attack Type: {security_event['attack_type']}")
        
        if "source_ip" in security_event and "destination_ip" in security_event:
            text_parts.append(f"Connection: {security_event['source_ip']} to {security_event['destination_ip']}")
        
        if "protocol" in security_event:
            text_parts.append(f"Protocol: {security_event['protocol']}")
        
        # Add drift-specific information if available
        if "drift_score" in security_event:
            text_parts.append(f"Drift Score: {security_event['drift_score']}")
        
        if "features" in security_event:
            text_parts.append(f"Affected Features: {', '.join(security_event['features'])}")
        
        return " ".join(text_parts)
    
    def prepare_fine_tuning_data(self, security_events: List[Dict[str, Any]], insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for fine-tuning embeddings"""
        try:
            fine_tuning_data = []
            
            for i, (event, insight) in enumerate(zip(security_events, insights)):
                # Create a training example
                example = {
                    "input_text": self._security_event_to_text(event),
                    "output_text": insight.get("explanation", "") + "\n" + insight.get("technical_details", ""),
                    "embedding": self.generate_security_event_embedding(event).tolist()
                }
                
                fine_tuning_data.append(example)
            
            logger.info(f"Prepared fine-tuning data for {len(security_events)} events")
            return fine_tuning_data
        except Exception as e:
            logger.error(f"Error preparing fine-tuning data: {str(e)}")
            raise
    
    def save_fine_tuning_data(self, fine_tuning_data: List[Dict[str, Any]], output_path: str) -> None:
        """Save fine-tuning data to a file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(fine_tuning_data, f)
            
            logger.info(f"Saved fine-tuning data to {output_path}")
        except Exception as e:
            logger.error(f"Error saving fine-tuning data: {str(e)}")
            raise
