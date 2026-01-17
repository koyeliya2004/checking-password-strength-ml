# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-consolidated.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-consolidated.txt

# Copy the entire application
COPY password-ml-app/ ./password-ml-app/

# Copy essential model files from root to the app models directory
# These are needed for ML predictions
COPY enhancedpasswordmodel.pkl ./password-ml-app/models/
COPY password_improvement_model.pkl ./password-ml-app/models/
COPY tfidf_vectorizer_1.pkl ./password-ml-app/models/
COPY reuse_list.txt ./password-ml-app/models/

# Set working directory to the app folder
WORKDIR /app/password-ml-app

# Expose port (configurable via PORT env var)
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run the application with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app
