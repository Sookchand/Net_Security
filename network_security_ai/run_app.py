#!/usr/bin/env python3
"""
Run script for Network Security AI Platform
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """Run the application"""
    # Get configuration from environment variables
    host = "0.0.0.0"
    port = 8000
    debug = True
    
    print(f"Starting Network Security AI Platform on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug
    )

if __name__ == "__main__":
    main()
