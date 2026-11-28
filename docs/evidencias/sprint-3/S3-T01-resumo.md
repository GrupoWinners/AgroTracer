# S3-T01 — Manejos nutricionais

Validação local em 2026-11-07, no PostgreSQL descartável
`agrotracer_s2_t01_teste`. Base: `feature/S3-T02` (PR #27).

- Migration atual: `s3t01_manejos (head)`.
- Períodos inclusivos: [01,10] conflita com [10,15]; [11,11] é permitido.
- CHECK de datas/dieta e FKs RESTRICT exercitados no PostgreSQL.
- Duas sessões concorrentes, com commit real: uma gravação e um conflito.
  Verificado tanto pelo service (409 MANEJO_SOBREPOSTO) como diretamente
  pelo banco (SQLSTATE 23P01, constraint EXCLUDE GiST).
- Cleanup remove apenas os registros criados pelo próprio teste.
- Modelo usa EXCLUDE somente no PostgreSQL; SQLite não comprova concorrência.
- CI habilitado também para PRs encadeados sobre branches da Sprint 3.

Comandos no diretório backend, com as URLs do banco de teste configuradas:

```text
python -m alembic current
python -m flake8 app tests migrations/versions/s3t01_manejos_nutricionais.py
python -m pytest -q -k "not test_s1_t01_postgresql"
```

Resultado: lint sem erros; 154 passed, 1 deselected, 1 warning.
O teste S1-T01 exige outro banco e continua excluído conforme a base S3-T02.
Warning existente de depreciação Starlette/httpx. Não equivale a homologação
humana nem a aprovação do QA Gate; CI remoto deve ser conferido no PR.
