# Sprint 6 — entregas Samela

Requisitos lidos integralmente no Jira em 19/11/2026; complemento SEC oficial
no Guia Comercial Detalhado v3 Revisado Tech Lead, pagina 19, secao 13.2.
O PDF foi consultado no caminho fornecido por Samela e nao foi copiado ao Git.

| Issue | Tarefa | Dependencia | PR/base |
| --- | --- | --- | --- |
| AG-103 | S6-T02 seguranca | S5-T06 integrada | #46 / develop |
| AG-104 | S6-T03 performance | S6-T02 | #47 / feature/S6-T02 |
| AG-107 | S6-T06 recuperacao (equipe) | S6-T02 e S6-T03 | #48 / feature/S6-T03 |

Base develop verificada antes de editar: ca4a86d1d64a0736d7d1a4b1e1f11ee4159eec41,
com Sprint 5 e S6-T01 integradas. Checkout limpo no inicio; nenhum arquivo
preexistente nao commitado foi sobrescrito. Nenhum merge para develop executado.

## Evidencias verificadas

- S6-T02: CI 127, 324 passed, 1 deselected pelo filtro historico
  `not test_s1_t01_postgresql`; migrations, lint, PostgreSQL e Redis reais.
  https://github.com/GrupoWinners/AgroTracer/actions/runs/44580703562
- S6-T03: CI 129, 327 passed, 1 deselected; resumo PostgreSQL em
  S6-T03-performance-ci.json e todas as amostras no artifact s6-performance.
  https://github.com/GrupoWinners/AgroTracer/actions/runs/44580975135
- S6-T06: CI 132 aprovada, restore real em containers independentes;
  relatorio S6-T06-restore-ci.json. RTO academico 4,389 s em destino
  pre-provisionado. Login WP, upload/Bridge, certificado publico e PDF HMAC
  com SHA-256 identico validados apos desligar origem.
  https://github.com/GrupoWinners/AgroTracer/actions/runs/44582596016

## Integracao e DoD

Revisar/aprovar na ordem #46, #47, #48. Quando a dependencia for integrada,
alterar a base do PR seguinte para develop, conferir o diff e executar CI/QA
novamente antes do merge. Em squash merge, verificar se commits herdados
reaparecem no diff e atualizar a branch antes de seguir.

Implementacao e evidencias automatizadas nao substituem review de outro
integrante, QA Gate e homologacao. Responsaveis devem registrar no Jira quem
revisou/homologou e bugs P1/P2 ou riscos aceitos com owner/data. S6-T06 exige
custodia conjunta Samela (API/DB/segredos) e Joao (WP/Bridge/proxy).
