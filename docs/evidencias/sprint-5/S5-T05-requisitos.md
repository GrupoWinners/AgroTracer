# AG-100 / S5-T05 — Página pública de verificação e DTO minimizado (RN-13)

Responsável: João Vitor Santos de Souza
Depende de: S5-T03 (`consultar_token` + rate limit por IP no Redis) e S5-T04 (link público em memória).
Bloqueia: S5-T06.

## Escopo Implementado

### 1. Backend FastAPI (DTO Minimizado & Consulta Pública)
- **Schema (`backend/app/schemas/certificado_publico.py`):**
  - `CertificadoPublicoSaida` e `CertificadoPublicoResultados` com `ConfigDict(extra="forbid")`.
  - Allowlist estrita: `certificado_id`, `lote_id`, `status` (`VALIDO` | `REVOGADO`), `emitido_em`, `versao_metodo`, `versao_parametros`, `source_types`, `synthetic`, `aviso_proveniencia`, `data_abate`, `numero_animais_abate`, `resultados` (strings preservadas sem arredondamento + unidades), `snapshot_sha256` e `pdf_sha256` (quando gerado).
  - Exclui rigorosamente dados pessoais do produtor (nome, CPF/CNPJ, e-mail, telefone, `wordpress_user_id`), dados de propriedade (fazenda, CAR, município/UF, coordenadas), identificadores de animais, `token`, `token_hash`, `idempotency_hash`, `request_hash` e `source_uri`.
- **Serviço (`backend/app/services/certificado_publico_service.py`):**
  - Integra `consultar_token()` (S5-T03) aplicando rate limit compartilhado no Redis (30 consultas/minuto por IP, retornando `429` ao exceder e `503` se Redis indisponível).
  - `obter_ip_cliente()` utiliza o IP direto da conexão; `X-Forwarded-For` só é considerado quando `AGROTRACER_TRUSTED_PROXIES` está explicitamente configurado.
  - Valida integridade criptográfica do snapshot (`SNAPSHOT_INTEGRO_OBRIGATORIO` -> `409`).
- **Rota (`GET /api/v1/certificados/publico?token=...`):**
  - Pública (sem exigência de sessão WordPress/HMAC), retornando `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff` e `X-Robots-Tag: noindex, nofollow`.

### 2. WordPress Bridge, Página Pública e QR Code Local
- **Cliente HTTP (`AgroTracer_Http_Client::get_public`):**
  - Executa `GET` público sem cabeçalhos de ator/HMAC e mapeia `CONSULTA_INDISPONIVEL`, `LIMITE_CONSULTAS` e `SNAPSHOT_INTEGRO_OBRIGATORIO`.
- **Controlador & Shortcode (`AgroTracer_Bridge` / `AgroTracer_Shortcodes`):**
  - Provisiona de forma idempotente a página `/certificado/` com shortcode `[agrotracer_certificado_publico]` e canvas isolado (`templates/canvas-certificado-publico.php`).
  - Expõe `GET /wp-json/agrotracer/v1/certificados/publico` com allowlist defensiva (`sanitize_public_certificate_dto`) e resposta genérica `404 CERTIFICADO_NAO_ENCONTRADO` (`"Certificado não encontrado."`, RN-13).
- **Interface Pública (`templates/certificado-publico.php`) e QR Local (`fechamento.php`, `agrotracer-screens.js`):**
  - Badges semânticos (`agro-badge success` para `VALIDO`; `agro-badge danger` + alerta para `REVOGADO`), banner explícito `[SYNTHETIC]` e escape HTML em todos os campos.
  - Geração 100% local em memória de QR Code SVG ISO-18004 (`buildQrCodeSvg`) no card de emissão (`#cert-res-qr-container`), sem enviar o token opaco a serviços externos.
