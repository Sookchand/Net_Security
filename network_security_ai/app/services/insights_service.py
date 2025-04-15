import logging
from typing import Dict, List, Any, Optional
import json
import uuid
from datetime import datetime

from .gemini_service import GeminiService
from .knowledge_base import SecurityKnowledgeBase

logger = logging.getLogger(__name__)

class SecurityInsightsService:
    """Service for generating security insights with RAG enhancement"""
    
    def __init__(self, gemini_service: GeminiService, knowledge_base: SecurityKnowledgeBase):
        """Initialize with Gemini service and knowledge base"""
        self.gemini_service = gemini_service
        self.knowledge_base = knowledge_base
        self.conversations = {}
        logger.info("Security Insights Service initialized")
    
    async def generate_insights(self, security_event: Dict[str, Any], context_info: Optional[str] = None) -> Dict[str, Any]:
        """Generate security insights enhanced with RAG"""
        try:
            # Prepare query for the knowledge base
            query = self._prepare_rag_query(security_event)
            
            # Retrieve relevant documents
            rag_results = self.knowledge_base.search(query)
            
            # Format RAG results for inclusion in the prompt
            formatted_rag_results = self.knowledge_base.format_rag_results(rag_results)
            
            # Generate insights with RAG enhancement
            insights = await self.gemini_service.generate_security_insights(
                security_event, 
                context_info=context_info,
                rag_results=formatted_rag_results
            )
            
            # Add the RAG results to the insights
            insights["similar_events"] = rag_results
            
            # Update the knowledge base with the new event and insights
            self._update_knowledge_base(security_event, insights)
            
            logger.info(f"Generated insights for security event of type {security_event.get('event_type')}")
            return insights
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {
                "explanation": f"Error generating insights: {str(e)}",
                "severity": "Unknown",
                "recommendations": [],
                "technical_details": ""
            }
    
    def _prepare_rag_query(self, security_event: Dict[str, Any]) -> str:
        """Prepare a query for the knowledge base based on the security event"""
        query_parts = []
        
        # Add event type
        if "event_type" in security_event:
            query_parts.append(f"Event Type: {security_event['event_type']}")
        
        # Add attack type if available
        if "attack_type" in security_event:
            query_parts.append(f"Attack Type: {security_event['attack_type']}")
        
        # Add source and destination IPs if available
        if "source_ip" in security_event and "destination_ip" in security_event:
            query_parts.append(f"Connection: {security_event['source_ip']} to {security_event['destination_ip']}")
        
        # Add protocol if available
        if "protocol" in security_event:
            query_parts.append(f"Protocol: {security_event['protocol']}")
        
        return " ".join(query_parts)
    
    def _update_knowledge_base(self, security_event: Dict[str, Any], insights: Dict[str, Any]) -> None:
        """Update the knowledge base with a new security event and its insights"""
        try:
            # Prepare the document to add
            document = {
                "event_type": security_event.get("event_type"),
                "timestamp": security_event.get("timestamp", datetime.now().isoformat()),
                "description": insights.get("explanation", ""),
                "severity": insights.get("severity", ""),
                "technical_details": insights.get("technical_details", ""),
                "resolution": ", ".join(insights.get("recommendations", [])),
            }
            
            # Add attack-specific information if available
            if "attack_type" in security_event:
                document["attack_type"] = security_event["attack_type"]
            
            if "source_ip" in security_event:
                document["source_ip"] = security_event["source_ip"]
            
            if "destination_ip" in security_event:
                document["destination_ip"] = security_event["destination_ip"]
            
            if "protocol" in security_event:
                document["protocol"] = security_event["protocol"]
            
            # Add to the knowledge base
            self.knowledge_base.add_document(document)
            logger.info("Added new document to knowledge base")
        except Exception as e:
            logger.error(f"Error updating knowledge base: {str(e)}")
    
    async def start_conversation(self, security_event: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation about a security event"""
        try:
            conversation_id = str(uuid.uuid4())
            
            # Generate initial insights
            initial_insights = await self.generate_insights(security_event)
            
            # Store the conversation
            self.conversations[conversation_id] = {
                "security_event": security_event,
                "messages": [
                    {"role": "system", "content": "Initial analysis"},
                    {"role": "assistant", "content": json.dumps(initial_insights)}
                ]
            }
            
            logger.info(f"Started conversation {conversation_id} for security event")
            return {
                "conversation_id": conversation_id,
                "insights": initial_insights
            }
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return {
                "error": f"Error starting conversation: {str(e)}"
            }
    
    async def ask_followup_question(self, conversation_id: str, question: str) -> Dict[str, Any]:
        """Ask a follow-up question about a security event"""
        try:
            if conversation_id not in self.conversations:
                logger.warning(f"Conversation {conversation_id} not found")
                return {"error": "Conversation not found"}
            
            conversation = self.conversations[conversation_id]
            security_event = conversation["security_event"]
            
            # Add the question to the conversation history
            conversation["messages"].append({"role": "user", "content": question})
            
            # Prepare the context from the conversation history
            context = "\n".join([msg["content"] for msg in conversation["messages"]])
            
            # Generate a response to the follow-up question
            response = await self.gemini_service.ask_followup_question(security_event, question, context)
            
            # Add the response to the conversation history
            conversation["messages"].append({"role": "assistant", "content": response})
            
            logger.info(f"Answered follow-up question in conversation {conversation_id}")
            return {
                "conversation_id": conversation_id,
                "response": response
            }
        except Exception as e:
            logger.error(f"Error answering follow-up question: {str(e)}")
            return {
                "error": f"Error answering follow-up question: {str(e)}"
            }
