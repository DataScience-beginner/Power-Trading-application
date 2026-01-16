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

# Start server directly (database will auto-create on first request)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
