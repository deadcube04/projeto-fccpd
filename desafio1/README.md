# Desafio 1 — Containers em Rede

##  Descrição da Solução

Implementação de dois containers Docker que se comunicam através de uma rede customizada. O sistema consiste em um servidor web Flask que recebe requisições HTTP e um cliente que realiza requisições periódicas, demonstrando comunicação eficiente entre containers via rede Docker.

##  Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                  Rede Docker Bridge                      │
│                (desafio1-network)                        │
│                  172.20.0.0/16                           │
│                                                          │
│  ┌─────────────────────┐      ┌────────────────────┐   │
│  │   Container Server  │      │  Container Client  │   │
│  │                     │      │                    │   │
│  │  Flask App (8080)   │◄─────┤  HTTP Client       │   │
│  │                     │      │  (requests loop)   │   │
│  │  - Endpoints REST   │      │                    │   │
│  │  - Logging          │      │  - Requisições 5s  │   │
│  │  - Health Check     │      │  - Logs detalhados │   │
│  └──────────┬──────────┘      └────────────────────┘   │
│             │                                            │
└─────────────┼────────────────────────────────────────────┘
              │
              │ Port Mapping
              ▼
         Host:8080
```

### Componentes

#### 1. **Servidor Flask** (`server/`)
- **Linguagem**: Python 3.11
- **Framework**: Flask
- **Porta**: 8080
- **Funcionalidades**:
  - Endpoint principal (`/`) com informações da requisição
  - Health check (`/health`) para monitoramento
  - Estatísticas (`/stats`) com total de requisições
  - Logging detalhado de todas as requisições
  - Contador de requisições recebidas
  - Tratamento de erros 404

#### 2. **Cliente HTTP** (`client/`)
- **Linguagem**: Python 3.11
- **Biblioteca**: requests
- **Funcionalidades**:
  - Requisições HTTP GET periódicas (intervalo de 5 segundos)
  - Verificação de disponibilidade do servidor antes de iniciar
  - Logging detalhado de cada requisição
  - Estatísticas de sucesso/falha com taxa de sucesso
  - Tratamento robusto de erros (ConnectionError, Timeout, etc)
  - Consulta periódica das estatísticas do servidor

#### 3. **Rede Docker**
- **Nome**: `desafio1-network`
- **Driver**: bridge
- **Subnet**: 172.20.0.0/16
- **DNS**: Resolução automática de nomes entre containers
- **Isolamento**: Containers isolados da rede host padrão

## 🔧 Decisões Técnicas

### 1. **Escolha do Python Alpine**
- Imagens base `python:3.11-alpine` (~50MB vs ~900MB da imagem completa)
- Menor superfície de ataque de segurança
- Builds mais rápidos e menor consumo de recursos
- Instalação manual do `curl` para health checks

### 2. **Arquitetura Limpa**
- **Separação de responsabilidades**: Cada componente tem função bem definida
- **Classes bem definidas**: `HTTPClient` encapsula lógica do cliente
- **Logging estruturado**: Formato consistente com timestamps
- **Tratamento de erros em camadas**: Cada tipo de erro é tratado especificamente

### 3. **Health Checks Robustos**
- Implementados no Dockerfile E no docker-compose.yml
- Usa `curl -f` para validar resposta HTTP 200
- Cliente depende do servidor estar "healthy" antes de iniciar
- Intervalo de 10s, timeout de 5s, 5 retries, start_period de 5s

### 4. **Logging Detalhado**
- Formato: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Níveis apropriados (INFO para operações, ERROR para falhas)
- Output para stdout para integração com Docker logs
- Facilita debugging e auditoria

### 5. **Restart Policies**
- `unless-stopped` para ambos containers
- Garante alta disponibilidade em caso de falhas temporárias
- Não reinicia se parado manualmente

### 6. **Depends On com Service Healthy**
- Cliente só inicia quando servidor está healthy
- Evita erros de conexão no início
- Garante ordem de inicialização correta

### 7. **Variáveis de Ambiente**
- `PYTHONUNBUFFERED=1`: Output imediato dos logs (sem buffer)
- Facilita visualização de logs em tempo real

## 📁 Estrutura do Projeto

```
desafio1/
├── README.md                 # Este arquivo
├── docker-compose.yml        # Orquestração dos containers
├── .gitignore               # Arquivos ignorados pelo Git
│
├── server/                  # Container do servidor
│   ├── Dockerfile           # Imagem do servidor (Alpine + Flask)
│   ├── app.py              # Aplicação Flask com 3 endpoints
│   └── requirements.txt     # Flask==3.0.0, Werkzeug==3.0.1
│
├── client/                  # Container do cliente
│   ├── Dockerfile           # Imagem do cliente (Alpine + requests)
│   ├── client.py           # Cliente HTTP com classe HTTPClient
│   └── requirements.txt     # requests==2.31.0
│
└── scripts/                 # Scripts de automação bash
    ├── start.sh            # Inicia o ambiente completo
    ├── stop.sh             # Para os containers
    ├── logs.sh             # Visualiza logs em tempo real
    ├── test.sh             # Testa a comunicação
    └── clean.sh            # Limpeza completa do ambiente
```

## Instruções de Execução

### Pré-requisitos

- Docker instalado (versão 20.10 ou superior)
- Docker Compose instalado (versão 1.29 ou superior)
- Porta 8080 disponível no host

### Método 1: Usando Scripts Automatizados (Recomendado)

```bash
# 1. Navegar até o diretório do desafio
cd desafio1

# 2. Iniciar o ambiente (constrói imagens, cria rede, inicia containers)
./scripts/start.sh

# 3. Visualizar logs em tempo real (Ctrl+C para sair)
./scripts/logs.sh

# 4. Testar a comunicação (em outro terminal)
./scripts/test.sh

# 5. Parar o ambiente
./scripts/stop.sh

# 6. Limpar completamente (opcional - remove imagens e rede)
./scripts/clean.sh
```

### Método 2: Usando Docker Compose Diretamente

```bash
# 1. Navegar até o diretório do desafio
cd desafio1

# 2. Construir e iniciar containers
docker compose up --build -d

# 3. Ver logs
docker compose logs -f

# 4. Parar containers
docker compose down
```

## Testando a Comunicação

### 1. Testar Servidor Diretamente (do host)

```bash
# Endpoint principal - retorna informações da requisição
curl http://localhost:8080

# Health check - verifica saúde do servidor
curl http://localhost:8080/health

# Estatísticas - total de requisições
curl http://localhost:8080/stats
```

### 2. Verificar Logs do Servidor

```bash
docker logs -f desafio1-server
```

**Exemplo de saída:**
```
2025-11-19 00:59:48,123 - __main__ - INFO - ============================================================
2025-11-19 00:59:48,123 - __main__ - INFO - Iniciando servidor Flask na porta 8080
2025-11-19 00:59:48,123 - __main__ - INFO - Endpoints disponíveis:
2025-11-19 00:59:48,123 - __main__ - INFO -   - GET /         : Endpoint principal
2025-11-19 00:59:48,123 - __main__ - INFO -   - GET /health   : Health check
2025-11-19 00:59:48,123 - __main__ - INFO -   - GET /stats    : Estatísticas do servidor
2025-11-19 00:59:48,123 - __main__ - INFO - ============================================================
2025-11-19 00:59:53,561 - __main__ - INFO - Requisição #1 recebida de 172.20.0.3
2025-11-19 00:59:58,571 - __main__ - INFO - Requisição #2 recebida de 172.20.0.3
```

### 3. Verificar Logs do Cliente

```bash
docker logs -f desafio1-client
```

**Exemplo de saída:**
```
2025-11-19 00:59:45,456 - __main__ - INFO - ============================================================
2025-11-19 00:59:45,456 - __main__ - INFO - Cliente HTTP iniciado
2025-11-19 00:59:45,456 - __main__ - INFO - Servidor alvo: http://server:8080
2025-11-19 00:59:45,456 - __main__ - INFO - Intervalo entre requisições: 5 segundos
2025-11-19 00:59:45,456 - __main__ - INFO - ============================================================
2025-11-19 00:59:45,457 - __main__ - INFO - Aguardando servidor ficar disponível...
2025-11-19 00:59:48,123 - __main__ - INFO - ✓ Servidor disponível!
2025-11-19 00:59:48,124 - __main__ - INFO - 
--- Requisição #1 ---
2025-11-19 00:59:48,124 - __main__ - INFO - Enviando requisição para http://server:8080/
2025-11-19 00:59:48,234 - __main__ - INFO - ✓ Resposta recebida (Status: 200)
2025-11-19 00:59:48,234 - __main__ - INFO -   Mensagem: Servidor Flask em execução!
2025-11-19 00:59:48,234 - __main__ - INFO -   Timestamp: 2025-11-19T00:59:48.231234
2025-11-19 00:59:48,234 - __main__ - INFO -   Request #: 1
2025-11-19 00:59:48,235 - __main__ - INFO - 
Aguardando 5 segundos...
```

### 4. Verificar Status dos Containers

```bash
# Status geral
docker compose ps
```

## Monitoramento

### Ver Estatísticas de Recursos

```bash
# CPU e memória em tempo real
docker stats desafio1-server desafio1-client
```

### Verificar Logs com Filtros

```bash
# Últimas 50 linhas
docker compose logs --tail=50

# Logs desde uma data específica
docker compose logs --since "2025-11-19T00:00:00"

# Logs apenas do servidor
docker compose logs -f server

# Logs com timestamps
docker compose logs -f --timestamps
```

## 🎯 Demonstração da Comunicação

O sistema demonstra a comunicação entre containers através de:

1. **Resolução de DNS**: O cliente usa o nome `server` que é resolvido automaticamente para o IP `172.20.0.2`
2. **Requisições HTTP**: Cliente faz GET requests periódicas a cada 5 segundos
3. **Logs Sincronizados**: Ambos containers registram as interações com timestamps
4. **Health Checks**: Docker monitora automaticamente a saúde do servidor
5. **Estatísticas**: Cliente consulta estatísticas do servidor a cada 5 requisições
6. **Tratamento de Erros**: Cliente trata falhas de conexão e continua tentando

## 📝 Observações Importantes

- O servidor registra cada requisição com timestamp e IP do cliente
- O cliente aguarda até 30 tentativas (1 minuto) para o servidor ficar disponível
- A rede bridge permite comunicação direta entre containers via DNS
- Health checks garantem disponibilidade antes do cliente iniciar
- Logs estruturados facilitam debugging e auditoria
- Imagens Alpine reduzem tamanho e aumentam segurança
- Restart policy garante alta disponibilidade

## 👤 Autor

Gabriel Melo Cavalcanti de Albuquerque  
Fundamentos de Computação Paralela e Distribuída - 2025

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.
