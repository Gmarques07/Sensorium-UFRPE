FROM python:3.12-slim

# Evitar escrita de pyc e output bufferizado
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema necessárias para compilação de algumas wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libssl-dev \
       libffi-dev \
       default-libmysqlclient-dev \
       gcc \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar cache do docker
COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir bcrypt==4.3.0 passlib==1.7.4

# Copiar o código do backend
COPY . /app

# Garantir que o pacote app seja importável
ENV PYTHONPATH=/app

EXPOSE 8001

# Comando padrão para iniciar a API
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
