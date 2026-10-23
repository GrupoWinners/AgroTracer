# AgroTracer
Projeto desenvolvido pelo Grupo Winners.

## Objetivo
Sistema AgroTracer.

## Status
Sprint 0 - Preparação do ambiente.

## Requisitos
Python 3.14.7

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
