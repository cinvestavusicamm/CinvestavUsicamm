<<<<<<< HEAD
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["uvicorn", "infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8003"]
=======
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8003"]
>>>>>>> agente-prueba
