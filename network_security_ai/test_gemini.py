#!/usr/bin/env python3
"""
Test script for Gemini API connection
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def main():
    """Test Gemini API connection"""
    # Get API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return

    print(f"Using API key: {api_key[:5]}...{api_key[-5:]}")

    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)

        # List available models
        print("Available models:")
        for m in genai.list_models():
            print(f"- {m.name}")

        # Create a model
        model = genai.GenerativeModel(
            model_name="models/gemini-pro",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )

        # Generate content
        response = model.generate_content("Explain what a DDoS attack is in one paragraph.")

        print("\nGemini API Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        print("\nGemini API connection test successful!")

    except Exception as e:
        print(f"\nError testing Gemini API connection: {str(e)}")

if __name__ == "__main__":
    main()
