FROM python:3.12-slim

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set working directory
WORKDIR /app

# Copy only requirements to install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Change ownership of the directory
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the app's port
EXPOSE 3001

# Run the app
CMD ["python3", "/app/main.py"]
