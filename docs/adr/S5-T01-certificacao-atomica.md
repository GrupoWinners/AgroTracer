# AG-96 — certificacao atomica

Fonte: https://losel.atlassian.net/browse/AG-96, lida em 2026-11-18.
Responsavel: Samela; status Fazendo. Depende de S5-T03 e S4-T03;
bloqueia S5-T02 e S5-T04.

Escopo e aceite: POST /lotes/{id}/certificar; validar, calcular, criar
snapshot, token e persistir em transacao unica; rollback integral;
um certificado VALIDO por lote; clique duplo idempotente ou 409 controlado.
Indice parcial exigido: uq_certificado_valido_por_lote.

## Decisoes

- Rota sob /api/v1, autenticacao HMAC e autorizacao por proprietario.
- SELECT FOR UPDATE no lote serializa emissao/fechamento. Indice parcial
  protege tambem acessos concorrentes fora da rota.
- Idempotency-Key obrigatoria, 1–128 caracteres ASCII imprimiveis sem
  espacos, escopo por usuario, persistida como hash junto ao hash do payload.
- Repeticao retorna 409 CERTIFICACAO_JA_PROCESSADA; mudanca de payload com
  a mesma chave retorna 409 IDEMPOTENCY_KEY_REUTILIZADA. Outra chave no
  mesmo lote retorna 409 CERTIFICADO_JA_EXISTENTE. Nao emitir token novo
  nem armazenar original para reproduzir respostas.
- Resposta 201 inclui token uma unica vez e Cache-Control: no-store.
  Cliente deve guarda-lo para montar o link publico. Se perder a resposta,
  consultar o certificado por fluxo autenticado; nao tentar recuperar token
  por hash. Rotacao/reemissao nao foi especificada e nao foi implementada.
- Reutiliza fechamento/snapshot da Sprint 4. Se o lote ja estiver FECHADO,
  exige que os dados enviados coincidam; nao recalcula historico imutavel.
- Hash do snapshot: JSON UTF-8, sort_keys, separadores compactos,
  ensure_ascii=False; schema_version=1, versoes, entradas e resultados.
  Identificadores internos e timestamps ficam fora do conteudo canonico.
- Auditoria nao inclui token ou chave original. Commit somente na rota.

## Integracao e QA

S5-T04 deve enviar chave unica por tentativa logica e tratar 409 sem
duplicar emissao. S5-T05 integra consultar_token (S5-T03) e minimiza DTO.
PDF e gerado pela S5-T02 a partir do snapshot, sem alterar a certificacao.
Teste de indice PostgreSQL usa transacao revertida. Testes de falha cobrem
calculo, snapshot, token e auditoria; testes API cobrem autorizacao,
repeticao e compatibilidade com lotes fechados.

DoD: evidencias em docs/evidencias/sprint-5, erros e OpenAPI definidos,
review de outro integrante e QA Gate conforme risco; nenhum P1/P2 aberto
relacionado. Review/QA humanos pendentes; nao fazer merge automatico.
