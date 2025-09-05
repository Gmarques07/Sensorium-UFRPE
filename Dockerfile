# Usar uma imagem base oficial do Python
FROM python:3.9-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do backend para o diretório de trabalho
COPY . .

# Expôr a porta que a aplicação roda
EXPOSE 8001

# Comando para rodar a aplicação
CMD ["python", "backend/main.py"]