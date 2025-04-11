# --- Builder Stage ---
    FROM python:3.10-slim-buster AS builder
    WORKDIR /build
    
    # Copy only the requirements file first to leverage Docker cache
    COPY requirements.txt .
    
    # Install dependencies
    RUN apt-get update -y && apt-get install -y --no-install-recommends \
        build-essential \
        && apt-get clean && rm -rf /var/lib/apt/lists/*
    
    RUN pip install --no-cache-dir -r requirements.txt
    
    # --- Final Stage ---
    FROM python:3.10-slim-buster
    WORKDIR /app
    
    # Copy the application code
    COPY . /app
    
    # Copy the virtual environment from the builder stage
    COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
    
    #CMD ["python3", "app.py"]
    CMD ["python", "/app/app.py"]