# S0-T06 — Registro de Evidência: Compatibilidade HMAC-SHA256 e Normalização RFC 3986 (PHP WordPress ↔ Python FastAPI)

- **Projeto:** AgroTracer
- **Sprint:** 0 / Integração Sprint 1
- **Tasks Relacionadas:** `S0-T06` (`feature/PY-06`) e `S1-T03` (`feature/WP-03-fazendas-ui`)
- **Referência Arquitetural:** ADR-002 — Autenticação e Segurança da Bridge
- **Equipe (Grupo Winners):** DEV Front-end & PO: João Vitor | Back-End & Scrum: Samela Maria | QA & UI: Nadiny Martins
- **Data da Execução:** 16/10/2026
- **Status:** ✅ 100% COMPATÍVEL E HOMOLOGADO

---

## 1. Validação do Vetor de Teste Oficial (HMAC-SHA256)

O vetor de teste compartilhado entre o backend Python (`test_vetor_hmac_compartilhado` em `backend/tests/test_hmac_protocol.py`) e o plugin WordPress (`AgroTracer_Bridge::build_canonical_string` / `AgroTracer_Bridge::generate_hmac_signature` em `wordpress/agrotracer-bridge/includes/class-agrotracer-bridge.php`) foi executado no runtime **PHP 8.2.29 (x64)** e **Python 3**.

### Parâmetros de Entrada
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

### Canonical String Gerada
```text
POST
/api/v1/fazendas
1792020000
00112233445566778899aabbccddeeff
42
44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
```

### Resultado Comparativo da Assinatura
- **Python (`hmac_protocol.gerar_assinatura`):** `ca62dbbd01854e311b419ff2e64d3721e0ccb6bf698ebcf94f9026e5d562c9bc`
- **PHP (`AgroTracer_Bridge::generate_hmac_signature`):** `ca62dbbd01854e311b419ff2e64d3721e0ccb6bf698ebcf94f9026e5d562c9bc`
- **Resultado:** `MATCH EXATO (100%)`

---

## 2. Vetores de Teste de Casos Especiais de Normalização (`PATH_WITH_QUERY` — RFC 3986)

Para garantir paridade absoluta com `normalizar_path_query()` do Python (`parse_qsl(..., keep_blank_values=True)` + `urlencode(..., quote_via=quote, safe="")`), a camada PHP implementa `AgroTracer_Bridge::normalize_path_query()` utilizando `explode('&')`, `urldecode()`, ordenação alfabética estável (`usort` preservando ordem relativa de chegada para chaves repetidas, idêntico ao Timsort do Python) e `rawurlencode()` (RFC 3986).

| Caso de Teste | Entrada (`path_with_query`) | Saída PHP (`normalize_path_query`) | Saída Python (`normalizar_path_query`) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. Sem query string** | `/api/v1/fazendas` | `/api/v1/fazendas` | `/api/v1/fazendas` | ✅ Match |
| **2. Espaços (`+` e `%20`)** | `/api/v1/fazendas?status=ativo&nome=Fazenda+Azul` | `/api/v1/fazendas?nome=Fazenda%20Azul&status=ativo` | `/api/v1/fazendas?nome=Fazenda%20Azul&status=ativo` | ✅ Match |
| **3. Acentos UTF-8** | `/api/v1/fazendas?uf=MS&municipio=Corumb%C3%A1&busca=S%C3%A3o%20Bento` | `/api/v1/fazendas?busca=S%C3%A3o%20Bento&municipio=Corumb%C3%A1&uf=MS` | `/api/v1/fazendas?busca=S%C3%A3o%20Bento&municipio=Corumb%C3%A1&uf=MS` | ✅ Match |
| **4. Chaves repetidas** | `/api/v1/fazendas?tag=b&tag=a&status=ativo` | `/api/v1/fazendas?status=ativo&tag=b&tag=a` | `/api/v1/fazendas?status=ativo&tag=b&tag=a` | ✅ Match |
| **5. Valor em branco** | `/api/v1/fazendas?vazio=&outro=1` | `/api/v1/fazendas?outro=1&vazio=` | `/api/v1/fazendas?outro=1&vazio=` | ✅ Match |
| **6. Caracteres RFC 3986** | `/api/v1/fazendas?filtro=a/b~c_d-e.f*g` | `/api/v1/fazendas?filtro=a%2Fb~c_d-e.f%2Ag` | `/api/v1/fazendas?filtro=a%2Fb~c_d-e.f%2Ag` | ✅ Match |
| **7. Path percent-encoded** | `/api/v1/fazendas%20teste?b=2&a=1` | `/api/v1/fazendas%20teste?a=1&b=2` | `/api/v1/fazendas%20teste?a=1&b=2` | ✅ Match |

---

## 3. Validação Integrada dos Headers e Envelope de Erro (ADR-002)

Pacote gerado por `AgroTracer_Bridge::build_signed_headers()` no WordPress e validado contra `validar_headers_bridge()` e `verificar_hmac_requisicao()` do FastAPI:

```json
{
    "Content-Type": "application/json",
    "X-AgroTracer-Signature": "237c4da0f0e121483b795492c91393971b4887583810e8357e7ee41e320be65f",
    "X-AgroTracer-Timestamp": "1792204402",
    "X-AgroTracer-Nonce": "6a4a14915ca23129825337e6a55d435f",
    "X-AgroTracer-User-Id": "42",
    "X-Correlation-ID": "f2079c68-fbe4-4d92-9fb4-55daba0c666b",
    "User-Agent": "AgroTracer-Bridge/3.1.0 (WordPress)"
}
```

- **Formato `X-AgroTracer-Signature`:** `[0-9a-f]{64}` — Validado.
- **Formato `X-AgroTracer-Nonce`:** `[0-9a-f]{32}` (16 bytes CSPRNG via `bin2hex(random_bytes(16))`) — Validado.
- **Formato `X-AgroTracer-User-Id`:** `(0|[1-9][0-9]{0,19})` — Validado.
- **Formato `X-Correlation-ID`:** UUID v4 canônico de 36 caracteres minúsculos — Validado.
- **Códigos do Envelope de Erro Confirmados:** `AUTH_INVALID_REQUEST` (HTTP 401) e `AUTH_SERVICE_UNAVAILABLE` (HTTP 503).
