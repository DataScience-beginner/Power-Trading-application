# Python backend
FROM python:3.11-slim

# Install system dependencies including LibreOffice for .xls conversion
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    libreoffice \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Build frontend
RUN cd frontend-react && \
    npm install && \
    npm run build && \
    cd ..

# Expose port
EXPOSE 8000

# Start server (database will initialize on startup)
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
