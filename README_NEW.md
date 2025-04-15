# Network Security AI Platform

A machine learning platform for detecting and analyzing network security threats.

## Project Structure

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

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Docker (optional)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Net_Security.git
   cd Net_Security
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```
   pip install -r requirements_consolidated.txt
   ```

### Running the Application

#### Local Development

Run the application using:
```
python run_app.py
```

Or with uvicorn directly:
```
uvicorn enhanced_app_with_templates:app --reload
```

#### Docker Deployment

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

## Features

- **Network Traffic Analysis**: Detect potential security threats in network traffic
- **Email & Text Analysis**: Analyze emails and text content for security threats
- **Data Drift Detection**: Monitor changes in data distribution
- **Model Drift Detection**: Monitor changes in model performance
- **Interactive Visualizations**: View results with interactive charts and tables

## License

This project is licensed under the MIT License - see the LICENSE file for details.
