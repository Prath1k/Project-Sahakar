# Use lightweight Python 3.10 image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for audio processing and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and voice tensors
COPY app/ ./app/
COPY voices/ ./voices/
COPY test_audio_output/ ./test_audio_output/

# Expose FastAPI port (Hugging Face Spaces defaults to 7860, Render uses 8000/10000)
ENV PORT=7860
EXPOSE $PORT

# Set Python path
ENV PYTHONPATH=/app/app

# Run FastAPI server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
