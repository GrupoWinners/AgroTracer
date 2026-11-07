# S3-T03 — API de manejos e consulta administrativa

## Contrato

- `POST /api/v1/lotes/{lote_id}/manejos`: 201 com id, lote_id, inicio, fim,
  parametro_set_id e tipo_dieta. Datas ISO AAAA-MM-DD inclusivas.
- Corpo: `{"inicio":"2026-11-01","fim":"2026-11-10",
  "parametro_set_id":1,"tipo_dieta":"PASTAGEM"}`.
- 409 `MANEJO_SOBREPOSTO`; 422 para dados inválidos; campos extras proibidos.
  Erros de validação e domínio usam `error.code`, `error.message`,
  `error.field_errors` e `error.correlation_id`.
- Lote inexistente e lote de outro produtor retornam o mesmo 404.
  Conjunto de parâmetros inexistente retorna 404. A regra herdada da S3-T01
  exige existência do conjunto, sem introduzir nova restrição de status.
- `GET /api/v1/admin/parametro-sets`: lista versões e fatores, com filtros
  `status=RASCUNHO|ATIVO|INATIVO`, `limit` (1–100, padrão 50), `offset` (>=0).
  Valores Decimal são strings JSON; source_type/source_uri são preservados.
- GET exige administrador configurado em AGROTRACER_ADMIN_WP_IDS.
  Não é rota para produtor comum; o consumidor WordPress deve respeitar isso.
- Ambas as rotas exigem os cinco headers HMAC do ADR-002, documentados em
  `/openapi.json`. Identidade nunca é aceita no corpo. Replays retornam 401.
- Manejo e auditoria CRIAR_MANEJO são confirmados atomicamente; correlation_id
  é propagado no header, nos erros e no evento.

## Evidência local — 2026-11-07

`python -m flake8 app tests`: sem erros.
`python -m pytest -q -k "not test_s1_t01_postgresql"`: 171 aprovados,
1 desmarcado (legado exige banco próprio), 1 warning Starlette/httpx.

Cobertura: 201/auditoria, 409/fronteiras, 422, IDOR/404, rollback quando a
auditoria falha, admin/403, paginação, Decimal/proveniência, HMAC real com
assinatura válida, identidade adulterada e replay (Redis simulado).
Teste PostgreSQL com duas requisições simultâneas confirma 201 + 409 e um
único evento de auditoria. As migrations reais da S3-T01 estão aplicadas.

Dependência: PR #28 sobre #27. Não declara homologação humana, integração
WordPress ou aprovação do QA Gate; revisão e merge continuam pendentes.
