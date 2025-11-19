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

### 🔜 Desafio 2
*Em desenvolvimento...*

---

### 🔜 Desafio 3
*Em desenvolvimento...*

---

### 🔜 Desafio 4
*Em desenvolvimento...*

---

### 🔜 Desafio 5
*Em desenvolvimento...*

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
├── desafio2/                 # Desafio 2
├── desafio3/                 # Desafio 3
├── desafio4/                 # Desafio 4
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

### Desafios Futuros
- 🔜 Microsserviços
- 🔜 Balanceamento de carga
- 🔜 Mensageria
- 🔜 Persistência de dados
- 🔜 Escalabilidade horizontal

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
| Desafio 2 | 🔜 Pendente | - | - |
| Desafio 3 | 🔜 Pendente | - | - |
| Desafio 4 | 🔜 Pendente | - | - |
| Desafio 5 | 🔜 Pendente | - | - |

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
