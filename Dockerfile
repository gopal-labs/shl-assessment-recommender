FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for compiling some python packages if any)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure data directories exist
RUN mkdir -p data/raw data/processed data/faiss_index

# Fetch data and build FAISS index during build
RUN python scripts/scrape_catalog.py
RUN python scripts/build_index.py

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
