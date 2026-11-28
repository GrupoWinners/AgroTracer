# S7-T05 — Registro de Code Review (João Vitor: WordPress, Bridge, UI e Proxy/TLS)

Complemento ao gate de release (`docs/evidencias/sprint-7/S7-T05.md` e `docs/operacao/release-checklist.md`), cobrindo os itens atribuídos a **João Vitor**:

## 1. Bridge WordPress (`class-agrotracer-http-client.php` e `class-agrotracer-bridge.php`)

- **TLS obrigatório:** `AgroTracer_Http_Client::should_verify_ssl()` retorna `true` incondicionalmente; overrides inseguros (`AGROTRACER_API_SSLVERIFY = false`) são ignorados e cobertos por `test-s7-t05-release.php`.
- **Autorização explícita:** removido o fallback `publish_posts` em todas as rotas REST da Bridge e em `resolve_authorized_actor()`. Apenas usuários autenticados com capability explícita `agrotracer_manage_farms` têm acesso.
- **Preview offline controlado:** `AgroTracer_Bridge::allow_offline_preview()` só habilita dados demonstrativos quando `wp_get_environment_type()` é `local`/`development`, `AGROTRACER_OFFLINE_PREVIEW === true` e o usuário possui `manage_options`. Fora desse escopo, falhas de API retornam 503 sem simular escrita/leitura bem-sucedida.

## 2. Fluxo Real da Interface e Impacto das Listagens Mock

- O fluxo principal de demonstração e operação (**Fazendas**, **Lotes**, **Manejos por lote**, **Fechamento/Certificação**, **Download de PDF** e **Consulta Pública `/certificado/`**) comunica-se com a API FastAPI autenticada via HMAC.
- As listagens anteriormente exclusivamente demonstrativas (`GET /animais`, `GET /parametros`, `GET /fechamentos` e `GET /manejos` sem `lote_id`) agora respondem `503 DEMO_ONLY_UNAVAILABLE` fora do preview autorizado, evitando apresentar dados estáticos como persistidos em produção.
- A homologação visual final das telas em execução com QA (Nadiny) permanece vinculada ao gate `S7-T03`.

## 3. Proxy e Logs no Ambiente Alvo

- `certificado_publico_service.py` valida `AGROTRACER_TRUSTED_PROXIES` em modo fail-closed (`503 PROXY_CONFIG_INVALID`) para redes irrestritas (`0.0.0.0/0`, `::/0`) ou inválidas.
- `ops/demo/apache-safe-logs.conf` e `ops/demo/php-safe.ini` restringem logs Apache para status/duração (`%>s %D`), sem query string/token, e desativam `display_errors`/`expose_php`.

## Decisão do Review

- **Status da revisão técnica (WordPress/Bridge/Proxy):** **APROVADA**.
- **Pendência mantida:** QA final (`S7-T03`) antes de autorizar a tag `v1.0.0` (`S7-T06`).
