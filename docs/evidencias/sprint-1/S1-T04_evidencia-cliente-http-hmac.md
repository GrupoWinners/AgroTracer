---
title: "S1-T04 — Evidência Técnica: Cliente HTTP Centralizado, Assinatura HMAC-SHA256 e Testes Anti-Replay (agrotracer-bridge)"
date: 2026-10-22
author: "João Vitor (Losel)"
tags:
  - agrotracer
  - wordpress
  - php
  - seguranca
  - hmac
  - sprint-1
status: "Concluído e Homologado"
version: "3.1.0"
---

# S1-T04 — Registro de Evidência Técnica: Cliente HTTP Centralizado e Assinatura HMAC-SHA256 (`agrotracer-bridge`)

- **Épico:** `[EP-S1] Sprint 1 — Fundação de dados e identidade`
- **Task:** `S1-T04` — Implementar cliente HTTP centralizado, assinar `GET`/`POST`, validar identidade server-side e mapear erros de UI
- **Responsável Técnico:** João Vitor Santos de Souza (P.O. / Front-end & WordPress Lead)
- **Revisão Cruzada:** Samela Maria (Back-end Python / FastAPI) & Nadiny Martins (QA Lead)
- **Referência Arquitetural:** Guia AgroTracer v3.0 (Seções 4.2, 4.3, 6.3) e ADR-002
- **Data da Execução:** 22/10/2026
- **Status:** ✅ **APROVADO (DoD 100% ATINGIDO)**

---

## 1. Resumo de Engenharia

Foi implementado no plugin `agrotracer-bridge` o cliente HTTP centralizado `\AgroTracerBridge\Http\AgroTracer_Http_Client` (`includes/class-agrotracer-http-client.php`), isolando toda a comunicação servidor-a-servidor entre WordPress e FastAPI sob tipagem estrita (`declare(strict_types=1);`).

### Garantias de Segurança Implementadas
1. **Transporte Nativo Defensivo:** Uso exclusivo de `wp_remote_get()` e `wp_remote_post()` com timeout defensivo explícito (`DEFAULT_TIMEOUT_SECONDS = 10`, configurável via `AGROTRACER_API_TIMEOUT`), `redirection => 0` e controle de TLS (`sslverify`).
2. **Derivação Estrita de Identidade Server-Side:** O método `resolve_authorized_actor()` valida obrigatoriamente o nonce do WordPress (`wp_verify_nonce`), verifica a capability (`current_user_can('agrotracer_manage_farms')`) e extrai o ator exclusivamente via `get_current_user_id()`. O método `sanitize_actor_payload()` remove qualquer chave `user_id`, `actor_id` ou `produtor_id` vinda do navegador.
3. **Pacote de Headers Obrigatórios e Rastreabilidade:**
   - `X-AgroTracer-Actor-ID` e `X-AgroTracer-User-Id`: ID do usuário autenticado resolvido no backend WordPress.
   - `X-AgroTracer-Timestamp`: Timestamp UNIX UTC em segundos.
   - `X-AgroTracer-Nonce`: Nonce criptográfico de 128 bits (`bin2hex(random_bytes(16))`) único por requisição.
   - `X-AgroTracer-Signature`: Assinatura `HMAC-SHA256` em hexadecimal minúsculo computada sobre o payload canônico (`METHOD\nPATH_WITH_QUERY\nTIMESTAMP\nNONCE\nACTOR_ID\nSHA256_BODY`).
   - `X-Correlation-ID`: UUIDv4 canônico propagado de ponta a ponta.
4. **Mapeamento Seguro de Falhas para UI:** Tradução não vazada dos status `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500` e `503` em `map_error_to_ui_message()`, suprimindo qualquer stack trace Python ou erro SQL (`psycopg`).

---

## 2. Log de Execução da Suíte de Testes Automatizados

**Comando Executado:**
```powershell
php wordpress/agrotracer-bridge/tests/test-agrotracer-http-client.php
```

**Saída Real Obtida (Runtime PHP 8.2.29 x64):**
```text
PHPUnit / AgroTracer Bridge Security & Contract Test Runner (PHP 8.2.29)
=========================================================================
 [PASS] test_happy_path_get_request_with_valid_headers_and_signature_is_approved
 [PASS] test_happy_path_post_request_and_official_vector_match
 [PASS] test_rejection_when_actor_id_in_header_is_tampered
 [PASS] test_rejection_when_request_body_is_modified_after_signing
 [PASS] test_rejection_when_timestamp_is_outside_tolerance_window
 [PASS] test_rejection_when_nonce_is_reused_in_replay_attack
 [PASS] test_identity_and_capability_enforcement
 [PASS] test_ui_error_mapping_for_400_401_403_404_422_500_without_leaking_internals
-------------------------------------------------------------------------
Time: 8.1 ms | Tests: 8 | Passed: 8 | Failed: 0 | Assertions: 72
```

---

## 3. Matriz de Rastreabilidade de Testes (Critérios de Aceite)

| ID | Cenário Exercitado | Método de Teste | Resultado Esperado | Status |
| :--- | :--- | :--- | :--- | :---: |
| **CT-01** | **Fluxo Feliz GET:** Normalização RFC 3986, headers obrigatórios e assinatura HMAC válida | `test_happy_path_get_request_with_valid_headers_and_signature_is_approved` | `HTTP 200 OK` + strip de `user_id` na query | ✅ PASS |
| **CT-02** | **Fluxo Feliz POST:** Assinatura de body JSON, paridade 100% com vetor Python e vínculo de `produtor_id` | `test_happy_path_post_request_and_official_vector_match` | `HTTP 201 Created` + hash `ca62dbbd...` exato | ✅ PASS |
| **CT-03** | **Rejeição por Adulteração de Ator:** Alteração de `X-AgroTracer-Actor-ID` (`42` -> `99`) pós-assinatura | `test_rejection_when_actor_id_in_header_is_tampered` | `HTTP 401 Unauthorized` (`AUTH_SIGNATURE_MISMATCH`) | ✅ PASS |
| **CT-04** | **Rejeição por Adulteração de Body:** Modificação do JSON em trânsito após cálculo do HMAC | `test_rejection_when_request_body_is_modified_after_signing` | `HTTP 401 Unauthorized` (`AUTH_SIGNATURE_MISMATCH`) | ✅ PASS |
| **CT-05** | **Rejeição por Timestamp Expirado/Futuro:** Timestamp fora da janela de `±300s` (`-301s` e `+301s`) | `test_rejection_when_timestamp_is_outside_tolerance_window` | `HTTP 401 Unauthorized` (`AUTH_TIMESTAMP_EXPIRED`) | ✅ PASS |
| **CT-06** | **Rejeição por Ataque de Replay:** Reenvio de requisição com o mesmo `X-AgroTracer-Nonce` dentro do TTL (`660s`) | `test_rejection_when_nonce_is_reused_in_replay_attack` | 1ª: `200 OK` / 2ª: `HTTP 401` (`AUTH_NONCE_REPLAYED`) | ✅ PASS |
| **CT-07** | **Guarda de Sessão, Nonce WP e Capability:** Bloqueio de CSRF inválido, anônimo (`ID=0`) e sem permissão | `test_identity_and_capability_enforcement` | `401` para nonce/sessão inválida; `403` sem capability | ✅ PASS |
| **CT-08** | **Mapeamento Seguro de Erros UI:** Códigos `400, 401, 403, 404, 422, 500` sem vazamento de SQL/Traceback | `test_ui_error_mapping_for_400_401_403_404_422_500_without_leaking_internals` | Mensagens amigáveis em PT-BR; zero leak de `SELECT *` | ✅ PASS |

---

## 4. Auditoria de Segurança e Ausência de Segredos Commitados

Foi executada varredura estática sobre os arquivos do plugin e bundle JavaScript:
1. **Bundle Front-end (`assets/js/agrotracer-screens.js` e `wp_localize_script`):** Contém apenas `ajaxUrl`, `restUrl`, `nonce` (CSRF do WP) e `correlationId`. Nenhuma chave HMAC ou segredo compartilhado é injetado no DOM.
2. **Repositório Git (`.env.example` e `wordpress/agrotracer-bridge/`):** Nenhuma chave de produção commitada; leitura realizada via constantes de ambiente (`AGROTRACER_API_HMAC_SECRET` / `AGROTRACER_BRIDGE_SECRET`).

---

## 5. Checklist de Definition of Done (DoD — Sprint 1 / Task S1-T04)

- [x] **Código-fonte em PHP com `declare(strict_types=1);`:** Implementado em `includes/class-agrotracer-http-client.php` e integrado ao controller `includes/class-agrotracer-bridge.php`.
- [x] **Uso das APIs nativas (`wp_remote_get`, `wp_remote_post`) com timeout defensivo:** Configurado (`10s` padrão, limitado entre `2s` e `30s`).
- [x] **Resolução estrita do ator via `get_current_user_id()` após `wp_verify_nonce()` e `current_user_can()`:** Validado e testado.
- [x] **Bloqueio de `user_id` vindo do navegador e zero exposição de segredo HMAC no front-end:** Sanitização ativa em `sanitize_actor_payload()`.
- [x] **Headers obrigatórios (`X-AgroTracer-Actor-ID`, `X-AgroTracer-Timestamp`, `X-AgroTracer-Nonce`, `X-AgroTracer-Signature`, `X-Correlation-ID`):** Presentes e validados por regex e HMAC.
- [x] **Mapeamento amigável de erros (`400, 401, 403, 404, 422, 500`):** Implementado em `map_error_to_ui_message()` com sanitização de `field_errors`.
- [x] **Suíte de testes automatizados passando 100% (8/8 testes, 72 asserções):** Fluxo feliz, adulteração de ator/body, timestamp expirado e ataque de replay comprovados.
