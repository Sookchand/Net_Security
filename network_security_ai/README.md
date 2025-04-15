# Network Security AI Platform

An advanced network security analysis platform powered by Google's Gemini API and Retrieval-Augmented Generation (RAG) technology.

## Features

- **Natural Language Security Insights**: Generate human-readable explanations of security events using Gemini API
- **Retrieval-Augmented Generation (RAG)**: Enhance insights with context from similar historical events
- **Interactive Q&A**: Ask follow-up questions about security events and get detailed responses
- **Drift Detection**: Identify anomalies in network traffic patterns
- **Attack Analysis**: Analyze and explain potential security attacks
- **Interactive Visualizations**: Visualize security data with interactive charts
- **Vector Database**: Store and retrieve similar security events using semantic search

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Network Security AI Platform                        │
│                                                                         │
│  ┌───────────────┐    ┌───────────────────────┐    ┌───────────────┐    │
│  │ Network Data  │    │  Data Processing &    │    │  Security     │    │
│  │ Collection    │───▶│  Drift Detection      │───▶│  Dashboard    │    │
│  └───────────────┘    └───────────────────────┘    └───────────────┘    │
│                                   │                         ▲            │
│                                   ▼                         │            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │           Gemini-Powered Security Insights Generator              │  │
│  │                                                                   │  │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────┐  │  │
│  │  │ Vector DB   │   │ Gemini API  │   │ Interactive Analysis    │  │  │
│  │  │ & RAG System│──▶│ Integration │──▶│ & Response Generation   │  │  │
│  │  │             │   │             │   │                         │  │  │
│  │  └─────────────┘   └─────────────┘   └─────────────────────────┘  │  │
│  │         │                 │                      │                 │  │
│  │         │                 │                      │                 │  │
│  │         ▼                 ▼                      ▼                 │  │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────┐  │  │
│  │  │ Threat      │   │ Embedding   │   │ GenAI Agents for        │  │  │
│  │  │ Prioritization│  │ Generation  │   │ Automated Response      │  │  │
│  │  └─────────────┘   └─────────────┘   └─────────────────────────┘  │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
network_security_ai/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI main application
│   ├── config.py                # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── security_event.py    # Data models for security events
│   │   └── insights.py          # Data models for insights
│   ├── services/
│   │   ├── __init__.py
│   │   ├── drift_detector.py    # Drift detection service
│   │   ├── gemini_service.py    # Gemini API integration
│   │   ├── knowledge_base.py    # Vector DB and RAG system
│   │   ├── embedding_service.py # Embedding generation
│   │   └── insights_service.py  # Security insights generation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py            # API endpoints
│   │   └── dependencies.py      # API dependencies
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css       # CSS styles
│   │   ├── js/
│   │   │   ├── dashboard.js     # Dashboard functionality
│   │   │   └── charts.js        # Chart generation
│   │   └── img/                 # Images
│   └── templates/
│       ├── index.html           # Main dashboard
│       ├── insights.html        # Insights page
│       └── components/          # Reusable components
│           ├── header.html
│           └── footer.html
├── data/
│   ├── vector_db/              # Vector database storage
│   └── sample_events.json      # Sample security events
├── tests/
│   ├── __init__.py
│   ├── test_drift_detector.py
│   ├── test_gemini_service.py
│   └── test_insights_service.py
├── requirements.txt            # Project dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # Project documentation
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/network-security-ai.git
   cd network-security-ai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemini-pro
   ```

## Running the Application

1. Start the application:
   ```bash
   cd network_security_ai
   uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

3. API documentation is available at:
   ```
   http://localhost:8000/api/docs
   ```

## Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t network-security-ai .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name network-security-ai network-security-ai
   ```

## API Endpoints

- `GET /api/health`: Health check endpoint
- `POST /api/events/drift`: Process a drift detection event
- `POST /api/events/attack`: Process an attack event
- `POST /api/events`: Process a generic security event
- `POST /api/conversation/start`: Start a new conversation about a security event
- `POST /api/conversation/question`: Ask a follow-up question in a conversation
- `GET /api/sample/drift`: Get a sample drift event with insights
- `GET /api/sample/attack`: Get a sample attack event with insights

## Technologies Used

- **Backend**: FastAPI, Python 3.10+
- **AI**: Google Gemini API, Sentence Transformers
- **Vector Database**: FAISS
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5, Plotly.js
- **Containerization**: Docker

## License

MIT

## Acknowledgements

- Google Gemini API
- Sentence Transformers
- FAISS
- FastAPI
- Plotly.js
