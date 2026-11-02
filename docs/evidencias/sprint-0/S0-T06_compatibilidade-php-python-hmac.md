# S0-T06 — Registro de Evidência: Compatibilidade HMAC-SHA256, Normalização RFC 3986 e Fechamento do Protocolo (PHP WordPress ↔ Python FastAPI)

- **Projeto:** AgroTracer
- **Sprint:** 0 / Integração Sprint 1
- **Tasks Relacionadas:** `S0-T06` (`feature/PY-06`) e `S1-T03` (`feature/WP-03-fazendas-ui`)
- **Referência Arquitetural:** ADR-002 — Autenticação e Segurança da Bridge
- **Equipe (Grupo Winners):** DEV Front-end & PO: João Vitor | Back-End & Scrum: Samela Maria | QA & UI: Nadiny Martins
- **Data da Atualização:** 19/10/2026
- **Status:** ✅ 100% COMPATÍVEL, DELIBERADO E HOMOLOGADO

---

## 1. Validação dos Vetores de Teste Oficiais (HMAC-SHA256)

Os vetores de teste compartilhados entre o backend Python (`backend/app/core/hmac_protocol.py` / `backend/tests/test_hmac_protocol.py`) e o plugin WordPress (`AgroTracer_Bridge::build_canonical_string` / `AgroTracer_Bridge::generate_hmac_signature` em `wordpress/agrotracer-bridge/includes/class-agrotracer-bridge.php`) foram executados e confrontados nos runtimes **PHP 8.2.29 (x64)** e **Python 3.14.7**.

### 1.1. Vetor Oficial #1 — Requisição Base Sem Query String

| Campo | Valor |
| :--- | :--- |
| `METHOD` | `POST` |
| `PATH_WITH_QUERY` | `/api/v1/fazendas` |
| `TIMESTAMP` | `1792020000` |
| `NONCE` | `00112233445566778899aabbccddeeff` |
| `WP_USER_ID` | `42` |
| `BODY` | `{}` |
| `SHA256_BODY` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| `AGROTRACER_BRIDGE_SECRET` | `agrotracer_chave_exclusivamente_teste_2026` |

**Canonical String Gerada (PHP e Python):**
```text
POST
/api/v1/fazendas
1792020000
00112233445566778899aabbccddeeff
42
44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
```

- **Python (`hmac_protocol.gerar_assinatura`):** `ca62dbbd01854e311b419ff2e64d3721e0ccb6bf698ebcf94f9026e5d562c9bc`
- **PHP (`AgroTracer_Bridge::generate_hmac_signature`):** `ca62dbbd01854e311b419ff2e64d3721e0ccb6bf698ebcf94f9026e5d562c9bc`
- **Resultado:** `MATCH EXATO (100%)`

---

### 1.2. Vetor Oficial #2 — Parâmetros Fora de Ordem, Espaço (`+`) e Chaves Repetidas (Validação Cruzada 19/10/2026)

| Campo | Valor |
| :--- | :--- |
| `METHOD` | `POST` |
| `URL Original` | `/api/v1/fazendas?tag=2&nome=Fazenda+Azul&cidade=Araguari&tag=1` |
| `URL Normalizada (RFC 3986)` | `/api/v1/fazendas?cidade=Araguari&nome=Fazenda%20Azul&tag=2&tag=1` |
| `TIMESTAMP` | `1792020000` |
| `NONCE` | `00112233445566778899aabbccddeeff` |
| `WP_USER_ID` | `42` |
| `BODY` | `{}` |
| `SHA256_BODY` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| `AGROTRACER_BRIDGE_SECRET` | `agrotracer_chave_exclusivamente_teste_2026` |

**Canonical String Gerada (PHP e Python):**
```text
POST
/api/v1/fazendas?cidade=Araguari&nome=Fazenda%20Azul&tag=2&tag=1
1792020000
00112233445566778899aabbccddeeff
42
44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
```

- **Python (`hmac_protocol.gerar_assinatura`):** `75ff30bfcf8c437b26ae0f3ee554319cb8e131ab19bcaffcde294190159dada6`
- **PHP (`AgroTracer_Bridge::generate_hmac_signature`):** `75ff30bfcf8c437b26ae0f3ee554319cb8e131ab19bcaffcde294190159dada6`
- **Resultado:** `MATCH EXATO (100%)`

---

## 2. Vetores de Casos Especiais de Normalização e Entradas Inválidas (`PATH_WITH_QUERY` — RFC 3986)

Para garantir paridade absoluta com `normalizar_path_query()` do Python (`parse_qsl(..., keep_blank_values=True, errors="strict")` + `urlencode(..., quote_via=quote, safe="")`), a camada PHP implementa `AgroTracer_Bridge::normalize_path_query()` utilizando `explode('&')`, `urldecode()`, validação estrita de UTF-8 (`preg_match('//u', ...)`), ordenação alfabética estável pela chave (`usort` com desempate por índice de chegada `$a['idx'] <=> $b['idx']`, idêntico ao Timsort do Python) e `rawurlencode()` (RFC 3986).

### 2.1. Casos Válidos de Canonicalização
| Caso de Teste | Entrada (`path_with_query`) | Saída PHP (`normalize_path_query`) | Saída Python (`normalizar_path_query`) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. Sem query string** | `/api/v1/fazendas` | `/api/v1/fazendas` | `/api/v1/fazendas` | ✅ Match |
| **2. Ordenação simples** | `/api/v1/fazendas?z=9&a=1` | `/api/v1/fazendas?a=1&z=9` | `/api/v1/fazendas?a=1&z=9` | ✅ Match |
| **3. Espaços (`+` e `%20`)** | `/api/v1/fazendas?status=ativo&nome=Fazenda+Azul` | `/api/v1/fazendas?nome=Fazenda%20Azul&status=ativo` | `/api/v1/fazendas?nome=Fazenda%20Azul&status=ativo` | ✅ Match |
| **4. Acentos UTF-8** | `/api/v1/fazendas?nome=Fazenda+Azul&municipio=Uberl%C3%A2ndia` | `/api/v1/fazendas?municipio=Uberl%C3%A2ndia&nome=Fazenda%20Azul` | `/api/v1/fazendas?municipio=Uberl%C3%A2ndia&nome=Fazenda%20Azul` | ✅ Match |
| **5. Chaves repetidas (ordem preservada)** | `/api/v1/fazendas?tag=2&nome=Fazenda+Azul&cidade=Araguari&tag=1` | `/api/v1/fazendas?cidade=Araguari&nome=Fazenda%20Azul&tag=2&tag=1` | `/api/v1/fazendas?cidade=Araguari&nome=Fazenda%20Azul&tag=2&tag=1` | ✅ Match |
| **6. Valores vazios repetidos** | `/api/v1/fazendas?b=&a=1&b=` | `/api/v1/fazendas?a=1&b=&b=` | `/api/v1/fazendas?a=1&b=&b=` | ✅ Match |
| **7. Caractere UTF-8 U+FFFD legítimo** | `/api/v1/fazendas?nome=%EF%BF%BD` | `/api/v1/fazendas?nome=%EF%BF%BD` | `/api/v1/fazendas?nome=%EF%BF%BD` | ✅ Match |
| **8. Caracteres RFC 3986** | `/api/v1/fazendas?filtro=a/b~c_d-e.f*g` | `/api/v1/fazendas?filtro=a%2Fb~c_d-e.f%2Ag` | `/api/v1/fazendas?filtro=a%2Fb~c_d-e.f%2Ag` | ✅ Match |
| **9. Path percent-encoded** | `/api/v1/fazendas%20teste?b=2&a=1` | `/api/v1/fazendas%20teste?a=1&b=2` | `/api/v1/fazendas%20teste?a=1&b=2` | ✅ Match |

### 2.2. Rejeição Estrita de Entradas Inválidas
| Caso de Teste | Entrada Inválida | Comportamento PHP | Comportamento Python | Status |
| :--- | :--- | :--- | :--- | :--- |
| **10. Path sem `/` inicial** | `api/v1/fazendas` | Lança `InvalidArgumentException` | Lança `ValueError` | ✅ Match |
| **11. URL absoluta com scheme/host** | `https://exemplo.com/api/v1/fazendas` | Lança `InvalidArgumentException` | Lança `ValueError` | ✅ Match |
| **12. URL com fragmento `#`** | `/api/v1/fazendas#fragmento` | Lança `InvalidArgumentException` | Lança `ValueError` | ✅ Match |
| **13. Byte UTF-8 inválido (`%FF`)** | `/api/v1/fazendas?nome=%FF` | Lança `InvalidArgumentException` | Lança `UnicodeDecodeError` | ✅ Match |

---

## 3. Deliberações Arquiteturais e Fechamento do Protocolo (ADR-002)

### 3.1. Aprovação do TTL do Nonce em 660 Segundos (`SET NX EX 660`)
- **Decisão:** **APROVADO** (`AgroTracer_Bridge::NONCE_TTL_SECONDS = 660` / `NONCE_TTL_SEGUNDOS = 660`).
- **Fundamentação Técnica:** Como o FastAPI aceita timestamps na janela de `±300s` em relação ao relógio UTC do servidor, uma requisição assinada com `timestamp = T + 300` recebida no instante `T` permanece válida dentro da janela temporal até `T + 600`. O TTL de `660 segundos` (`600s` da janela total + `60s` de margem de segurança) elimina qualquer condição de corrida ou brecha de replay na extremidade da janela.

### 3.2. Convenção de Usuário de Sistema (`WP_USER_ID = 0`) e Derivação Exclusiva no Servidor
- **Decisão:** **APROVADO** (`AgroTracer_Bridge::SYSTEM_USER_ID = 0`).
- **Derivação Server-Side no WordPress:** Nas rotas REST do plugin (`handle_create_farm` e `handle_get_farms` em `class-agrotracer-bridge.php`), a identidade `X-AgroTracer-User-Id` é obtida exclusivamente no servidor via `(int) get_current_user_id()`, após verificação de sessão (`is_user_logged_in()`) e capability (`current_user_can('agrotracer_manage_farms')`), ignorando qualquer identificador enviado pelo navegador no payload ou headers.
- **Isolamento de Rotas de Negócio vs. Sistema:**
  - `WP_USER_ID > 0`: Obrigatório para todas as rotas de negócio acionadas por usuários WordPress (validado tanto no WordPress quanto na dependência `exigir_usuario_wordpress` do FastAPI).
  - `WP_USER_ID = 0`: Reservado exclusivamente para rotinas internas/sistema autorizadas que utilizem apenas `exigir_autenticacao_bridge`. Tentativas de uso de `WP_USER_ID = 0` em rotas de usuário são bloqueadas com **HTTP 403 (`AUTH_USER_REQUIRED`)**.

### 3.3. Catálogo Consolidado de Erros da Bridge
| Código de Erro | HTTP Status | Condição de Disparo |
| :--- | :---: | :--- |
| `AUTH_INVALID_REQUEST` | `401 Unauthorized` | Headers ausentes/inválidos, timestamp fora de `±300s`, assinatura HMAC divergente, UTF-8 inválido ou nonce reutilizado (replay). |
| `AUTH_USER_REQUIRED` | `403 Forbidden` | Requisição autenticada com `X-AgroTracer-User-Id: 0` em rota restrita a usuários WordPress (`exigir_usuario_wordpress`). |
| `AUTH_SERVICE_UNAVAILABLE` | `503 Service Unavailable` | Segredo `AGROTRACER_BRIDGE_SECRET` ausente/inválido ou Redis indisponível (política *fail-closed*). |

---

## 4. Validação Integrada dos Headers Gerados pela Bridge PHP

Pacote assinado gerado por `AgroTracer_Bridge::build_signed_headers()` no WordPress (PHP 8.2.29) e validado contra `validar_headers_bridge()`, `verificar_hmac_requisicao()` e `exigir_usuario_wordpress()` do FastAPI (Python 3.14.7):

```json
{
    "Content-Type": "application/json",
    "X-AgroTracer-Signature": "75ff30bfcf8c437b26ae0f3ee554319cb8e131ab19bcaffcde294190159dada6",
    "X-AgroTracer-Timestamp": "1792020000",
    "X-AgroTracer-Nonce": "00112233445566778899aabbccddeeff",
    "X-AgroTracer-User-Id": "42",
    "X-Correlation-ID": "f2079c68-fbe4-4d92-9fb4-55daba0c666b",
    "User-Agent": "AgroTracer-Bridge/3.1.0 (WordPress)"
}
```

- **Formato `X-AgroTracer-Signature`:** `[0-9a-f]{64}` — Validado.
- **Formato `X-AgroTracer-Nonce`:** `[0-9a-f]{32}` (16 bytes CSPRNG via `bin2hex(random_bytes(16))`) — Validado.
- **Formato `X-AgroTracer-User-Id`:** `(0|[1-9][0-9]{0,19})` — Validado.
- **Formato `X-Correlation-ID`:** UUID v4 canônico de 36 caracteres minúsculos — Validado.
