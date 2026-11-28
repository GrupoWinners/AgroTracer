# S4-T03 — Evidencia de snapshot e transacao

## Implementacao

- Fechamento do lote persiste entradas, resultados, chaves, valores,
  unidades, source_type/source_uri e versao de parametros no mesmo commit.
- `snapshots_fechamento` tem FK RESTRICT, versao_metodo, parametro_set_id
  e payloads JSONB com valores Decimais preservados como strings.
- Triggers PostgreSQL impedem UPDATE/DELETE de snapshots e fechamentos.
- Constraint trigger DEFERRABLE exige snapshot correspondente antes de
  confirmar um fechamento, protegendo contra gravacao parcial.
- Manejos novos sao bloqueados depois que o lote estiver FECHADO.

## Testes automatizados incluidos

- `backend/tests/test_s4_t03_snapshot.py`: persistencia,
  rollback de erro simulado, dados invalidos, timeline fechada.
- `backend/tests/test_s4_t03_postgresql.py`: presenca de triggers,
  fechamento sem snapshot rejeitado e imutabilidade no banco.
- `backend/tests/test_s4_t02_fechamento.py`: pre-condicoes RN-09 e RN-10,
  acesso por objeto, auditoria e erro 422.
- `backend/tests/test_s4_t01_carbon_engine.py`: exemplo sintetico
  13650 / 0.954, datas inclusivas e sem arredondamento por etapa.

## Qualidade e revisao

- CI GitHub Actions executa Alembic, Flake8 e Pytest no PostgreSQL de teste.
- Conferir resultados do PR #35 na ultima revisao para aprovar o QA Gate.
- Revisao humana por outro integrante e Nadiny ainda sao necessarias.
- O teste legado S1-T01 segue excluido temporariamente no CI do projeto.

## Metodologia

O resultado e demonstracao matematica sintética, sem afirmacao de
validade cientifica ou fator oficial atribuido ao IPCC/Embrapa.
