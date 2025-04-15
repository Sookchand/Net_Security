from fastapi import Depends
import numpy as np
import os
import logging
from typing import Dict, List, Any

from ..services.gemini_service import GeminiService
from ..services.knowledge_base import SecurityKnowledgeBase
from ..services.insights_service import SecurityInsightsService
from ..services.drift_detector import DriftDetector
from ..services.embedding_service import EmbeddingService
from ..config import GEMINI_API_KEY, GEMINI_MODEL, VECTOR_DB_PATH, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# Singleton instances
_gemini_service = None
_knowledge_base = None
_insights_service = None
_drift_detector = None
_embedding_service = None

def get_gemini_service() -> GeminiService:
    """Get or create the Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        logger.info("Initializing Gemini service")
        _gemini_service = GeminiService(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)
    return _gemini_service

def get_knowledge_base() -> SecurityKnowledgeBase:
    """Get or create the knowledge base singleton"""
    global _knowledge_base
    if _knowledge_base is None:
        logger.info("Initializing knowledge base")
        
        # Create vector DB directory if it doesn't exist
        os.makedirs(VECTOR_DB_PATH, exist_ok=True)
        
        # Check if index and documents files exist
        index_path = os.path.join(VECTOR_DB_PATH, "faiss_index")
        documents_path = os.path.join(VECTOR_DB_PATH, "documents.json")
        
        if os.path.exists(index_path) and os.path.exists(documents_path):
            logger.info(f"Loading existing knowledge base from {index_path} and {documents_path}")
            _knowledge_base = SecurityKnowledgeBase(
                embedding_model=EMBEDDING_MODEL,
                index_path=index_path,
                documents_path=documents_path
            )
        else:
            logger.info("Creating new knowledge base")
            _knowledge_base = SecurityKnowledgeBase(embedding_model=EMBEDDING_MODEL)
    
    return _knowledge_base

def get_insights_service(
    gemini_service: GeminiService = Depends(get_gemini_service),
    knowledge_base: SecurityKnowledgeBase = Depends(get_knowledge_base)
) -> SecurityInsightsService:
    """Get or create the insights service singleton"""
    global _insights_service
    if _insights_service is None:
        logger.info("Initializing insights service")
        _insights_service = SecurityInsightsService(gemini_service, knowledge_base)
    return _insights_service

def get_drift_detector() -> DriftDetector:
    """Get or create the drift detector singleton"""
    global _drift_detector
    if _drift_detector is None:
        logger.info("Initializing drift detector")
        
        # Create a simple baseline for demonstration
        # In a real application, this would be loaded from historical data
        num_features = 10
        num_samples = 100
        np.random.seed(42)  # For reproducibility
        baseline_data = np.random.normal(0, 1, (num_samples, num_features))
        feature_names = [f"feature_{i}" for i in range(num_features)]
        
        _drift_detector = DriftDetector(baseline_data, feature_names, sensitivity=0.1)
    
    return _drift_detector

def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        logger.info("Initializing embedding service")
        _embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    return _embedding_service
