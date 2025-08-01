FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Expose the port your app runs on
EXPOSE 3001

# Run the Python application
CMD ["python3", "/app/main.py"]
