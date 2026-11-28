# S2-T03 — Movimentação com XOR e cronologia

## Entregas

- Modelo Movimentacao.
- Migration s2t03_movimentacoes.
- POST /api/v1/movimentacoes.
- CHECK animal XOR lote.
- CHECK origem diferente de destino.
- Quatro FKs com ON DELETE RESTRICT.
- Validação cronológica RN-07.
- Controle de concorrência no PostgreSQL.
- Autorização por objeto RN-19.
- Auditoria transacional.
- Erros com códigos e mensagens definidos.
- OpenAPI atualizado pelo FastAPI.

## Qualidade

- 11 testes específicos aprovados.
- 96 testes na execução consolidada.
- 1 teste S1-T01 excluído por exigir outro banco.
- Flake8 aprovado.

## Evidências

- S2-T03-pytest.txt
- S2-T03-flake8.txt
- Testes em test_s2_t03_api.py
- Testes em test_s2_t03_db.py
- Testes em test_s2_t03_concorrencia.py

## Pendências

- Code review do João Vitor.
- QA Gate da Nadiny.
- Merge na develop.
