FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p instance app/static/uploads

# Set permissions
RUN chmod +x run.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
