from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import uvicorn
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
import random
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(title="Network Security API")
origins = ["*"]

# Root endpoint for health checks
@app.get("/")
async def root():
    return {"status": "healthy", "message": "Network Security API is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample attack types
ATTACK_TYPES = ["Normal", "DoS", "Probe", "R2L", "U2R"]

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Make predictions on network traffic data
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        with open("temp_upload.csv", "wb") as f:
            f.write(contents)
        
        # Load the data
        df = pd.read_csv("temp_upload.csv")
        
        # Generate simulated predictions
        predictions = []
        for _ in range(len(df)):
            # Simulate predictions with a bias towards Normal
            attack_type = random.choices(
                ATTACK_TYPES, 
                weights=[0.7, 0.1, 0.1, 0.05, 0.05], 
                k=1
            )[0]
            predictions.append(attack_type)
        
        # Add predictions to the dataframe
        df["predicted_attack"] = predictions
        
        # Count attack types
        attack_counts = df["predicted_attack"].value_counts().to_dict()
        
        # Calculate statistics
        total_records = len(df)
        total_attacks = sum(count for attack_type, count in attack_counts.items() if attack_type != "Normal")
        attack_percentage = (total_attacks / total_records) * 100 if total_records > 0 else 0
        
        # Generate a threat score (0-100)
        threat_score = min(100, int(attack_percentage * 1.5))
        
        # Create a summary
        if threat_score < 10:
            summary = "No significant threats detected in the network traffic."
        elif threat_score < 30:
            summary = "Low level of potential threats detected. Routine monitoring recommended."
        elif threat_score < 60:
            summary = "Moderate level of threats detected. Investigation recommended."
        else:
            summary = "High level of threats detected! Immediate investigation required."
        
        # Create recommendations based on threat score
        recommendations = []
        if threat_score > 0:
            recommendations.append("Review security logs for suspicious activities")
        if threat_score > 20:
            recommendations.append("Update firewall rules to block suspicious IP addresses")
        if threat_score > 40:
            recommendations.append("Implement additional network monitoring")
        if threat_score > 60:
            recommendations.append("Isolate affected systems for further investigation")
        if threat_score > 80:
            recommendations.append("Engage security incident response team immediately")
        
        # Create response
        response = {
            "status": "success",
            "prediction_summary": {
                "total_records": total_records,
                "total_attacks": total_attacks,
                "attack_percentage": round(attack_percentage, 2),
                "threat_score": threat_score,
                "attack_distribution": attack_counts
            },
            "analysis": {
                "summary": summary,
                "recommendations": recommendations
            },
            "data_preview": df.head(10).to_dict(orient="records")
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/analyze-text")
async def analyze_text(request: Request):
    """Analyze text content for security threats"""
    try:
        # Parse the request body
        body = await request.json()
        text_content = body.get("text_content")
        
        if not text_content:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Text content is required"
                }
            )
        
        # Check for common phishing indicators
        phishing_score = 0
        malware_score = 0
        social_engineering_score = 0
        spam_score = 0
        scam_score = 0
        
        # Simple keyword-based analysis
        phishing_keywords = ["verify your account", "confirm your identity", "update your information", 
                            "click here", "login to your account", "unusual activity", "suspended"]
        
        malware_keywords = ["attachment", "download", "execute", "invoice", "doc file", "zip file", 
                           "enable macros", "enable content"]
        
        social_engineering_keywords = ["urgent", "immediate action", "limited time", "act now", 
                                      "important notice", "security alert", "problem with your account"]
        
        spam_keywords = ["offer", "free", "discount", "save money", "best price", "buy now", 
                        "limited offer", "exclusive deal"]
        
        scam_keywords = ["lottery", "winner", "inheritance", "million dollars", "prince", "overseas", 
                        "transaction", "wire transfer", "western union"]
        
        # Calculate scores based on keyword matches
        for keyword in phishing_keywords:
            if keyword.lower() in text_content.lower():
                phishing_score += 20
        
        for keyword in malware_keywords:
            if keyword.lower() in text_content.lower():
                malware_score += 20
        
        for keyword in social_engineering_keywords:
            if keyword.lower() in text_content.lower():
                social_engineering_score += 15
        
        for keyword in spam_keywords:
            if keyword.lower() in text_content.lower():
                spam_score += 10
        
        for keyword in scam_keywords:
            if keyword.lower() in text_content.lower():
                scam_score += 25
        
        # Cap scores at 100
        phishing_score = min(100, phishing_score)
        malware_score = min(100, malware_score)
        social_engineering_score = min(100, social_engineering_score)
        spam_score = min(100, spam_score)
        scam_score = min(100, scam_score)
        
        # Calculate overall threat score
        threat_score = int((phishing_score * 0.3) + (malware_score * 0.3) + 
                          (social_engineering_score * 0.2) + (spam_score * 0.1) + (scam_score * 0.1))
        
        # Determine threat level
        if threat_score < 20:
            threat_level = "Safe"
            summary = "The content appears to be safe with no significant security threats detected."
        elif threat_score < 40:
            threat_level = "Low Risk"
            summary = "The content has some minor indicators of suspicious activity but is likely safe."
        elif threat_score < 60:
            threat_level = "Medium Risk"
            summary = "The content contains several suspicious elements that warrant caution."
        elif threat_score < 80:
            threat_level = "High Risk"
            summary = "The content contains multiple indicators of malicious intent. Exercise extreme caution."
        else:
            threat_level = "Critical Risk"
            summary = "The content is highly likely to be malicious. Do not interact with it."
        
        # Generate detailed summary
        detailed_summary = f"Analysis indicates this is a {threat_level.lower()} message. "
        
        if phishing_score > 50:
            detailed_summary += "It contains multiple phishing indicators attempting to steal credentials or personal information. "
        
        if malware_score > 50:
            detailed_summary += "It likely contains or references malicious attachments or downloads. "
        
        if social_engineering_score > 50:
            detailed_summary += "It uses social engineering tactics to manipulate the recipient. "
        
        if spam_score > 50:
            detailed_summary += "It has characteristics of unsolicited commercial content. "
        
        if scam_score > 50:
            detailed_summary += "It shows patterns consistent with common scams. "
        
        # Generate threats list
        threats = []
        if phishing_score > 30:
            threats.append({
                "type": "Phishing",
                "description": "Attempts to steal sensitive information by impersonating a trustworthy entity"
            })
        
        if malware_score > 30:
            threats.append({
                "type": "Malware",
                "description": "May contain or link to malicious software that can harm your system"
            })
        
        if social_engineering_score > 30:
            threats.append({
                "type": "Social Engineering",
                "description": "Uses psychological manipulation to trick users into making security mistakes"
            })
        
        if spam_score > 50:
            threats.append({
                "type": "Spam",
                "description": "Unsolicited bulk message, typically for commercial purposes"
            })
        
        if scam_score > 30:
            threats.append({
                "type": "Scam",
                "description": "Fraudulent scheme designed to trick people out of money or information"
            })
        
        # Generate recommendations
        recommendations = ["Do not click on any links in the message"]
        
        if phishing_score > 30:
            recommendations.append("Do not provide any personal information or credentials")
        
        if malware_score > 30:
            recommendations.append("Do not download or open any attachments")
        
        if threat_score > 50:
            recommendations.append("Report this message to your IT security team")
        
        if threat_score > 70:
            recommendations.append("Delete this message immediately")
        
        # Create analysis result
        analysis = {
            "threat_score": threat_score,
            "summary": summary,
            "detailed_summary": detailed_summary,
            "threats": threats,
            "threat_categories": {
                "Phishing": phishing_score,
                "Malware": malware_score,
                "Social Engineering": social_engineering_score,
                "Spam": spam_score,
                "Scam": scam_score
            },
            "recommendations": recommendations
        }
        
        return {
            "status": "success",
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error analyzing text: {str(e)}"
            }
        )

@app.post("/ask-about-text-analysis")
async def ask_about_text_analysis(request: Request):
    """Answer questions about text analysis results"""
    try:
        # Parse the request body
        body = await request.json()
        question = body.get("question")
        
        if not question:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Question is required"
                }
            )
        
        # Simple Q&A system with predefined answers
        answers = {
            "phishing": "Phishing is a type of cyber attack where attackers impersonate trusted entities to steal sensitive information like passwords or credit card details. Look for suspicious links, urgent requests, and poor grammar.",
            "malware": "Malware is malicious software designed to damage or gain unauthorized access to systems. Be cautious of unexpected attachments, executable files, and requests to enable macros in documents.",
            "social engineering": "Social engineering manipulates people into breaking security procedures or revealing sensitive information. It often exploits human psychology using urgency, fear, or authority.",
            "spam": "Spam refers to unsolicited bulk messages, typically for commercial purposes. While annoying, not all spam is malicious, but it can sometimes contain phishing attempts or malware.",
            "scam": "Scams are fraudulent schemes designed to trick people out of money or information. Common examples include lottery scams, inheritance scams, and romance scams.",
            "protection": "To protect yourself from email threats: 1) Don't click suspicious links, 2) Don't open unexpected attachments, 3) Verify sender identities, 4) Use multi-factor authentication, 5) Keep software updated.",
            "indicators": "Common indicators of malicious emails include: urgent language, grammar errors, suspicious sender addresses, unexpected attachments, requests for sensitive information, and suspicious links.",
            "report": "If you receive a suspicious email, don't interact with it. Report it to your IT department or security team, and delete it from your inbox."
        }
        
        # Process the question and find the most relevant answer
        question_lower = question.lower()
        
        if "phishing" in question_lower or "fake email" in question_lower:
            answer = answers["phishing"]
        elif "malware" in question_lower or "virus" in question_lower:
            answer = answers["malware"]
        elif "social engineering" in question_lower or "manipulate" in question_lower:
            answer = answers["social engineering"]
        elif "spam" in question_lower:
            answer = answers["spam"]
        elif "scam" in question_lower or "fraud" in question_lower:
            answer = answers["scam"]
        elif "protect" in question_lower or "prevent" in question_lower or "avoid" in question_lower:
            answer = answers["protection"]
        elif "indicator" in question_lower or "sign" in question_lower or "tell" in question_lower:
            answer = answers["indicators"]
        elif "report" in question_lower or "what should i do" in question_lower:
            answer = answers["report"]
        else:
            answer = "I don't have specific information about that. Generally, be cautious with unexpected emails, don't click suspicious links, and never share sensitive information in response to email requests."
        
        return {
            "answer": answer
        }
        
    except Exception as e:
        logger.error(f"Error answering text analysis question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error answering question: {str(e)}"
            }
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
