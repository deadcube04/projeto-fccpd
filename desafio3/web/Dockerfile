# Dockerfile para API Gateway
FROM python:3.11-alpine

LABEL maintainer="Desafio 3 - Docker Compose"
LABEL description="API Gateway com PostgreSQL e Redis"

WORKDIR /app

# Instala dependências do sistema
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev curl

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY app.py .

# Expõe porta 8000
EXPOSE 8000

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de execução
CMD ["python", "app.py"]
