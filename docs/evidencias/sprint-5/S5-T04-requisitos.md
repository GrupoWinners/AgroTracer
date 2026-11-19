# AG-99 / S5-T04 — Fechar/emitir, loading, retry seguro e download

Fonte: https://losel.atlassian.net/browse/AG-99 (2026-11-18).
Responsavel: Joao Vitor Santos De Souza; status consultado: Fazendo.
Depende de S5-T01 (`POST /api/v1/lotes/{id}/certificar`) e S5-T02 (`GET /api/v1/certificados/{id}/pdf`).

## Escopo Implementado (WordPress Bridge & UI)

- **Cliente HTTP (`AgroTracer_Http_Client`):**
  - `post()` passa a aceitar `$extra_headers` (usado para propagar `Idempotency-Key` sem sobrescrever headers protegidos `X-AgroTracer-*`, `X-Correlation-ID` ou `Content-Type`).
  - `get_binary()` executa `GET` assinado por HMAC-SHA256 para bytes `application/pdf`, preservando `X-PDF-SHA256`, `Content-Disposition` e normalizando erros `404`/`409`/`503` sem vazar internos.
  - `map_error_to_ui_message()` mapeia os codigos da Sprint 5 (`CERTIFICACAO_JA_PROCESSADA`, `IDEMPOTENCY_KEY_REUTILIZADA`, `CERTIFICADO_JA_EXISTENTE`, `CERTIFICACAO_CONFLITANTE`, `FECHAMENTO_DIVERGENTE`, `SNAPSHOT_AUSENTE`, `CERTIFICADO_NAO_ENCONTRADO`, `PDF_INDISPONIVEL`).
- **Rotas REST WordPress (`AgroTracer_Bridge`):**
  - `POST /agrotracer/v1/lotes/{lote_id}/certificar`: valida `Idempotency-Key` (`^[\x21-\x7e]{1,128}$`), serializa `FechamentoEntrada` sem campos extras (`$bind_produtor_id = false`), despacha para `/api/v1/lotes/{lote_id}/certificar` e propaga `201` (`Cache-Control: no-store`), `409`, `422` ou `503`.
  - `GET /agrotracer/v1/certificados/{certificado_id}/pdf`: proxy autenticado via `get_binary()` com streaming binario direto via filtro `rest_pre_serve_request`, `Cache-Control: no-store`, `X-Content-Type-Options: nosniff` e `X-PDF-SHA256`.
- **Frontend (`fechamento.php`, `modals.php`, `agrotracer-screens.js`):**
  - Trava sincrona contra clique duplo (`isSubmitting` + `disabled` + spinner) no submit, modal de confirmacao e retry.
  - `Idempotency-Key` unica por tentativa logica (`buildAttemptFingerprint` + `getOrCreateIdempotencyKey`), preservada integralmente em falhas transientes (`503`/`ERRO_CONEXAO`) para o botao **Tentar Novamente (Retry Seguro)** e rotacionada ao alterar qualquer parametro.
  - Card do certificado emitido exibindo `id`, `status`, `snapshot_sha256`, link publico em memoria a partir do token unico e download privado do PDF com trava `isDownloadingPdf` e retry seguro em `503 PDF_INDISPONIVEL`.
