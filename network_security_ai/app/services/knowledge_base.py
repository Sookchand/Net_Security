import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityKnowledgeBase:
    """Vector database and RAG system for security events"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", 
                 index_path: Optional[str] = None, 
                 documents_path: Optional[str] = None):
        """Initialize the security knowledge base with embedding model and vector storage"""
        try:
            # Load the embedding model
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
            
            # Initialize the vector index
            self.index = None
            self.documents = []
            
            # Load existing index and documents if provided
            if index_path and os.path.exists(index_path) and documents_path and os.path.exists(documents_path):
                self.load(index_path, documents_path)
                logger.info(f"Loaded existing knowledge base with {len(self.documents)} documents")
            else:
                # Initialize an empty index
                self._initialize_empty_index()
                logger.info("Initialized empty knowledge base")
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            raise
    
    def _initialize_empty_index(self) -> None:
        """Initialize an empty FAISS index"""
        # Get the embedding dimension
        embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Create a new index
        self.index = faiss.IndexFlatL2(embedding_dim)
        logger.info(f"Created empty FAISS index with dimension {embedding_dim}")
        
    def add_document(self, document: Dict[str, Any]) -> int:
        """Add a document to the knowledge base"""
        try:
            # Generate embedding for the document
            text_for_embedding = self._prepare_text_for_embedding(document)
            embedding = self.embedding_model.encode([text_for_embedding])[0]
            
            # Add to the index
            if self.index.ntotal == 0:
                # First document, need to initialize the index
                self.index = faiss.IndexFlatL2(embedding.shape[0])
                
            self.index.add(np.array([embedding], dtype=np.float32))
            
            # Store the document
            self.documents.append(document)
            
            doc_id = len(self.documents) - 1
            logger.info(f"Added document to knowledge base with ID {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Error adding document to knowledge base: {str(e)}")
            raise
    
    def _prepare_text_for_embedding(self, document: Dict[str, Any]) -> str:
        """Prepare document text for embedding"""
        # Combine relevant fields into a single text
        text_parts = []
        
        # Add event type
        if "event_type" in document:
            text_parts.append(f"Event Type: {document['event_type']}")
        
        # Add attack type if available
        if "attack_type" in document:
            text_parts.append(f"Attack Type: {document['attack_type']}")
        
        # Add description if available
        if "description" in document:
            text_parts.append(document["description"])
        
        # Add technical details if available
        if "technical_details" in document:
            text_parts.append(document["technical_details"])
        
        # Add source and destination IPs if available
        if "source_ip" in document and "destination_ip" in document:
            text_parts.append(f"Connection: {document['source_ip']} to {document['destination_ip']}")
        
        # Add protocol if available
        if "protocol" in document:
            text_parts.append(f"Protocol: {document['protocol']}")
        
        return " ".join(text_parts)
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in the knowledge base"""
        try:
            if self.index.ntotal == 0:
                logger.warning("Knowledge base is empty, cannot perform search")
                return []
                
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Search the index
            distances, indices = self.index.search(np.array([query_embedding], dtype=np.float32), k)
            
            # Collect the results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents) and idx >= 0:  # Valid index
                    results.append({
                        "document": self.documents[idx],
                        "similarity": float(1.0 - distances[0][i]),  # Convert distance to similarity
                    })
            
            logger.info(f"Search for '{query}' returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def save(self, index_path: str, documents_path: str) -> None:
        """Save the index and documents to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            os.makedirs(os.path.dirname(documents_path), exist_ok=True)
            
            # Save the FAISS index
            faiss.write_index(self.index, index_path)
            
            # Save the documents
            with open(documents_path, 'w') as f:
                json.dump(self.documents, f)
                
            logger.info(f"Saved knowledge base to {index_path} and {documents_path}")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {str(e)}")
            raise
    
    def load(self, index_path: str, documents_path: str) -> None:
        """Load the index and documents from disk"""
        try:
            # Load the FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load the documents
            with open(documents_path, 'r') as f:
                self.documents = json.load(f)
                
            logger.info(f"Loaded knowledge base from {index_path} and {documents_path}")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            raise
            
    def format_rag_results(self, rag_results: List[Dict[str, Any]], max_results: int = 3) -> str:
        """Format RAG results for inclusion in the prompt"""
        if not rag_results:
            return "No similar historical events found."
        
        # Limit to top results
        top_results = rag_results[:max_results]
        
        formatted_text = "Similar historical events:\n\n"
        
        for i, result in enumerate(top_results):
            document = result["document"]
            similarity = result["similarity"]
            
            formatted_text += f"Event {i+1} (Similarity: {similarity:.2f}):\n"
            
            # Add event details
            if "event_type" in document:
                formatted_text += f"- Type: {document['event_type']}\n"
            
            if "attack_type" in document:
                formatted_text += f"- Attack: {document['attack_type']}\n"
            
            if "description" in document:
                formatted_text += f"- Description: {document['description']}\n"
            
            if "resolution" in document:
                formatted_text += f"- Resolution: {document['resolution']}\n"
            
            formatted_text += "\n"
        
        return formatted_text
