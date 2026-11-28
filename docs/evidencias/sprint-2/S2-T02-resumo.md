# S2-T02 — Associação temporal

## Funcionalidades implementadas

- POST /api/v1/lotes/{lote_id}/animais
- DELETE /api/v1/lotes/{lote_id}/animais/{animal_id}
- Validação RN-06 na camada de serviço
- Autorização por produtor
- Erro HTTP 409 para associação ativa existente
- Encerramento sem exclusão da linha histórica
- Reassociação após encerramento
- Auditoria transacional da abertura e do encerramento

## Integridade e concorrência

A unicidade de associação ativa é protegida pelo
índice parcial uq_animal_associacao_ativa.

A API também trata violações desse índice,
retornando HTTP 409.

A estrutura e a concorrência do índice foram
testadas na S2-T01 e novamente incluídas na
execução consolidada da S2-T02.

## Testes

- Nove testes específicos da S2-T02
- Testes de regressão da S2-T01
- Testes PostgreSQL de integridade e concorrência
- Flake8

Consultar:
- S2-T02-pytest.txt
- S2-T02-flake8.txt

## Pendências de aprovação

- Code review
- QA Gate
- Merge
