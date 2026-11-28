# Sprint 7 — entregas Samela

Escopo confirmado pela usuaria: somente S7-T01 (AG-108) e S7-T05 (AG-112).
Requisitos integrais, dependencias, DoD e achados nos respectivos documentos.
Base develop apos Sprint 6: 86015bc1ee81a6064e95bfded83dd450e50fd377.

| PR | Branch | Base | Evidencia |
| --- | --- | --- | --- |
| #52 | feature/S7-T01 | develop | CI 145: demo limpa/repetida e 336 testes |
| #53 | feature/S7-T05 | feature/S7-T01 | CI 146: 341 testes, PHP, checklist e restore |

Ordem de review/integracao: #52 -> #53. Apos merge de #52, alterar base de
#53 para develop e conferir diff/CI novamente; nao executar merge sem review/QA.
Nenhuma tag ou merge realizado nesta entrega. Checkout inicial estava limpo.

`ci-verificada.json` contem apenas resultados seguros com link/commit.
O aceite de release S7-T05 permanece pendente de QA final (S7-T03) sem
P1/P2: em especial o impacto das listagens antes exclusivamente simuladas.
S7-T04 e S7-T06 nao executadas (tag `v1.0.0` aguarda QA final).

## Entregas complementares (João Vitor e Nadiny Martins)

- **PR #52 e PR #53:** revisados e integrados na `develop` na ordem `#52 -> #53`.
- **S7-T02 (João Vitor):** manual curto do fluxo do usuario em `docs/operacao/manual-usuario.md` e evidencia em `docs/evidencias/sprint-7/S7-T02.md`.
- **S7-T05 (review Bridge/UI/Proxy - João Vitor):** registrado em `docs/evidencias/sprint-7/S7-T05-review-joao.md`.
- **S7-T03 (QA Final e Release Gate - Nadiny Martins):** matriz consolidada de testes (S0 a S7), resultados de UAT nos 5 vetores de resiliência e inventário de bugs conhecidos (zero P1/P2 em aberto), registrado em `docs/evidencias/sprint-7/S7-T03.md`, `S7-T03-testes.txt` e suíte automatizada `backend/tests/test_s7_t03_qa_final.py`. Homologação aprovada, liberando S7-T04 e S7-T06.
