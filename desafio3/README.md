# Desafio 3 — Orquestração com Docker Compose

Este projeto demonstra a orquestração de múltiplos serviços interdependentes usando Docker Compose, implementando uma arquitetura completa com API Gateway, banco de dados relacional e cache distribuído.

## Descrição

Sistema de gerenciamento de produtos que integra três serviços principais:
- **Web (API Gateway)**: API REST em Flask que coordena requisições entre os serviços
- **PostgreSQL**: Banco de dados relacional para persistência
- **Redis**: Cache distribuído para otimização de performance

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
│                     (desafio3-network)                       │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │              │      │              │      │          │  │
│  │  PostgreSQL  │◄────►│  API Gateway │◄────►│  Redis   │  │
│  │   (postgres) │      │     (web)    │      │  (redis) │  │
│  │   port 5432  │      │   port 8000  │      │ port 6379│  │
│  │              │      │              │      │          │  │
│  └──────────────┘      └──────────────┘      └──────────┘  │
│         │                     │                     │       │
│         │                     │                     │       │
│    ┌────▼─────┐          Expõe           ┌─────▼──────┐    │
│    │ Volume:  │          porta           │  Volume:   │    │
│    │ postgres │          8000            │   redis    │    │
│    │   data   │                          │    data    │    │
│    └──────────┘                          └────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP Requests
                           ▼
                   ┌───────────────┐
                   │   Usuário     │
                   │ localhost:8000│
                   └───────────────┘
```

### Decisões Técnicas

#### 1. **Arquitetura de Microsserviços**
- **Separação de responsabilidades**: Cada serviço tem uma função específica
- **Acoplamento baixo**: Serviços comunicam via rede usando protocolos padrão
- **Escalabilidade**: Cada serviço pode ser escalado independentemente

#### 2. **Padrão API Gateway**
- Ponto único de entrada para requisições externas
- Coordena comunicação entre PostgreSQL e Redis
- Implementa lógica de negócio e validações
- Gerencia cache automático com estratégia de invalidação

#### 3. **Estratégia de Cache**
- **Cache-Aside Pattern**: Aplicação controla o cache
- **TTL (Time To Live)**: 5 minutos para listagem de produtos
- **Cache Invalidation**: Limpa cache ao modificar dados (POST/PUT/DELETE)
- **Métricas**: Rastreamento de hits/misses para monitoramento

#### 4. **Dependências entre Serviços**
```yaml
web:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
```
- **Health checks**: Garante que serviços estão prontos antes de iniciar dependentes
- **Ordem de inicialização**: postgres → redis → web
- **Graceful startup**: Evita erros de conexão durante inicialização

#### 5. **Gerenciamento de Configuração**
- **Environment Variables**: Configurações via docker-compose.yml
- **Secrets**: Credenciais do banco definidas no compose
- **Network isolation**: Rede interna isolada do host

## Funcionamento Detalhado

### 1. Inicialização dos Serviços

```bash
./scripts/start.sh
```

**Sequência de eventos:**

1. **Build das imagens**
   - `desafio3-web`: Cria imagem da API (Python 3.11-alpine + Flask)
   
2. **Inicialização do PostgreSQL**
   - Container `desafio3-postgres` inicia primeiro
   - Healthcheck verifica se aceita conexões: `pg_isready -U postgres`
   - Cria database `products_db` automaticamente
   - Inicializa tabela `products` com schema

3. **Inicialização do Redis**
   - Container `desafio3-redis` inicia após PostgreSQL estar healthy
   - Healthcheck verifica ping: `redis-cli ping`
   - Configura persistência RDB

4. **Inicialização da API Gateway**
   - Container `desafio3-web` inicia após ambos os serviços estarem healthy
   - Conecta ao PostgreSQL via hostname `postgres`
   - Conecta ao Redis via hostname `redis`
   - Healthcheck verifica endpoint: `curl -f http://localhost:8000/health`

### 2. Comunicação entre Serviços

#### Resolução de Nomes (DNS)
```python
# No código Python da API Gateway:
conn = psycopg2.connect(
    host='postgres',        # Docker Compose resolve para IP do container
    port=5432,
    dbname='products_db',
    user='postgres',
    password='postgres123'
)

redis_client = redis.Redis(
    host='redis',           # Docker Compose resolve para IP do container
    port=6379,
    decode_responses=True
)
```

Docker Compose cria entradas DNS automáticas para cada serviço usando o nome definido no `docker-compose.yml`.

#### Fluxo de Requisição (Listagem de Produtos)

```
1. Cliente HTTP → GET /products
                    │
                    ▼
2. API Gateway verifica cache
   └─► Redis: GET "products:all"
       │
       ├─► CACHE HIT: Retorna dados do cache (rápido)
       │
       └─► CACHE MISS:
           └─► PostgreSQL: SELECT * FROM products
               └─► Armazena no Redis com TTL 5min
               └─► Retorna dados
```

**Performance:**
- **Cache HIT**: ~2-5ms (Redis)
- **Cache MISS**: ~50-100ms (PostgreSQL + Redis)

### 3. Persistência de Dados

#### Volumes Nomeados
```yaml
volumes:
  postgres_data:     # Persiste dados do PostgreSQL
  redis_data:        # Persiste snapshots do Redis
```

**Ciclo de vida:**
- Dados sobrevivem a `docker compose down`
- Removidos apenas com `docker compose down -v`
- Podem ser inspecionados: `docker volume inspect desafio3_postgres_data`

### 4. Health Checks e Resiliência

Cada serviço define healthchecks customizados:

```yaml
# PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5

# Redis
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 3s
  retries: 5

# Web
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Como Executar

### Pré-requisitos
- Docker 20.10+
- Docker Compose v2.0+
- Porta 8000 disponível

### Passo 1: Iniciar o Ambiente

```bash
cd desafio3
./scripts/start.sh
```

O script irá:
- Construir as imagens
- Criar a rede Docker
- Iniciar os containers na ordem correta
- Aguardar todos os serviços ficarem healthy
- Exibir informações de status

### Passo 2: Popular com Dados

```bash
./scripts/populate.sh
```

Cria 8 produtos de exemplo em diferentes categorias:
- Eletrônicos (smartphone, notebook, fone)
- Livros (Clean Code, Design Patterns)
- Esportes (tênis, bicicleta)
- Casa (cafeteira)

### Passo 3: Testar a API

```bash
# Testes básicos da API
./scripts/test.sh

# Testar comunicação entre serviços
./scripts/test_communication.sh

# Demonstração de cache
./scripts/demo_cache.sh
```

### Passo 4: Monitorar

```bash
# Ver logs em tempo real
./scripts/logs.sh

# Ver status dos containers
docker compose ps

# Ver estatísticas de cache
curl http://localhost:8000/stats
```

## Endpoints da API

### Informações e Saúde

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações da API |
| GET | `/health` | Health check simplificado |
| GET | `/services` | Status detalhado de todos os serviços |
| GET | `/stats` | Estatísticas de cache e database |

### Gerenciamento de Produtos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/products` | Lista todos os produtos (cache 5min) |
| GET | `/products/<id>` | Busca produto por ID (cache 5min) |
| POST | `/products` | Cria novo produto (invalida cache) |
| PUT | `/products/<id>` | Atualiza produto (invalida cache) |
| DELETE | `/products/<id>` | Remove produto (invalida cache) |

### Cache

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| DELETE | `/cache/clear` | Limpa todo o cache |

### Exemplos de Uso

#### Criar Produto
```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Produto Teste",
    "description": "Descrição do produto",
    "price": 99.99,
    "stock": 100,
    "category": "electronics"
  }'
```

#### Listar Produtos
```bash
curl http://localhost:8000/products
```

#### Atualizar Produto
```bash
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Produto Atualizado",
    "price": 149.99,
    "stock": 50
  }'
```

#### Ver Estatísticas
```bash
curl http://localhost:8000/stats | python3 -m json.tool
```

## Demonstrações

### Demonstração 1: Cache em Ação

```bash
./scripts/demo_cache.sh
```

**O que demonstra:**
1. Limpa cache completamente
2. Primeira requisição (CACHE MISS - busca PostgreSQL)
3. Segunda requisição (CACHE HIT - busca Redis, muito mais rápido)
4. Mostra diferença de performance
5. Testa invalidação automática ao criar produto

**Resultado esperado:**
- Cache MISS: 50-100ms
- Cache HIT: 2-5ms (10-20x mais rápido)

### Demonstração 2: Comunicação entre Serviços

```bash
./scripts/test_communication.sh
```

**O que testa:**
1. Web → PostgreSQL (consultas SQL)
2. Web → Redis (operações de cache)
3. Resolução DNS interna (ping entre containers)
4. Acesso direto aos serviços via docker exec

### Demonstração 3: Dependências

**Teste de falha de dependência:**

```bash
# Para o PostgreSQL
docker stop desafio3-postgres

# Tenta usar a API
curl http://localhost:8000/products
# Resultado: Erro indicando que database está indisponível

# Reinicia PostgreSQL
docker start desafio3-postgres

# Aguarda health check
sleep 10

# API volta a funcionar
curl http://localhost:8000/products
```

## Verificações de Funcionamento

### 1. Verificar Containers Ativos
```bash
docker compose ps
```
Deve mostrar 3 containers com status "healthy".

### 2. Verificar Logs
```bash
docker compose logs web
docker compose logs postgres
docker compose logs redis
```

### 3. Verificar Rede
```bash
docker network inspect desafio3-network
```
Deve mostrar os 3 containers conectados com IPs na mesma subnet.

### 4. Verificar Volumes
```bash
docker volume ls | grep desafio3
```
Deve mostrar `desafio3_postgres_data` e `desafio3_redis_data`.

### 5. Testar Health Checks
```bash
curl http://localhost:8000/health
```
Deve retornar:
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "timestamp": "..."
}
```

### 6. Verificar Comunicação Interna
```bash
# Ping do web para postgres
docker exec desafio3-web ping -c 3 postgres

# Ping do web para redis
docker exec desafio3-web ping -c 3 redis
```

## Configurações

### Variáveis de Ambiente

#### PostgreSQL
```yaml
POSTGRES_DB: products_db
POSTGRES_USER: postgres
POSTGRES_PASSWORD: postgres123
```

#### Redis
```yaml
# Usa configurações padrão
# Persistência habilitada via volume
```

#### API Gateway
```yaml
# Conexões
POSTGRES_HOST: postgres
POSTGRES_PORT: 5432
POSTGRES_DB: products_db
POSTGRES_USER: postgres
POSTGRES_PASSWORD: postgres123

REDIS_HOST: redis
REDIS_PORT: 6379

# Cache
CACHE_TTL: 300  # 5 minutos
```

### Portas Expostas

| Serviço | Porta Interna | Porta Host |
|---------|---------------|------------|
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| Web | 8000 | 8000 |

## 🧹 Limpeza

### Parar Serviços (Mantém Volumes)
```bash
./scripts/stop.sh
# ou
docker compose down
```

### Limpeza Completa (Remove Tudo)
```bash
./scripts/clean.sh
# ou
docker compose down -v
docker rmi desafio3-web
```

### Funcionalidades Esperadas

- [x] Aplicação com 3+ serviços interdependentes
- [x] Configuração de variáveis de ambiente
- [x] Uso de volumes para persistência
- [x] Rede interna isolada
- [x] Health checks para todos os serviços
- [x] Scripts de automação (start, test, populate, etc.)
- [x] Documentação completa com arquitetura

## 📚 Conceitos Demonstrados

1. **Docker Compose**: Orquestração de múltiplos containers
2. **Service Dependencies**: Controle de ordem de inicialização
3. **Health Checks**: Monitoramento de disponibilidade
4. **Networking**: Comunicação entre containers via DNS
5. **Volumes**: Persistência de dados
6. **Environment Variables**: Configuração via compose
7. **API Gateway Pattern**: Ponto único de entrada
8. **Cache-Aside Pattern**: Estratégia de cache
9. **Clean Architecture**: Separação de responsabilidades
10. **Microservices**: Arquitetura distribuída
## 👤 Autor

**Nome**: Gabriel Melo Cavalcanti de Albuquerque  
**Curso**: Fundamentos de Computação Paralela e Distribuída  
**Ano**: 2025

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.