import os
import google.generativeai as genai

# Set up the API key
api_key = "GEMINI_API_KEY"
genai.configure(api_key=api_key)

# List available models
print("Available models:")
for m in genai.list_models():
    print(f"- {m.name}")

# Create a model
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

# Generate content
response = model.generate_content("Explain what a DDoS attack is in one paragraph.")

print("\nGemini API Response:")
print("-" * 50)
print(response.text)
print("-" * 50)
