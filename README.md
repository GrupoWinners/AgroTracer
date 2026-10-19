# AgroTracer
Projeto desenvolvido pelo Grupo Winners.

## Objetivo
Sistema AgroTracer.

## Status
Sprint 0 - Preparação do ambiente.

## Requisitos
Python 3.12+ (ambiente testado com Python 3.14.7).
Docker Desktop com Docker Compose.

## Configuração do ambiente
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
```

## Verificação de código
O Flake8 é utilizado para verificar problemas de qualidade e formatação.

```bash
python -m flake8 app tests
```

## Testes automatizados
O projeto AgroTracer utiliza Pytest para executar verificações automatizadas.

```bash
python -m pytest -v
```

## Inicialização do ambiente completo

As instruções abaixo consideram Windows com Git Bash
e Docker Desktop instalado.

### 1. Clonar o projeto

```bash
git clone https://github.com/GrupoWinners/AgroTracer.git
cd AgroTracer
```

### 2. Configurar as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

No arquivo `.env`, defina uma senha local para
POSTGRES_PASSWORD e utilize a mesma senha na DATABASE_URL.

A DATABASE_URL utiliza a porta 55432, correspondente à
porta publicada pelo Docker Compose.

Nunca envie o arquivo `.env` ao GitHub.

### 3. Iniciar o PostgreSQL

Com o Docker Desktop aberto, na raiz do projeto:

```bash
docker compose up -d db
docker compose ps
```

Aguarde até o contêiner apresentar o estado healthy.

### 4. Preparar o Python

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
```

### 5. Carregar as variáveis de ambiente

```bash
set -a
source ../.env
set +a
```

### 6. Aplicar as migrations

```bash
python -m alembic upgrade head
python -m alembic current
```

A migration inicial habilita a extensão btree_gist
no PostgreSQL.

Todas as alterações de estrutura do banco deverão
ser realizadas por migrations.

### 7. Iniciar a API FastAPI

```bash
python -m uvicorn app.main:app --reload
```

A API ficará disponível em:

- Health: http://127.0.0.1:8000/health
- Swagger/OpenAPI: http://127.0.0.1:8000/docs
- Especificação JSON: http://127.0.0.1:8000/openapi.json

O endpoint /health deve responder HTTP 200 com:

```json
{"status": "ok"}
```

### 8. Executar os testes

Em outro terminal, dentro da pasta backend,
com o ambiente virtual ativado:

```bash
python -m pytest -v
python -m flake8 app tests
```

Os testes devem passar e o Flake8 não deve
apresentar erros.

### 9. Encerrar o ambiente

Interrompa o FastAPI com Ctrl+C.

Na raiz do projeto:

```bash
docker compose down
```

O volume do PostgreSQL será preservado.

Não utilize `docker compose down -v` para
encerrar normalmente, pois isso remove o
volume de dados.
