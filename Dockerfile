# Multi-stage build for Power Trading Application
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend-react/package*.json ./
RUN npm install
COPY frontend-react/ ./
RUN npm run build

# Python backend with built frontend
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY database/ ./database/
COPY parsers/ ./parsers/
COPY schemas/ ./schemas/
COPY init_database.py .
COPY generate_mock_reports.py .
COPY upload_mock_reports.py .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend-react/dist

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
python init_database.py\n\
python generate_mock_reports.py\n\
python upload_mock_reports.py\n\
uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}\n\
' > /app/start.sh && chmod +x /app/start.sh

# Use startup script
CMD ["/bin/bash", "/app/start.sh"]
