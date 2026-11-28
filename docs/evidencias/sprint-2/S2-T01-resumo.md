# S2-T01 — Lotes, animais e associação temporal

## Objetivo

Implementar o cadastro de lotes e animais e a estrutura
de associação temporal, garantindo integridade dos dados,
autorização e preservação do histórico.

## Implementações

- Modelos SQLAlchemy: Lote, Animal e LoteAnimal.
- Relacionamentos ORM com ON DELETE RESTRICT.
- Migrations Alembic:
  - s2t01_lotes_animais
  - s2t01_estados
- Índice parcial uq_animal_associacao_ativa.
- Ausência de animais.lote_id, conforme ADR-003.
- POST /api/v1/lotes.
- GET /api/v1/lotes.
- GET /api/v1/lotes/{id}.
- POST /api/v1/animais.
- Autenticação HMAC e autorização por produtor.
- Auditoria transacional nos cadastros.

## RN-04 — Decisão adotada nesta sprint

Estados:

RASCUNHO -> EM_MANEJO -> FECHADO

- RASCUNHO é o estado inicial.
- Não é permitido pular estados.
- Não é permitido retroceder.
- FECHADO é um estado final.

A API não permite que o cliente escolha o estado
inicial do lote.

O PostgreSQL possui CHECK para impedir estados
fora do conjunto permitido.

As transições são validadas na camada de domínio.
A CHECK do banco não substitui essa validação.

A aplicação das transições nos fluxos futuros deve
reutilizar validar_transicao_lote().

Esta decisão complementa o Guia v3.0 e está
sujeita à revisão do João Vitor.

## RN-05 — Identificação animal

- Identificador único.
- RFID opcional.
- Produtor vinculado à identidade autenticada.

## RN-06 e ADR-003 — Associação temporal

- Vínculos registrados em lote_animais.
- associado_em e desassociado_em.
- Apenas uma associação ativa por animal.
- Índice parcial no PostgreSQL.
- Histórico preservado.
- ON DELETE RESTRICT nas referências históricas.

## Testes realizados

- Validação dos modelos ORM.
- Testes dos endpoints.
- Cadastro e duplicidade.
- Auditoria.
- Autorização por objeto (BOLA).
- Integridade das FKs e constraints.
- Bloqueio de associação ativa duplicada.
- Teste de concorrência com duas transações.
- Transições válidas e inválidas da RN-04.
- Verificação de estado inválido no PostgreSQL.
- Verificações com pytest e Flake8.

Evidências:
- S2-T01-pytest.txt
- S2-T01-flake8.txt

Observação: o teste PostgreSQL específico da S1-T01
foi excluído da execução consolidada da Sprint 2
porque exige outro banco de testes.

## Continuidade

S2-T02: implementar abertura e encerramento de
associações temporais com auditoria.

S2-T03: implementar movimentações e validação
cronológica.

## Aprovação

Code review: pendente — João Vitor.
QA Gate: pendente — Nadiny.
Merge em develop: pendente.
