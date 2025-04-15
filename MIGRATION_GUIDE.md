# Migration Guide

This guide will help you migrate from the old project structure to the new, more organized structure.

## New Directory Structure

```
Net_Security/
├── app/                      # Web application files
│   ├── static/               # Static assets (CSS, JS, images)
│   └── templates/            # HTML templates
├── data/                     # Data directory
│   ├── raw/                  # Raw data files
│   └── processed/            # Processed data files
├── models/                   # Model files
│   ├── baseline/             # Baseline model
│   └── current/              # Current model
├── networksecurity/          # Core package
│   ├── components/           # Components
│   ├── constant/             # Constants
│   ├── entity/               # Entities
│   ├── exception/            # Exceptions
│   ├── logging/              # Logging
│   ├── pipeline/             # Pipelines
│   └── utils/                # Utilities
├── scripts/                  # Scripts
│   ├── deployment/           # Deployment scripts
│   └── testing/              # Testing scripts
├── docs/                     # Documentation
├── tests/                    # Tests
├── .env                      # Environment variables
├── requirements_consolidated.txt  # Main requirements file
├── Dockerfile.consolidated   # Main Dockerfile
├── enhanced_app_with_templates.py # Main application file with templates
├── run_app.py                # Entry point for running the application
└── README.md                 # Project README
```

## Migration Steps

### 1. Run the Cleanup Script

Run the cleanup script to create the new directory structure and move files to their appropriate locations:

```
python cleanup.py
```

### 2. Update Import Paths

Update import paths in Python files to reflect the new directory structure. For example:

Old:
```python
from networksecurity.components.data_validation import DataValidation
```

New:
```python
from networksecurity.components.data_validation import DataValidation
```

(In this case, the import path remains the same because we're keeping the `networksecurity` package structure.)

### 3. Update Configuration Files

Update configuration files to reflect the new directory structure:

- Update paths in `.env` files
- Update paths in configuration files
- Update paths in deployment scripts

### 4. Test the Application

Test the application to ensure it works with the new directory structure:

```
python run_app.py
```

Or with uvicorn directly:

```
uvicorn enhanced_app_with_templates:app --reload
```

### 5. Remove Unnecessary Files

After confirming that the application works with the new structure, you can remove unnecessary files:

- Duplicate Dockerfiles (keep only `Dockerfile.consolidated`)
- Duplicate requirement files (keep only `requirements_consolidated.txt`)
- Duplicate deployment scripts (keep only those in `scripts/deployment`)
- Test files that are no longer needed
- Temporary files and outputs

## Running the Application

### Local Development

Run the application using:
```
python run_app.py
```

Or with uvicorn directly:
```
uvicorn enhanced_app_with_templates:app --reload
```

### Docker Deployment

Build and run the Docker container:
```
docker build -t networksecurity:latest -f Dockerfile.consolidated .
docker run -p 8000:8000 networksecurity:latest
```

### Deployment to EC2

Deploy to an EC2 instance using:
```
python scripts/deployment/deploy.py --key your-key.pem --host your-ec2-host.compute.amazonaws.com --templates
```
