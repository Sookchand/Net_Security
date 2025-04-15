# Network Security Application: Running Commands Guide

This document explains the different commands used to run and deploy the Network Security application.

## Local Development Commands

### 1. `uvicorn enhanced_app_with_templates:app --reload`

This is the original command used for local development:
- Directly runs the FastAPI application using the Uvicorn ASGI server
- Uses `enhanced_app_with_templates.py` as the source file
- The `--reload` flag automatically reloads the application when code changes
- Used during development and testing on your local machine

### 2. `python run_app.py` (New Command)

This is the new command introduced in the reorganized project structure:
- A simple Python wrapper around the Uvicorn command
- Internally calls the same Uvicorn command
- Provides a more standard and easier-to-remember way to start the application
- Can be extended with additional configuration options if needed

The content of `run_app.py` is:

```python
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
```

## Deployment Commands

### 1. `python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com --templates`

This command deploys the template-based version of the application to EC2:
- Uses the `deploy.py` script to handle the deployment process
- The `--key` parameter specifies your SSH key for connecting to EC2
- The `--host` parameter specifies your EC2 instance address
- The `--templates` flag deploys the version with HTML templates (full web interface)
- Used for production deployment

### 2. `python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com --enhanced`

This command deploys the enhanced version without templates to EC2:
- Similar to the previous command
- The `--enhanced` flag deploys the enhanced version without templates
- Used when you want a simpler deployment without the full web interface

## Command Comparison

| Command | Purpose | Environment | Features |
|---------|---------|-------------|----------|
| `uvicorn enhanced_app_with_templates:app --reload` | Local development | Local | Auto-reload, direct |
| `python run_app.py` | Local development | Local | Auto-reload, easier to remember |
| `python deploy.py --key ... --host ... --templates` | Production deployment | EC2 | Full web interface |
| `python deploy.py --key ... --host ... --enhanced` | Production deployment | EC2 | Basic interface |

## When to Use Each Command

- **During development**: Use `python run_app.py` or `uvicorn enhanced_app_with_templates:app --reload`
  - Access the application at: http://localhost:8000 or http://127.0.0.1:8000
- **For production**: Use `python deploy.py --key ... --host ... --templates`
  - Access the application at: http://your-ec2-host.compute.amazonaws.com:8000
- **For testing deployment**: Use `python deploy.py --key ... --host ... --enhanced`
  - Access the application at: http://your-ec2-host.compute.amazonaws.com:8000

> **Note**: When using `0.0.0.0` as the host (as in the original Uvicorn command), you should still access the application using `localhost` or `127.0.0.1` in your browser. The `0.0.0.0` address means "listen on all available network interfaces" but is not meant to be used as a destination in your browser.

## Benefits of `run_app.py`

1. **Simplicity**: Easier to remember than the Uvicorn command
2. **Standardization**: Follows Python conventions for entry points
3. **Extensibility**: Can be modified to add configuration options
4. **IDE Integration**: Works well with IDE run configurations
5. **Consistency**: Provides a consistent way to start the application

## Future Enhancements

The `run_app.py` script could be enhanced to:
- Accept command-line arguments for host, port, etc.
- Load configuration from a file
- Set up logging
- Initialize resources before starting the server
- Provide different run modes (development, production, etc.)
