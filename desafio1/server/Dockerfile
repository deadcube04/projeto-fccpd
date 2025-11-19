# Dockerfile para o Servidor Flask
# Usa imagem oficial Python Alpine (mais leve)
FROM python:3.11-alpine

# Define metadata do container
LABEL maintainer="Desafio 1 - Containers em Rede"
LABEL description="Servidor Web Flask na porta 8080"

# Define diretório de trabalho
WORKDIR /app

# Instala curl para healthcheck
RUN apk add --no-cache curl

# Copia requirements e instala dependências
# (Copia requirements primeiro para aproveitar cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY app.py .

# Expõe a porta 8080
EXPOSE 8080

# Define variáveis de ambiente
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Healthcheck para verificar se o servidor está respondendo
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando para executar a aplicação
CMD ["python", "app.py"]
