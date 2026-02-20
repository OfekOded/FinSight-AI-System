FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2-binary

COPY server/ server/
COPY .env .env

EXPOSE 8000

ENV OLLAMA_BASE_URL="http://host.docker.internal:11434"

CMD ["sh", "-c", "python server/services/auth_service.py & python server/services/finance_service.py & python server/services/ai_service.py & uvicorn server.api_gateway:app --host 0.0.0.0 --port 8000"]