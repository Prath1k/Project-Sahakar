# Use lightweight Python 3.10 image
FROM python:3.10-slim

# Install system dependencies required for audio processing and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create user with UID 1000 (required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies as non-root user
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code with correct permissions
COPY --chown=user app/ ./app/

# Expose FastAPI port (Hugging Face Spaces requires 7860)
ENV PORT=7860
EXPOSE $PORT

# Set Python path
ENV PYTHONPATH=/app/app

# Run FastAPI server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
