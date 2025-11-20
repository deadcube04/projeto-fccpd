FROM python:3.11-alpine

LABEL maintainer="Gabriel Melo"
LABEL description="API Gateway"

RUN apk add --no-cache curl

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app.py"]
