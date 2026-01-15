FROM python:3.11-slim

# Metadata
LABEL maintainer="David <l.davidescobedo15@gmail.com>"
LABEL description="DVD Rental API - FastAPI"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app/ ./app/

# Usuario no-root
RUN groupadd -r fastapi --gid=1001 && \
    useradd -r -g fastapi --uid=1001 -m fastapi && \
    chown -R fastapi:fastapi /app

USER fastapi

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]