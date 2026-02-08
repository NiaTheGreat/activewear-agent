FROM python:3.12-slim

WORKDIR /app

# Install system deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install all Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy agent source (lazily imported by agent_service.py at search time)
COPY src/ ./src/
COPY config/ ./config/

WORKDIR /app/backend
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
