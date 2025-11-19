# Desafio 4 — Microsserviços Independentes

Este projeto demonstra a comunicação entre dois microsserviços independentes via HTTP, implementando uma arquitetura de microsserviços com separação clara de responsabilidades.

## Descrição

Sistema composto por dois microsserviços que se comunicam via HTTP REST:
- **Service A (Users Service)**: API REST que gerencia dados de usuários
- **Service B (Profile Service)**: API REST que consome Service A e enriquece os dados com análises

## Arquitetura

```
┌────────────────────────────────────────────────────────────┐
│               Docker Compose Network                        │
│              (desafio4-network - bridge)                    │
│                                                             │
│   ┌─────────────────────┐       ┌────────────────────────┐│
│   │   Service A         │       │   Service B            ││
│   │  (Users Service)    │◄──────│ (Profile Service)      ││
│   │                     │  HTTP │                        ││
│   │  Port: 5000         │       │  Port: 5001            ││
│   │  Hostname: service-a│       │  Hostname: service-b   ││
│   │                     │       │                        ││
│   │  Endpoints:         │       │  Endpoints:            ││
│   │  • GET /users       │       │  • GET /profiles       ││
│   │  • GET /users/<id>  │       │  • GET /profiles/<id>  ││
│   │  • POST /users      │       │  • GET /profiles/<id>/ ││
│   │  • PUT /users/<id>  │       │         summary        ││
│   │  • GET /health      │       │  • GET /health         ││
│   │  • GET /stats       │       │  • GET /stats          ││
│   └─────────────────────┘       └────────────────────────┘│
│            │                              │                │
│            │                              │                │
│            └──────────────┬───────────────┘                │
│                           │                                │
└───────────────────────────┼────────────────────────────────┘
                            │
                            │ Portas expostas
                            ▼
                    ┌───────────────┐
                    │   Cliente     │
                    │ localhost:5000│
                    │ localhost:5001│
                    └───────────────┘
```

### Decisões Técnicas

#### 1. **Arquitetura de Microsserviços**
- **Separação de responsabilidades**: Cada serviço tem domínio próprio
  - Service A: Fonte de verdade para dados de usuários
  - Service B: Agregação e enriquecimento de dados
- **Independência**: Cada serviço pode ser desenvolvido, testado e deployado separadamente
- **Comunicação síncrona**: HTTP REST para comunicação direta

#### 2. **Service A - Users Service**
**Responsabilidades:**
- CRUD completo de usuários
- Persistência em memória (simula banco de dados)
- Validação de dados
- Endpoints para consultas com filtros

**Dados gerenciados:**
```python
{
    'id': int,
    'username': str,
    'email': str,
    'full_name': str,
    'role': str,
    'department': str,
    'active': bool,
    'registration_date': ISO datetime,
    'last_login': ISO datetime,
    'projects': list[str],
    'skills': list[str],
    'location': str
}
```

#### 3. **Service B - Profile Service**
**Responsabilidades:**
- Consumir dados do Service A via HTTP
- Enriquecer dados com análises calculadas
- Gerar perfis combinados
- Criar resumos executivos

**Análises adicionadas:**
- **Experience Level**: Calculado baseado no tempo de registro
  - Junior (< 6 meses)
  - Mid-Level (6-12 meses)
  - Senior (1-2 anos)
  - Expert (> 2 anos)

- **Activity Status**: Baseado no último login
  - Online (< 1 hora)
  - Recently Active (< 24 horas)
  - Active This Week (< 7 dias)
  - Inactive (> 7 dias)

- **Tenure**: Tempo na empresa (anos e meses)
- **Métricas**: Contagem de projetos e skills

#### 4. **Comunicação HTTP**
```python
# Service B consumindo Service A
class UsersServiceClient:
    def get_all_users(self, filters):
        response = requests.get(f"{SERVICE_A_URL}/users", params=filters)
        return response.json()
    
    def get_user_by_id(self, user_id):
        response = requests.get(f"{SERVICE_A_URL}/users/{user_id}")
        return response.json()
```

**Características:**
- **Session reusável**: Mantém conexão HTTP para melhor performance
- **Timeout configurado**: Evita bloqueios indefinidos (5 segundos)
- **Error handling**: Tratamento de erros de rede e HTTP
- **Retry logic**: Pode ser implementado para maior resiliência

#### 5. **Isolamento via Docker**
- Cada serviço tem seu próprio Dockerfile
- Imagens baseadas em Alpine Linux (menor footprint)
- Health checks independentes
- Logs estruturados separados

## Funcionamento Detalhado

### Fluxo de Comunicação

#### Exemplo: Buscar Perfil Enriquecido

```
1. Cliente HTTP
   │
   │ GET /profiles/1
   ▼
2. Service B (Profile Service)
   │
   │ Recebe requisição
   │
   │ HTTP GET http://service-a:5000/users/1
   ▼
3. Service A (Users Service)
   │
   │ Consulta dados do usuário
   │
   │ Retorna dados básicos:
   │ {id: 1, username: "alice_dev", ...}
   ▼
4. Service B
   │
   │ Recebe dados do Service A
   │
   │ Enriquece com análises:
   │ - Calcula experience_level
   │ - Calcula activity_status
   │ - Calcula tenure
   │ - Calcula métricas
   │
   │ Retorna perfil enriquecido
   ▼
5. Cliente HTTP
   │
   │ Recebe resposta:
   │ {
   │   user_id: 1,
   │   username: "alice_dev",
   │   professional: {...},
   │   activity: {...},
   │   metrics: {...}
   │ }
```

### Health Checks e Dependências

```yaml
# docker-compose.yml
service-b:
  depends_on:
    service-a:
      condition: service_healthy
```

- Service B só inicia após Service A estar healthy
- Health check do Service B verifica disponibilidade do Service A
- Retorna status "degraded" se Service A estiver indisponível

## Como Executar

### Pré-requisitos
- Docker 20.10+
- Docker Compose v2.0+
- Portas 5000 e 5001 disponíveis

### Passo 1: Iniciar os Serviços

```bash
cd desafio4
./scripts/start.sh
```

O script irá:
- Construir as imagens Docker
- Criar a rede bridge
- Iniciar Service A
- Aguardar Service A ficar healthy
- Iniciar Service B
- Verificar saúde de ambos

### Passo 2: Testar Comunicação

```bash
./scripts/test_communication.sh
```

Demonstra:
- Service A retornando dados brutos
- Service B consumindo Service A via HTTP
- Comparação entre dados brutos e enriquecidos
- Resolução DNS interna
- Health checks de dependências

### Passo 3: Demonstração Completa

```bash
./scripts/demo.sh
```

Apresenta casos de uso:
- Listar usuários ativos
- Comparar dados entre serviços
- Gerar resumos executivos
- Aplicar filtros
- Visualizar estatísticas

### Passo 4: Testar Todos os Endpoints

```bash
./scripts/test.sh
```

Testa sistematicamente todos os endpoints de ambos os serviços.

## Endpoints

### Service A - Users Service (porta 5000)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações do serviço |
| GET | `/health` | Health check |
| GET | `/stats` | Estatísticas do serviço |
| GET | `/users` | Lista todos os usuários |
| GET | `/users?active=true` | Filtra usuários ativos |
| GET | `/users?department=Engineering` | Filtra por departamento |
| GET | `/users/<id>` | Busca usuário específico |
| POST | `/users` | Cria novo usuário |
| PUT | `/users/<id>` | Atualiza usuário |
| DELETE | `/users/<id>` | Desativa usuário (soft delete) |

### Service B - Profile Service (porta 5001)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações do serviço |
| GET | `/health` | Health check + verificação Service A |
| GET | `/stats` | Estatísticas + comunicação com Service A |
| GET | `/profiles` | Lista perfis enriquecidos |
| GET | `/profiles?department=Product` | Filtra perfis por departamento |
| GET | `/profiles/<id>` | Busca perfil enriquecido |
| GET | `/profiles/<id>/summary` | Resumo executivo do perfil |

## Exemplos de Uso

### Exemplo 1: Buscar Usuário (Service A)

```bash
curl http://localhost:5000/users/1
```

### Exemplo 2: Buscar Perfil Enriquecido (Service B)

```bash
curl http://localhost:5001/profiles/1
```

### Exemplo 3: Resumo Executivo (Service B)

```bash
curl http://localhost:5001/profiles/1/summary
```

### Exemplo 4: Criar Novo Usuário (Service A)

```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "grace_frontend",
    "email": "grace@example.com",
    "full_name": "Grace Frontend",
    "role": "Frontend Developer",
    "department": "Engineering",
    "skills": ["React", "TypeScript", "CSS"],
    "location": "Remote"
  }'
```

## Configuração

### Service A (Users Service)

**Configuração:**
- Porta: 5000
- Hostname: service-a
- Dados: Em memória (6 usuários de exemplo pré-carregados)

**Health Check:**
```yaml
test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
interval: 30s
timeout: 10s
retries: 3
start_period: 5s
```

### Service B (Profile Service)

**Configuração:**
- Porta: 5001
- Hostname: service-b
- Service A URL: http://service-a:5000

**Health Check:**
```yaml
test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
interval: 30s
timeout: 10s
retries: 3
start_period: 10s
```

**Dependência:**
```yaml
depends_on:
  service-a:
    condition: service_healthy
```

## Monitoramento

### Métricas do Service A

```bash
curl http://localhost:5000/stats
```

```json
{
  "service": "Users Service",
  "uptime_seconds": 1234.56,
  "requests": {
    "total": 42,
    "users_created": 2,
    "users_updated": 5
  },
  "users": {
    "total": 8,
    "active": 7,
    "inactive": 1,
    "by_department": {
      "Engineering": 3,
      "Product": 2,
      "Analytics": 1,
      "Operations": 1,
      "General": 1
    }
  }
}
```

### Métricas do Service B

```bash
curl http://localhost:5001/stats
```

```json
{
  "service": "Profile Service",
  "uptime_seconds": 1234.56,
  "requests": {
    "total": 28,
    "profiles_generated": 15
  },
  "service_a_communication": {
    "total_calls": 15,
    "errors": 0,
    "error_rate_percent": 0.0,
    "url": "http://service-a:5000"
  }
}
```

## 🧹 Limpeza

### Parar Serviços

```bash
./scripts/stop.sh
# ou
docker compose down
```

### Limpeza Completa

```bash
./scripts/clean.sh
```

Remove:
- Containers
- Imagens
- Rede Docker
## Conceitos Demonstrados

1. **Arquitetura de Microsserviços**: Serviços independentes com responsabilidades distintas
2. **Comunicação HTTP/REST**: API REST para comunicação entre serviços
3. **Service Discovery**: DNS interno do Docker para resolução de nomes
4. **Isolamento**: Cada serviço em container separado
5. **Dependências**: Service B depende do Service A
6. **Health Checks**: Monitoramento de disponibilidade
7. **Error Handling**: Tratamento de falhas de comunicação
8. **Data Enrichment**: Service B agrega valor aos dados do Service A
9. **Clean Architecture**: Separação clara de responsabilidades
10. **API Design**: RESTful endpoints bem estruturados

## 👤 Autor

**Nome**: Gabriel Melo Cavalcanti de Albuquerque  
**Curso**: Fundamentos de Computação Paralela e Distribuída  
**Ano**: 2025

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.
