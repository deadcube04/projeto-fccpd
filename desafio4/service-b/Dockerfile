FROM python:3.11-alpine

# Metadata
LABEL maintainer="Gabriel Melo"
LABEL description="Profile Service - Microservice B"

# Instala curl para healthcheck
RUN apk add --no-cache curl

# Diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY app.py .

# Expõe porta do serviço
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Comando para iniciar
CMD ["python", "app.py"]
