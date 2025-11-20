# Fundamentos de Computação Paralela e Distribuída

## 📋 Sobre o Projeto

Repositório contendo as implementações dos desafios práticos da disciplina de Fundamentos de Computação Paralela e Distribuída. Cada desafio explora conceitos fundamentais de sistemas distribuídos, containerização, microsserviços e comunicação entre processos.

## 🎯 Desafios Implementados

### ✅ [Desafio 1 — Containers em Rede](./desafio1/)
**Objetivo**: Criar dois containers que se comunicam por uma rede Docker customizada.

**Tecnologias**: Docker, Python, Flask, Docker Compose

**Destaques**:
- Servidor web Flask na porta 8080
- Cliente HTTP com requisições periódicas
- Rede bridge customizada
- Health checks automatizados
- Logging estruturado

[📖 Ver documentação completa](./desafio1/README.md)

---

### ✅ [Desafio 2 — Volumes e Persistência](./desafio2/)
**Objetivo**: Demonstrar persistência de dados usando volumes Docker.

**Tecnologias**: Docker, Python, Flask, PostgreSQL, Docker Volumes

**Destaques**:
- API REST completa (CRUD de tarefas)
- PostgreSQL com volume persistente
- Container leitor separado
- Demonstração automatizada de persistência
- Sistema de logs de operações

[📖 Ver documentação completa](./desafio2/README.md)

---

### ✅ [Desafio 3 — Orquestração com Docker Compose](./desafio3/)
**Objetivo**: Orquestrar múltiplos serviços interdependentes usando Docker Compose.

**Tecnologias**: Docker Compose, Python, Flask, PostgreSQL, Redis

**Destaques**:
- API Gateway com 3 serviços integrados
- Sistema de cache distribuído com Redis
- Dependências e health checks avançados
- Cache-aside pattern implementado
- Estatísticas de performance em tempo real
- Scripts de demonstração automatizados

[📖 Ver documentação completa](./desafio3/README.md)

---

### ✅ [Desafio 4 — Microsserviços Independentes](./desafio4/)
**Objetivo**: Implementar dois microsserviços que se comunicam via HTTP.

**Tecnologias**: Docker, Python, Flask, HTTP REST

**Destaques**:
- Service A: API de gerenciamento de usuários
- Service B: Serviço que consome e enriquece dados
- Comunicação HTTP entre microsserviços
- Data enrichment e análises calculadas
- Isolamento completo com Dockerfiles separados
- Health checks verificando dependências

[📖 Ver documentação completa](./desafio4/README.md)

---

### ✅ [Desafio 5 — API Gateway com Microsserviços](./desafio5/)
**Objetivo**: Implementar um API Gateway que centraliza acesso a múltiplos microsserviços.

**Tecnologias**: Docker, Python, Flask, HTTP REST, API Gateway Pattern

**Destaques**:
- API Gateway como ponto de entrada único
- Microsserviço de Users (CRUD completo)
- Microsserviço de Orders (CRUD + estatísticas)
- Proxy de requisições para backends
- Endpoints de orquestração (combina dados de múltiplos serviços)
- Comunicação HTTP síncrona entre serviços
- Tratamento de erros e timeouts
- Health checks em cascata

[📖 Ver documentação completa](./desafio5/README.md)

---

## 📁 Estrutura do Repositório

```
projeto-fccpd/
├── README.md                 # Este arquivo
├── desafio1/                 # Desafio 1: Containers em Rede
│   ├── README.md
│   ├── docker-compose.yml
│   ├── server/
│   ├── client/
│   └── scripts/
├── desafio2/                 # Desafio 2: Volumes e Persistência
│   ├── README.md
│   ├── docker-compose.yml
│   ├── app/
│   ├── reader/
│   └── scripts/
├── desafio3/                 # Desafio 3: Orquestração
│   ├── README.md
│   ├── docker-compose.yml
│   ├── web/
│   └── scripts/
├── desafio4/                 # Desafio 4: Microsserviços
│   ├── README.md
│   ├── docker-compose.yml
│   ├── service-a/
│   ├── service-b/
│   └── scripts/
└── desafio5/                 # Desafio 5
```

## 🚀 Pré-requisitos Gerais

Para executar os desafios deste repositório, você precisará ter instalado:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 1.29 ou superior)
- **Git** (para clonar o repositório)
- **curl** (para testar APIs)

### Instalação do Docker

#### Linux (Ubuntu/Debian)
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

#### macOS
```bash
# Usando Homebrew
brew install --cask docker
```

#### Windows
Baixe e instale o [Docker Desktop](https://www.docker.com/products/docker-desktop)

## 📖 Como Usar Este Repositório

### 1. Clone o Repositório
```bash
git clone https://github.com/deadcube04/projeto-fccpd.git
cd projeto-fccpd
```

### 2. Navegue até o Desafio Desejado
```bash
cd desafio1
```

### 3. Siga as Instruções Específicas
Cada desafio possui seu próprio README.md com instruções detalhadas de execução.

## 🎓 Conceitos Abordados

### Desafio 1
- ✅ Containerização com Docker
- ✅ Redes Docker customizadas
- ✅ Comunicação entre containers
- ✅ Health checks e monitoramento
- ✅ APIs REST
- ✅ Logging estruturado

### Desafio 2
- ✅ Volumes Docker
- ✅ Persistência de dados
- ✅ PostgreSQL
- ✅ Named Volumes
- ✅ Container isolamento
- ✅ Backup e restore

### Desafio 3
- ✅ Docker Compose avançado
- ✅ Orquestração de serviços
- ✅ Cache distribuído (Redis)
- ✅ API Gateway pattern
- ✅ Service dependencies (depends_on)
- ✅ Health checks em cascata
- ✅ Comunicação entre microsserviços

### Desafio 4
- ✅ Arquitetura de microsserviços
- ✅ Comunicação HTTP/REST
- ✅ Service-to-service communication
- ✅ Data enrichment pattern
- ✅ Isolamento com containers
- ✅ Health checks de dependências
- ✅ Error handling em comunicação

### Desafio 5
- ✅ API Gateway pattern
- ✅ Microsserviços independentes
- ✅ Proxy de requisições
- ✅ Orquestração de serviços
- ✅ Comunicação HTTP síncrona
- ✅ Service-to-service orchestration
- ✅ Data aggregation
- ✅ Error handling e timeouts

### Desafios Futuros
- 🔜 Balanceamento de carga
- 🔜 Mensageria assíncrona
- 🔜 Escalabilidade horizontal
- 🔜 Service mesh

## 🛠️ Boas Práticas Aplicadas

- **Código Limpo**: Nomenclatura clara, comentários relevantes
- **Arquitetura Limpa**: Separação de responsabilidades, baixo acoplamento
- **Princípios SOLID**: Design orientado a objetos robusto
- **Containerização**: Imagens otimizadas (Alpine Linux)
- **Documentação**: README detalhados com diagramas e exemplos
- **Scripts de Automação**: Facilita execução e testes
- **Versionamento**: Commits semânticos e organizados

## 📊 Status dos Desafios

| Desafio | Status | Pontuação | Tecnologias |
|---------|--------|-----------|-------------|
| Desafio 1 | ✅ Concluído | 20/20 pts | Docker, Flask, Python |
| Desafio 2 | ✅ Concluído | 20/20 pts | Docker, PostgreSQL, Volumes |
| Desafio 3 | ✅ Concluído | 25/25 pts | Docker Compose, PostgreSQL, Redis |
| Desafio 4 | ✅ Concluído | 20/20 pts | Microsserviços, HTTP REST |
| Desafio 5 | ✅ Concluído | 25/25 pts | API Gateway, Microsserviços, Orquestração |

## 👤 Autor

**Nome**: Gabriel Melo Cavalcanti de Albuquerque  
**Curso**: Fundamentos de Computação Paralela e Distribuída  
**Ano**: 2025

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

## 🤝 Contribuições

Este é um projeto acadêmico individual. Sugestões e feedback são bem-vindos através das issues do GitHub.

## 📞 Contato

Para dúvidas ou sugestões:
- GitHub: [@deadcube04](https://github.com/deadcube04)
- Repositório: [projeto-fccpd](https://github.com/deadcube04/projeto-fccpd)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
