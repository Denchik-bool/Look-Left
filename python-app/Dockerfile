# Use an official Python base image
FROM python:3.8-slim

# Install necessary tools
RUN apt-get update && apt-get install -y \
    zabbix-sender \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask app's port
EXPOSE 5000

# Run the application
CMD ["python", "python_metrics.py"]
