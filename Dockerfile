# Use official Python slim image for smaller footprint
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code
COPY app.py .

# Expose port (Render typically uses PORT env, defaulting to 10000 if not set)
EXPOSE 10000

# Run with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", "--workers", "2", "--timeout", "120", "app:app"]
