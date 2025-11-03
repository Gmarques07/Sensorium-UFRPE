# Usar uma imagem base oficial do Python 3.12
FROM python:3.12-slim

# Evitar escrita de pyc e output bufferizado
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

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
       procps \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar cache do docker
COPY requirements.txt ./

# Instalar dependências
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do projeto
COPY . .

# Expôr a porta que a aplicação roda
EXPOSE 8001