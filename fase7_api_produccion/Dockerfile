# Build context: la RAIZ del repo (no esta carpeta), porque la API
# reutiliza codigo de fases anteriores (fase3_ejercicio_chromadb,
# fase6_orquestador_multiagente, etc.) - ver docker-compose.yml.
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "fase7_api_produccion.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
