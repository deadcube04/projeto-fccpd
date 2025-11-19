# Dockerfile para o Cliente HTTP
# Usa imagem oficial Python Alpine (mais leve)
FROM python:3.11-alpine

# Define metadata do container
LABEL maintainer="Desafio 1 - Containers em Rede"
LABEL description="Cliente HTTP que faz requisições periódicas"

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências
# (Copia requirements primeiro para aproveitar cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY client.py .

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Comando para executar a aplicação
CMD ["python", "client.py"]
