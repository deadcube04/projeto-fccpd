# Dockerfile para a Aplicação Flask
FROM python:3.11-alpine

LABEL maintainer="Desafio 2 - Volumes e Persistência"
LABEL description="Aplicação Flask de gerenciamento de tarefas"

WORKDIR /app

# Instala dependências do sistema necessárias para psycopg2
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev curl

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY app.py .

# Expõe a porta 5000
EXPOSE 5000

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de execução
CMD ["python", "app.py"]
