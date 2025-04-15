import google.generativeai as genai
import json
import logging
from typing import Dict, List, Any, Optional

from ..config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google's Gemini API"""

    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        """Initialize the Gemini service with API key and model"""
        self.api_key = api_key
        self.model_name = model

        # Configure the Gemini API
        genai.configure(api_key=api_key)

        # Default safety settings (can be customized)
        self.safety_settings = None

        # Initialize the model
        try:
            # Add 'models/' prefix if not already present
            model_name = self.model_name
            if not model_name.startswith('models/'):
                model_name = f"models/{model_name}"

            self.gemini_model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 1024
                }
            )
            logger.info(f"Gemini model {model} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise

    async def generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            return f"Error generating content: {str(e)}"

    async def generate_security_insights(self,
                                        security_event: Dict[str, Any],
                                        context_info: Optional[str] = None,
                                        rag_results: Optional[str] = None) -> Dict[str, Any]:
        """Generate security insights for a security event"""
        # Prepare the prompt
        prompt = self._prepare_security_prompt(security_event, context_info, rag_results)

        # Generate response
        response_text = await self.generate_content(prompt)

        # Parse the response
        insights = self._parse_security_insights(response_text, security_event.get("event_type", "unknown"))

        return insights

    def _prepare_security_prompt(self,
                               security_event: Dict[str, Any],
                               context_info: Optional[str] = None,
                               rag_results: Optional[str] = None) -> str:
        """Prepare a prompt for security event analysis"""
        prompt = f"""
        As a cybersecurity expert, analyze this security event:

        Event Type: {security_event.get('event_type', 'Unknown')}
        """

        # Add event-specific details
        if security_event.get("event_type") == "drift_detected":
            prompt += f"""
            Drift Score: {security_event.get('drift_score', 'N/A')}
            Affected Features: {', '.join(security_event.get('features', []))}
            Severity: {security_event.get('severity', 'Unknown')}
            """
        elif security_event.get("event_type") == "attack_detected":
            prompt += f"""
            Attack Type: {security_event.get('attack_type', 'Unknown')}
            Source IP: {security_event.get('source_ip', 'N/A')}
            Destination IP: {security_event.get('destination_ip', 'N/A')}
            Protocol: {security_event.get('protocol', 'N/A')}
            Confidence: {security_event.get('confidence', 'N/A')}
            """

        # Add contextual information if available
        if context_info:
            prompt += f"""

            Contextual Information:
            {context_info}
            """

        # Add RAG results if available
        if rag_results:
            prompt += f"""

            Relevant Historical Information:
            {rag_results}
            """

        # Add the request for analysis
        prompt += """

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

        return prompt

    def _parse_security_insights(self, response_text: str, event_type: str) -> Dict[str, Any]:
        """Parse the Gemini response into structured insights"""
        # Initialize the result structure
        insights = {
            "explanation": "",
            "severity": "Unknown",
            "recommendations": [],
            "technical_details": ""
        }

        # Extract sections using markers
        sections = {
            "EXPLANATION": "explanation",
            "SEVERITY": "severity",
            "RECOMMENDATIONS": "recommendations",
            "TECHNICAL_DETAILS": "technical_details"
        }

        current_section = None
        section_content = []

        # Process the response line by line
        for line in response_text.split('\n'):
            line = line.strip()

            # Check if this line is a section header
            is_header = False
            for marker, field in sections.items():
                if line.startswith(marker + ":") or line == marker:
                    # Save the previous section if there was one
                    if current_section and section_content:
                        if current_section == "recommendations":
                            # Process list items for recommendations
                            insights[current_section] = self._extract_list_items('\n'.join(section_content))
                        else:
                            insights[current_section] = '\n'.join(section_content).strip()

                    # Start a new section
                    current_section = field
                    section_content = []
                    is_header = True
                    break

            # If not a header and we're in a section, add the line to the current section
            if not is_header and current_section and line:
                section_content.append(line)

        # Save the last section
        if current_section and section_content:
            if current_section == "recommendations":
                insights[current_section] = self._extract_list_items('\n'.join(section_content))
            else:
                insights[current_section] = '\n'.join(section_content).strip()

        return insights

    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from a text section"""
        items = []
        for line in text.split('\n'):
            # Look for numbered or bulleted list items
            line = line.strip()
            if line and any(line.startswith(prefix) for prefix in ("1.", "2.", "3.", "4.", "5.", "•", "-", "*")):
                # Remove the prefix and add to items
                cleaned_line = line[line.find(" ")+1:].strip() if " " in line else line
                items.append(cleaned_line)
            elif line and not any(marker in line for marker in (":", "EXPLANATION", "SEVERITY", "RECOMMENDATIONS", "TECHNICAL_DETAILS")):
                # If it's not a marker and not empty, add it as an item
                items.append(line)

        return items

    async def ask_followup_question(self,
                                  security_event: Dict[str, Any],
                                  question: str,
                                  previous_context: str) -> str:
        """Ask a follow-up question about a security event"""
        prompt = f"""
        As a cybersecurity expert, answer this follow-up question about a security event:

        Original Security Event:
        {json.dumps(security_event, indent=2)}

        Previous Context:
        {previous_context}

        Follow-up Question:
        {question}

        Provide a detailed and accurate response focusing specifically on answering the question.
        """

        response = await self.generate_content(prompt)
        return response
