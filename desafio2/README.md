# Desafio 2 — Volumes e Persistência

## Descrição da Solução

Implementação de um sistema de gerenciamento de tarefas com PostgreSQL que demonstra **persistência de dados usando volumes Docker**. O projeto inclui uma API REST Flask para manipular dados e um container separado que comprova a persistência lendo dados mesmo após a recriação dos containers.

## Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                    Rede Docker Bridge                         │
│                   (desafio2-network)                          │
│                                                               │
│  ┌────────────────┐    ┌─────────────────┐   ┌────────────┐ │
│  │  Container App │    │   PostgreSQL    │   │  Container │ │
│  │                │    │                 │   │   Reader   │ │
│  │  Flask API     │───▶│  tasks_db       │◄──│            │ │
│  │  (Port 5000)   │    │  (Port 5432)    │   │  Python    │ │
│  │                │    │                 │   │  Script    │ │
│  │  - CRUD Tasks  │    │  ┌───────────┐  │   │            │ │
│  │  - REST API    │    │  │  Tabelas  │  │   │ - Lê dados │ │
│  │  - Logs        │    │  │  - tasks  │  │   │ - Stats    │ │
│  └────────────────┘    │  │  - logs   │  │   │ - Logs     │ │
│         │              │  └─────┬─────┘  │   └────────────┘ │
│         │              │        │        │                   │
│         │              │        ▼        │                   │
│         │              │  ┌───────────┐  │                   │
│         │              │  │  VOLUME   │  │                   │
│         └──────────────┼──│ Persistente│──┼───────────────── │
│                        │  │  (Docker) │  │                   │
│                        │  └───────────┘  │                   │
└────────────────────────┴─────────────────┴───────────────────┘
                                 │
                                 ▼
                         Host: /var/lib/docker/volumes/
                               desafio2_postgres_data
```

### Componentes

#### 1. **PostgreSQL Container** (`postgres:16-alpine`)
- **Função**: Banco de dados relacional
- **Porta**: 5432
- **Volume**: `desafio2_postgres_data` → `/var/lib/postgresql/data`
- **Características**:
  - Dados persistem no volume Docker
  - Health check integrado
  - Configurações via variáveis de ambiente
  - Imagem Alpine (menor tamanho)

#### 2. **Aplicação Flask** (`app/`)
- **Linguagem**: Python 3.11
- **Framework**: Flask
- **Porta**: 5000
- **Funcionalidades**:
  - **CRUD completo de tarefas**
    - `GET /tasks` - Lista todas as tarefas
    - `POST /tasks` - Cria nova tarefa
    - `GET /tasks/<id>` - Obtém tarefa por ID
    - `PUT /tasks/<id>` - Atualiza tarefa
    - `DELETE /tasks/<id>` - Remove tarefa
  - **Endpoints auxiliares**
    - `GET /` - Info da API
    - `GET /health` - Health check
    - `GET /stats` - Estatísticas do banco
    - `GET /logs` - Logs de operações
  - **Sistema de logs**: Registra todas as operações no banco
  - **Health check**: Verifica conexão com PostgreSQL

#### 3. **Container Leitor** (`reader/`)
- **Função**: Demonstra persistência lendo dados
- **Características**:
  - Executa sob demanda (profile: tools)
  - Lê dados diretamente do PostgreSQL
  - Exibe estatísticas e logs
  - Prova que dados persistem

### Banco de Dados

#### Tabela: `tasks`
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: `operation_logs`
```sql
CREATE TABLE operation_logs (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(50) NOT NULL,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Decisões Técnicas

### 1. **PostgreSQL vs SQLite**
- **Escolha**: PostgreSQL
- **Motivo**: 
  - Mais próximo de ambiente real de produção
  - Melhor para demonstrar volumes Docker
  - Suporte a múltiplas conexões simultâneas
  - Health checks nativos

### 2. **Volume Named vs Bind Mount**
- **Escolha**: Named Volume
- **Motivo**:
  - Gerenciado pelo Docker (mais seguro)
  - Portável entre sistemas
  - Melhor performance
  - Backup facilitado

### 3. **Container Leitor Separado**
- **Escolha**: Container independente com profile
- **Motivo**:
  - Demonstra isolamento de containers
  - Prova que dados estão no volume (não no container)
  - Execução sob demanda (não fica rodando)
  - Simula cenário real de múltiplos serviços

### 4. **API REST Completa**
- **Escolha**: CRUD completo com logs
- **Motivo**:
  - Demonstra uso prático
  - Facilita testes
  - Registra histórico de operações
  - Permite verificar persistência de forma clara

### 5. **Health Checks em Cascata**
- **Escolha**: depends_on com service_healthy
- **Motivo**:
  - App só inicia quando PostgreSQL está pronto
  - Evita erros de conexão
  - Ordem de inicialização garantida

## Estrutura do Projeto

```
desafio2/
├── README.md                      # Este arquivo
├── docker-compose.yml             # Orquestração dos serviços
├── .gitignore                     # Arquivos ignorados
│
├── app/                          # Container da aplicação
│   ├── Dockerfile                # Imagem Flask + psycopg2
│   ├── app.py                    # API REST completa
│   └── requirements.txt          # Flask, psycopg2-binary
│
├── reader/                       # Container leitor
│   ├── Dockerfile                # Imagem Python + psycopg2
│   ├── reader.py                 # Script de leitura
│   └── requirements.txt          # psycopg2-binary
│
└── scripts/                      # Scripts de automação
    ├── start.sh                  # Inicia o ambiente
    ├── stop.sh                   # Para containers (mantém volume)
    ├── logs.sh                   # Visualiza logs
    ├── test.sh                   # Testa API
    ├── populate.sh               # Popula banco com exemplos
    ├── read_data.sh              # Executa leitor
    ├── demo_persistence.sh       # Demonstra persistência
    └── clean.sh                  # Limpeza completa
```

## Instruções de Execução

### Pré-requisitos

- Docker instalado (versão 20.10+)
- Docker Compose instalado (versão 1.29+)
- Portas 5000 e 5432 disponíveis
- `curl` instalado para testes

### Método 1: Usando Scripts (Recomendado)

```bash
# 1. Navegar até o diretório
cd desafio2

# 2. Iniciar ambiente
./scripts/start.sh

# 3. Popular com dados de exemplo
./scripts/populate.sh

# 4. Testar API
./scripts/test.sh

# 5. Demonstrar persistência
./scripts/demo_persistence.sh

# 6. Ler dados com container separado
./scripts/read_data.sh
```

### Método 2: Comandos Docker Compose

```bash
# Iniciar serviços
docker compose up -d

# Ver logs
docker compose logs -f

# Executar leitor
docker compose run --rm reader

# Parar (mantém volumes)
docker compose down

# Parar e remover tudo
docker compose down -v
```

## Demonstração de Persistência

### Cenário de Teste Completo

#### **Etapa 1: Criar dados iniciais**

```bash
# Popular banco com dados
./scripts/populate.sh
```

#### **Etapa 2: Verificar dados**

```bash
# Listar tarefas
curl http://localhost:5000/tasks | python3 -m json.tool
```

#### **Etapa 3: Remover container da aplicação**

```bash
# Parar e remover container
docker stop desafio2-app
docker rm desafio2-app

# Verificar que foi removido
docker ps -a | grep desafio2-app  # Não deve retornar nada
```

#### **Etapa 4: Recriar container**

```bash
# Recriar container
docker compose up -d app

# Aguardar ficar healthy
docker ps
```

#### **Etapa 5: Verificar que dados persistiram**

```bash
# Verificar estatísticas
curl http://localhost:5000/stats | python3 -m json.tool
```

#### **Etapa 6: Ler com container separado**

```bash
# Executar leitor
./scripts/read_data.sh
```

**Resultado esperado:**
```
======================================================================
📊 LEITOR DE DADOS PERSISTIDOS - DESAFIO 2
======================================================================

📈 ESTATÍSTICAS GERAIS
----------------------------------------------------------------------
  Total de tarefas: 5
  Tarefas por status:
    • completed: 3
    • in_progress: 1
    • pending: 1
  Total de operações registradas: 6
  Primeira tarefa: 2025-11-19 01:30:00.123456
  Última tarefa: 2025-11-19 01:30:05.789012

📝 TAREFAS CADASTRADAS
----------------------------------------------------------------------
  Total: 5 tarefa(s)

  [1] ID: 1
      Título: Estudar Docker Volumes
      Descrição: Aprender sobre persistência de dados em containers
      Status: completed
      Criada em: 2025-11-19 01:30:00.123456

  [2] ID: 2
      Título: Implementar API REST
      ...

📋 LOGS DE OPERAÇÕES (últimos 20)
----------------------------------------------------------------------
  Total de operações: 6

  [1] CREATE - Tarefa criada: Estudar Docker Volumes
      2025-11-19 01:30:00.123456

  [2] CREATE - Tarefa criada: Implementar API REST
      ...

======================================================================
✅ Demonstração de persistência de dados concluída!
   Os dados acima foram lidos diretamente do volume Docker persistido.
======================================================================
```

### Script Automatizado

```bash
# Demonstração completa automática
./scripts/demo_persistence.sh
```

Este script:
1. ✅ Adiciona dados ao banco
2. ✅ Para e remove o container da aplicação
3. ✅ Recria o container
4. ✅ Verifica que dados ainda existem
5. ✅ Exibe logs comprovando persistência

## Testes da API

### Criar Tarefa

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Minha Tarefa",
    "description": "Descrição detalhada",
    "status": "pending"
  }'
```

### Listar Tarefas

```bash
curl http://localhost:5000/tasks
```

### Atualizar Tarefa

```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

### Deletar Tarefa

```bash
curl -X DELETE http://localhost:5000/tasks/1
```

### Obter Estatísticas

```bash
curl http://localhost:5000/stats
```

### Ver Logs de Operações

```bash
curl http://localhost:5000/logs?limit=10
```

## Observações Importantes

- Volume persiste dados mesmo após `docker compose down`
- Use `docker compose down -v` para remover volumes
- PostgreSQL inicia em ~5-10 segundos
- Health checks garantem ordem de inicialização
- Backup do volume recomendado antes de limpar
- Container leitor não fica rodando (executa e sai)

## 👤 Autor

Gabriel Melo Cavalcanti de Albuquerque  
Fundamentos de Computação Paralela e Distribuída - 2025

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.
