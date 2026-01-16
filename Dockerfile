# Python backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Build frontend inside the same container
RUN apt-get update && apt-get install -y nodejs npm && \
    cd frontend-react && \
    npm install && \
    npm run build && \
    cd .. && \
    apt-get remove -y nodejs npm && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 8000

# Start server
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
