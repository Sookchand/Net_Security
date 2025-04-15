"""
Main application file for the Network Security AI Platform.

This file serves as the entry point for the application and imports the necessary
components from the enhanced_app_with_templates.py file.

Usage:
    python run_app.py

After running, access the application at:
    http://localhost:8000 or http://127.0.0.1:8000
"""

from enhanced_app_with_templates import app
import uvicorn
import sys

def main():
    """Run the application using uvicorn."""
    host = "127.0.0.1"  # Use 127.0.0.1 instead of 0.0.0.0 for better browser compatibility
    port = 8000
    reload = True

    print(f"\n{'=' * 60}\n Network Security AI Platform \n{'=' * 60}")
    print(f"\nStarting server at http://{host}:{port}")
    print(f"Access the application in your browser at: http://{host}:{port}")
    print(f"Press Ctrl+C to stop the server\n{'=' * 60}\n")

    try:
        uvicorn.run("enhanced_app_with_templates:app", host=host, port=port, reload=reload)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
