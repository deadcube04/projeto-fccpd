# 🌐 Desafio 5: API Gateway com Microsserviços

## 📋 Descrição

Implementação de uma arquitetura de microsserviços com **API Gateway** como ponto de entrada centralizado. O Gateway orquestra chamadas para múltiplos microsserviços independentes, fornecendo uma interface unificada para os clientes.

## 🎯 Objetivos

- ✅ Implementar um **API Gateway** que centraliza o acesso aos microsserviços
- ✅ Criar dois microsserviços independentes (Users e Orders)
- ✅ Gateway deve proxy requests para os microsserviços backend
- ✅ Implementar **endpoints de orquestração** que combinam dados de múltiplos serviços
- ✅ Garantir independência e resiliência dos microsserviços
- ✅ Implementar comunicação via HTTP/REST

## 🏗️ Arquitetura

```
┌─────────────────┐
│     Cliente     │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────────────────────┐
│       API Gateway :5000          │
│  ┌───────────────────────────┐  │
│  │   Proxy Endpoints         │  │
│  │   • /users/*              │  │
│  │   • /orders/*             │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │   Orchestration Layer     │  │
│  │   • GET /users/:id/orders │  │
│  │   • GET /orders/:id/detail│  │
│  └───────────────────────────┘  │
└────────┬─────────────┬──────────┘
         │             │
    HTTP │        HTTP │
         ▼             ▼
┌─────────────┐ ┌─────────────┐
│Users Service│ │Orders Service│
│   :5001     │ │   :5002      │
│             │ │              │
│ • CRUD      │ │ • CRUD       │
│ • In-Memory │ │ • In-Memory  │
│ • 5 Users   │ │ • 6 Orders   │
└─────────────┘ └──────────────┘
```

## 🔧 Tecnologias Utilizadas

- **Python 3.11 (alpine)**: Runtime leve e eficiente
- **Flask**: Framework web minimalista para APIs REST
- **Docker**: Containerização dos serviços
- **Docker Compose**: Orquestração de containers
- **HTTP/REST**: Protocolo de comunicação entre serviços

## 📦 Componentes

### 1. API Gateway (Port 5000)

**Responsabilidades:**
- **Proxy de requisições**: Encaminha requests para os microsserviços apropriados
- **Orquestração**: Combina dados de múltiplos serviços em um único response
- **Ponto de entrada único**: Clientes só conhecem o Gateway
- **Roteamento inteligente**: Direciona tráfego baseado no path da URL

**Endpoints Proxy:**
- `GET /users` → Users Service
- `GET /users/:id` → Users Service
- `POST /users` → Users Service
- `PUT /users/:id` → Users Service
- `DELETE /users/:id` → Users Service
- `GET /orders` → Orders Service
- `GET /orders/:id` → Orders Service
- `POST /orders` → Orders Service
- `PUT /orders/:id/status` → Orders Service
- `GET /orders/stats` → Orders Service

**Endpoints de Orquestração:**
- `GET /users/:id/orders`: Retorna dados do usuário + todos os seus pedidos
  - Combina: `GET /users/:id` + `GET /orders?user_id=:id`
  
- `GET /orders/:id/details`: Retorna dados do pedido + dados completos do usuário
  - Combina: `GET /orders/:id` + `GET /users/:user_id`

### 2. Users Service (Port 5001)

**Responsabilidades:**
- Gerenciar dados de usuários
- CRUD completo de usuários
- Armazenamento em memória (lista Python)

**Endpoints:**
- `GET /users`: Lista todos usuários
- `GET /users/:id`: Retorna um usuário específico
- `POST /users`: Cria novo usuário
- `PUT /users/:id`: Atualiza usuário
- `DELETE /users/:id`: Remove usuário

**Dados Iniciais (5 usuários):**
```json
[
  {"id": 1, "name": "Alice Silva", "email": "alice@email.com"},
  {"id": 2, "name": "Bob Santos", "email": "bob@email.com"},
  {"id": 3, "name": "Carol Oliveira", "email": "carol@email.com"},
  {"id": 4, "name": "David Costa", "email": "david@email.com"},
  {"id": 5, "name": "Eva Lima", "email": "eva@email.com"}
]
```

### 3. Orders Service (Port 5002)

**Responsabilidades:**
- Gerenciar pedidos de usuários
- CRUD de pedidos
- Associar pedidos a usuários via `user_id`
- Calcular estatísticas de pedidos

**Endpoints:**
- `GET /orders`: Lista todos pedidos (filtro por `user_id` opcional)
- `GET /orders/:id`: Retorna um pedido específico
- `POST /orders`: Cria novo pedido
- `PUT /orders/:id/status`: Atualiza status do pedido
- `GET /orders/stats`: Estatísticas agregadas

**Dados Iniciais (6 pedidos):**
```json
[
  {"id": 1, "user_id": 1, "product": "Notebook", "amount": 3500.00, "status": "completed"},
  {"id": 2, "user_id": 2, "product": "Mouse", "amount": 50.00, "status": "pending"},
  {"id": 3, "user_id": 1, "product": "Teclado", "amount": 200.00, "status": "completed"},
  {"id": 4, "user_id": 3, "product": "Monitor", "amount": 1200.00, "status": "shipped"},
  {"id": 5, "user_id": 2, "product": "Webcam", "amount": 300.00, "status": "cancelled"},
  {"id": 6, "user_id": 4, "product": "Headset", "amount": 150.00, "status": "pending"}
]
```

## 🚀 Como Executar

### Pré-requisitos
- Docker
- Docker Compose

### Inicialização

```bash
cd desafio5/scripts
./start.sh
```

O script `start.sh`:
1. Para e remove containers existentes
2. Realiza build das imagens
3. Inicia os containers em background
4. Aguarda health checks dos serviços
5. Exibe status dos containers

### Verificar Logs

```bash
./logs.sh          # Todos os serviços
./logs.sh gateway  # Apenas gateway
./logs.sh users    # Apenas users-service
./logs.sh orders   # Apenas orders-service
```

### Testes Automatizados

**Teste de endpoints básicos:**
```bash
./test.sh
```

**Teste de orquestração:**
```bash
./test_orchestration.sh
```

**Demonstração completa:**
```bash
./demo.sh
```

### Parar Serviços

```bash
./stop.sh
```

### Limpeza Completa

```bash
./clean.sh  # Remove containers, imagens, networks, volumes
```

## 📊 Exemplos de Uso

### 1. Listar todos os usuários (via Gateway)

```bash
curl http://localhost:5000/users
```

**Response:**
```json
{
  "users": [
    {"id": 1, "name": "Alice Silva", "email": "alice@email.com"},
    {"id": 2, "name": "Bob Santos", "email": "bob@email.com"},
    ...
  ]
}
```

### 2. Criar novo pedido (via Gateway)

```bash
curl -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "product": "SSD 1TB", "amount": 500.00}'
```

**Response:**
```json
{
  "message": "Order created successfully",
  "order": {
    "id": 7,
    "user_id": 1,
    "product": "SSD 1TB",
    "amount": 500.0,
    "status": "pending"
  }
}
```

### 3. Orquestração: Usuário + Seus Pedidos

```bash
curl http://localhost:5000/users/1/orders
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "Alice Silva",
    "email": "alice@email.com"
  },
  "orders": [
    {"id": 1, "product": "Notebook", "amount": 3500.0, "status": "completed"},
    {"id": 3, "product": "Teclado", "amount": 200.0, "status": "completed"}
  ],
  "total_orders": 2,
  "total_amount": 3700.0
}
```

### 4. Orquestração: Pedido + Dados do Usuário

```bash
curl http://localhost:5000/orders/1/details
```

**Response:**
```json
{
  "order": {
    "id": 1,
    "user_id": 1,
    "product": "Notebook",
    "amount": 3500.0,
    "status": "completed"
  },
  "user": {
    "id": 1,
    "name": "Alice Silva",
    "email": "alice@email.com"
  }
}
```

### 5. Estatísticas de Pedidos

```bash
curl http://localhost:5000/orders/stats
```

**Response:**
```json
{
  "total_orders": 6,
  "total_amount": 5400.0,
  "average_amount": 900.0,
  "by_status": {
    "pending": 2,
    "completed": 2,
    "shipped": 1,
    "cancelled": 1
  }
}
```

## 🧪 Cenários de Demonstração

O script `demo.sh` executa 7 cenários completos:

1. **Usuários existentes**: Lista todos usuários iniciais
2. **Pedidos existentes**: Lista todos pedidos iniciais
3. **Criar novo usuário**: Adiciona "Fernando Ribeiro"
4. **Criar pedido**: Novo pedido para o usuário criado
5. **Orquestração usuário+pedidos**: Combina dados de ambos os serviços
6. **Atualizar status**: Muda pedido de pending → completed
7. **Estatísticas**: Visualiza métricas agregadas

## 🎨 Decisões Técnicas

### 1. **API Gateway Pattern**

**Por quê?**
- ✅ **Ponto de entrada único**: Clientes não precisam conhecer múltiplos endpoints
- ✅ **Desacoplamento**: Microsserviços podem mudar sem afetar clientes
- ✅ **Orquestração centralizada**: Lógica de combinação de dados em um só lugar
- ✅ **Simplificação de clientes**: Um único host/port para conectar

**Trade-offs:**
- ⚠️ Gateway como single point of failure (poderia ter múltiplas instâncias com load balancer)
- ⚠️ Latência adicional (1 hop extra)

### 2. **Comunicação HTTP Síncrona**

**Por quê?**
- ✅ **Simplicidade**: HTTP é universal e fácil de debugar
- ✅ **Request-response**: Natural para operações CRUD
- ✅ **Stateless**: Cada request é independente

**Alternativas consideradas:**
- Message queues (RabbitMQ, Kafka): Overkill para este cenário simples
- gRPC: Melhor performance, mas maior complexidade

### 3. **Storage In-Memory**

**Por quê?**
- ✅ **Simplicidade**: Foco no padrão Gateway, não em persistência
- ✅ **Performance**: Acesso instantâneo aos dados
- ✅ **Sem dependências externas**: Não precisa de banco de dados

**Trade-offs:**
- ⚠️ Dados perdidos ao reiniciar (OK para demo/testes)
- ⚠️ Não escalável horizontalmente (necessitaria banco compartilhado)

### 4. **Health Checks no Docker Compose**

**Por quê?**
- ✅ **Confiabilidade**: Gateway só inicia quando serviços estão prontos
- ✅ **Restart automático**: Docker detecta falhas e reinicia
- ✅ **Observabilidade**: `docker ps` mostra status de saúde

### 5. **Tratamento de Erros Robusto**

**Implementações:**
- ✅ **404**: Quando recurso não encontrado
- ✅ **400**: Validação de entrada
- ✅ **500**: Erro interno do servidor
- ✅ **503**: Serviço backend indisponível (no Gateway)
- ✅ **Timeout**: Gateway desiste após 5 segundos

### 6. **Orquestração vs Choreography**

**Escolhido: Orquestração (Gateway coordena)**

**Por quê?**
- ✅ **Controle centralizado**: Gateway decide quando chamar cada serviço
- ✅ **Transações complexas**: Fácil implementar fluxos multi-step
- ✅ **Debugging**: Logs centralizados no Gateway

**Choreography** (cada serviço reage a eventos):
- Seria melhor para sistemas event-driven
- Maior desacoplamento, mas maior complexidade

## 📐 Boas Práticas Aplicadas

### Código Limpo
- ✅ **Nomes descritivos**: `proxy_to_users_service()`, `get_user_with_orders()`
- ✅ **Funções pequenas**: Cada função tem uma responsabilidade
- ✅ **Constantes**: `USERS_SERVICE_URL`, `ORDERS_SERVICE_URL`
- ✅ **Comentários**: Explicações em pontos críticos
- ✅ **Type hints**: `-> tuple[dict, int]`

### Arquitetura
- ✅ **Separation of Concerns**: Cada serviço tem responsabilidade única
- ✅ **DRY**: Função `proxy_request()` reutilizada para proxy
- ✅ **Fail-fast**: Validações no início das funções
- ✅ **Graceful degradation**: Gateway retorna 503 se backend falha

### Docker
- ✅ **Imagens leves**: Alpine (5MB base)
- ✅ **Multi-stage builds**: Não usado aqui (apps simples), mas seria ideal para apps maiores
- ✅ **Health checks**: Garantem disponibilidade antes de aceitar tráfego
- ✅ **Networks**: Isolamento de rede para comunicação interna

### Testes
- ✅ **Scripts automatizados**: `test.sh`, `test_orchestration.sh`
- ✅ **Dados de seed**: Usuários e pedidos pré-populados
- ✅ **Demonstração end-to-end**: `demo.sh` cobre todos cenários

## 📈 Possíveis Melhorias

### 1. **Autenticação e Autorização**
- JWT tokens no Gateway
- Validação de permissões por endpoint

### 2. **Rate Limiting**
- Limitar requests por IP/usuário
- Prevenir abusos e DDoS

### 3. **Caching**
- Redis no Gateway para cache de responses
- Reduzir latência e carga nos backends

### 4. **Service Discovery**
- Consul/Eureka para descobrir serviços dinamicamente
- Gateway não precisaria conhecer IPs fixos

### 5. **Circuit Breaker**
- Padrão Hystrix/Resilience4j
- Gateway para de chamar serviço que está falhando constantemente

### 6. **Logging Centralizado**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Agregação de logs de todos os serviços

### 7. **Observabilidade**
- Prometheus + Grafana para métricas
- Jaeger/Zipkin para distributed tracing

### 8. **Database Real**
- PostgreSQL para Users
- MongoDB para Orders
- Persistência e escalabilidade

### 9. **Containerização Multi-stage**
- Separar build e runtime
- Imagens ainda menores

### 10. **API Versioning**
- `/v1/users`, `/v2/users`
- Suporte a múltiplas versões da API

## ✅ Critérios de Avaliação (25 pontos)

- [x] **Gateway centraliza acesso** (8 pts)
  - Gateway expõe endpoints `/users` e `/orders`
  - Proxy de todas requisições para os microsserviços corretos
  - Orquestração de múltiplos serviços em endpoints compostos
  
- [x] **Microsserviços independentes** (8 pts)
  - Users Service completamente independente
  - Orders Service completamente independente
  - Cada serviço tem seu próprio container e porta
  - Podem ser iniciados/parados individualmente
  
- [x] **Comunicação entre serviços** (5 pts)
  - HTTP/REST entre Gateway e microsserviços
  - Tratamento de erros de comunicação
  - Timeout configurado (5 segundos)
  
- [x] **Documentação completa** (4 pts)
  - README.md detalhado com arquitetura
  - Diagramas de componentes
  - Exemplos de uso com curl
  - Decisões técnicas documentadas
  - Scripts de automação comentados

## 📝 Estrutura de Arquivos

```
desafio5/
├── README.md                       # Este arquivo
├── docker-compose.yml              # Orquestração dos 3 serviços
├── gateway/
│   ├── app.py                      # API Gateway (proxy + orquestração)
│   ├── Dockerfile                  # Container do Gateway
│   └── requirements.txt            # Dependências (Flask, requests)
├── users-service/
│   ├── app.py                      # Microsserviço de usuários
│   ├── Dockerfile                  # Container do Users Service
│   └── requirements.txt            # Dependências (Flask)
├── orders-service/
│   ├── app.py                      # Microsserviço de pedidos
│   ├── Dockerfile                  # Container do Orders Service
│   └── requirements.txt            # Dependências (Flask)
└── scripts/
    ├── start.sh                    # Inicialização com health checks
    ├── stop.sh                     # Parar containers
    ├── logs.sh                     # Visualizar logs
    ├── test.sh                     # Testes de endpoints
    ├── test_orchestration.sh       # Testes de orquestração
    ├── demo.sh                     # Demonstração completa
    └── clean.sh                    # Limpeza completa
```

## 🔗 Referências

- [Microservices Pattern: API Gateway](https://microservices.io/patterns/apigateway.html)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Desenvolvido para o curso de Sistemas Distribuídos** | **Desafio 5/5** ✅
