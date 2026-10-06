#!/usr/bin/env bash
# Levanta el Sistema Final con un solo comando:
#   1. valida que el .env tenga las claves necesarias,
#   2. indexa el corpus en Pinecone (idempotente: solo reindexa lo que cambio),
#   3. arranca la API en http://127.0.0.1:${PORT:-8000} (docs en /docs).
# Uso: ./run.sh   (requiere Python 3.12+ y las dependencias de requirements.txt)
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python}"

if [ ! -f .env ]; then
  echo "Falta .env: copia .env.example a .env y completa las claves." >&2
  exit 1
fi

# Carga solo las lineas CLAVE=valor (como python-dotenv). No se hace "source":
# eso ejecutaria cualquier linea suelta del .env como comando.
while IFS= read -r linea || [ -n "$linea" ]; do
  linea="${linea%$'\r'}"
  if [[ "$linea" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
    clave="${linea%%=*}"
    valor="${linea#*=}"
    # Quita espacios y comillas alrededor del valor, como hace python-dotenv.
    valor="${valor#"${valor%%[![:space:]]*}"}"
    valor="${valor%"${valor##*[![:space:]]}"}"
    valor="${valor#\"}"; valor="${valor%\"}"
    valor="${valor#\'}"; valor="${valor%\'}"
    export "$clave=$valor"
  fi
done < .env

for var in GROQ_API_KEY PINECONE_API_KEY REDIS_URL; do
  if [ -z "${!var:-}" ]; then
    echo "Falta ${var} en .env" >&2
    exit 1
  fi
done

echo "==> Indexando el corpus en Pinecone (idempotente)"
"$PYTHON" -m sistema_final.rag.ingest

echo "==> Levantando la API en el puerto ${PORT:-8000}"
exec "$PYTHON" -m uvicorn sistema_final.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
