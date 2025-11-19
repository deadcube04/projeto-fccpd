# Dockerfile para o Leitor de Dados
FROM python:3.11-alpine

LABEL maintainer="Desafio 2 - Volumes e Persistência"
LABEL description="Container leitor de dados persistidos"

WORKDIR /app

# Instala dependências do sistema
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY reader.py .

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Comando de execução
CMD ["python", "reader.py"]
