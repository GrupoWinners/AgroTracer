# S5-T06 — Registro Oficial do QA Gate da Sprint 5

> **Épico:** `[EP-S5] Sprint 5 — Certificado PDF, QR e consulta pública`  
> **Task:** `S5-T06 — QA Gate da Sprint 5: Comparação Banco/API/PDF/QR, Leak Test (SEC-07), Clique Duplo (SEC-08) e BOLA`  
> **Custódia:** QA Lead — AgroTracer  
> **Dependências concluídas:** `S5-T01` (PR #40), `S5-T02` (PR #41), `S5-T03` (PR #39), `S5-T04` (PR #42), `S5-T05` (PR #43)  
> **Desbloqueia:** `S6-T01`, `S6-T02`  
> **Data:** 19/11/2026  
> **Resultado:** **APROVADO NO QA GATE DA SPRINT 5**

---

## 1. Matriz de Critérios de Aceite da Sprint 5

| Task | Entrega | Evidência Principal | Status |
|---|---|---|---|
| **S5-T01** | Emissão atômica do certificado com `Idempotency-Key` e token público opaco (sem persistência plaintext) | `S5-T01-pytest.txt`, `test_s5_t01_certificacao.py` | Aprovado |
| **S5-T02** | Download privado de PDF minimizado com hash persistido `X-PDF-SHA256` pós-geração e sem PII | `S5-T02-requisitos.md`, `S5-T02-certificado-demo.pdf`, `test_s5_t02_pdf.py` | Aprovado |
| **S5-T03** | Token opaco 256 bits (`secrets.token_urlsafe(32)`), lookup exclusivo via SHA-256 e rate limit distribuído (Redis) | `S5-T03-requisitos.md`, `S5-T03-pytest.txt`, `test_s5_t03_tokens.py` | Aprovado |
| **S5-T04** | Fechar/emitir certificado com retry seguro, bloqueio de clique duplo e download via WordPress Bridge | `S5-T04-requisitos.md`, `test-s5-t04-certificacao-download.php` | Aprovado |
| **S5-T05** | Página pública `/certificado/`, DTO minimizado (RN-13) com allowlist estrita e QR Code 100% local em SVG | `S5-T05-requisitos.md`, `test_s5_t05_publico.py`, `test-s5-t05-consulta-publica.php` | Aprovado |
| **S5-T06** | QA Gate: Comparação Banco/API/PDF/QR, Leak test (SEC-07), Clique duplo (SEC-08) e BOLA | `test_s5_t06_qa_gate.py`, `S5-T06-testes-qa-gate.txt`, este documento | Aprovado |

---

## 2. Escopo Técnico Auditado e Resultados das Verificações

### 2.1. Comparação Banco vs. API vs. PDF vs. QR (Consistência End-to-End)
- **API de Emissão (`POST /api/v1/lotes/{id}/certificar`):**
  - Retorna HTTP `201 Created` com `Cache-Control: no-store`.
  - Retorna o `token` opaco de 43 caracteres URL-safe **uma única vez**.
- **Banco de Dados (PostgreSQL / SQLite):**
  - Tabela `certificados`: persiste `snapshot_sha256`, `lote_id`, `status: VALIDO`.
  - Tabela `tokens_publicos`: armazena **exclusivamente** o `token_hash` (SHA-256). O token opaco original nunca é persistido em tabelas de auditoria, snapshot ou banco.
  - Tabela `certificados_pdf`: persiste os bytes do PDF e `pdf_sha256`.
- **PDF Privado (`GET /api/v1/certificados/{id}/pdf`):**
  - Contém versão do método (`CARBONENGINE-MVP-1.0`), versão dos parâmetros (`S4-DEMO-1`), rótulo `[SYNTHETIC]`, `snapshot_sha256` e unidades de emissão.
  - **Zero vazamento:** o `token` opaco e o `pdf_sha256` **não** constam no texto renderizado do PDF (anti-circularidade e conformidade com S5-T03).
- **QR Code Local & Consulta Pública (`GET /api/v1/certificados/publico?token=...`):**
  - O QR Code SVG é renderizado pelo front-end localmente em memória (`buildQrCodeSvg`), apontando para a URL pública `/certificado/?token=<token>`.
  - O DTO retornado na consulta pública bate com exatidão matemática os mesmos valores de emissão total, intensidade, versão de método, status e `snapshot_sha256` registrados no banco e no PDF.

### 2.2. Validação dos 3 Tokens (Critério de Aceite)
1. **Token Válido:** Retorna HTTP `200 OK` com `status: "VALIDO"`, DTO com resultados e unidades preservadas sem arredondamento.
2. **Token de Certificado Revogado:** Ao marcar o certificado como `REVOGADO`, a rota pública retorna HTTP `200 OK` com `status: "REVOGADO"`, mantendo integridade e rastreabilidade pública.
3. **Token Inexistente ou Malformado (RN-13):**
   - Testado contra tokens inexistentes de 43 caracteres, strings vazias, tokens curtos, tokens com caracteres especiais e payloads abusivos (>2000 chars).
   - Todos retornam invariavelmente HTTP `404 Not Found` com código `CERTIFICADO_NAO_ENCONTRADO` e mensagem padronizada `"Certificado nao encontrado."`.
   - **Prevenção de Timing Attack / Enumeração:** Requisições malformadas consomem rate limit igualmente no Redis antes de qualquer rejeição.

### 2.3. Leak Test do DTO Público (SEC-07)
- Foi injetada uma carga deliberada de dados confidenciais no snapshot de teste:
  - CPF (`123.456.789-00`) e CNPJ (`12.345.678/0001-90`)
  - E-mail (`produtor.confidencial@fazenda.com.br`) e telefone (`+55 34 99999-8888`)
  - Chaves privadas e API keys (`rsa-priv-secret-key-12345`, `secret-internal-api-key-99999`)
  - Notas internas de fiscalização
  - `source_uri` (`https://intranet.fazenda.example/privado/laudo.xlsx`)
  - Dados de propriedade (`CAR-MG-0001928374`, nome de fazenda, município e UF)
  - Hashes de controle interno (`token_hash`, `idempotency_hash`, `request_hash`, `wordpress_user_id`, `produtor_id`)
- **Resultado da Inspeção:** O DTO público serializado em JSON foi inspecionado integralmente. **Nenhum** dos dados confidenciais ou identificadores privados vazou no DTO público, respeitando a configuração Pydantic `extra="forbid"` e a allowlist de sanitização do WordPress Bridge.

### 2.4. Prevenção de Clique Duplo e Idempotência (SEC-08)
- **1ª Requisição (`Idempotency-Key: clique-duplo-gate`):** Sucesso (`201 Created`).
- **2ª Requisição Imediata (Clique Duplo):** Rejeitada com `409 Conflict`, código `CERTIFICACAO_JA_PROCESSADA`, sem duplicar registros no banco e sem reemitir token.
- **3ª Requisição (Mesma Chave com Payload Divergente):** Rejeitada com `409 Conflict`, código `IDEMPOTENCY_KEY_REUTILIZADA`.
- **4ª Requisição (Nova Chave em Lote Já Certificado):** Rejeitada com `409 Conflict`, código `CERTIFICADO_JA_EXISTENTE`.
- **Trava de Interface (JavaScript):**
  - Variáveis síncronas `isSubmitting = true` e `isDownloadingPdf = true` no script `agrotracer-screens.js`.
  - Desativação imediata dos botões de ação e exibição de spinners de carregamento no DOM.

### 2.5. Broken Object Level Authorization (BOLA) em Certificados
- **Tentativa de Acesso Cruzado entre Produtores:**
  - Usuário A emite certificado para seu lote.
  - Usuário B (`wordpress_user_id: 999`) tenta baixar o PDF do Produtor A via `GET /api/v1/certificados/{id_produtor_A}/pdf`.
  - Resposta: HTTP `404 CERTIFICADO_NAO_ENCONTRADO` (`"Certificado nao encontrado."`).
  - Comparado com ID inexistente (`99999`): retorna exatamente a mesma resposta HTTP `404`, impedindo ataques de enumeração horizontal de recursos.
  - Tentativa de certificar lote alheio (`POST /api/v1/lotes/{lote_produtor_A}/certificar`): retorna HTTP `404 LOTE_NAO_ENCONTRADO`.

### 2.6. Geração Local de QR Code e Segurança de Infraestrutura
- O arquivo `wordpress/agrotracer-bridge/assets/js/agrotracer-screens.js` implementa `buildQrCodeSvg` em JavaScript puro no navegador (ISO-18004, versões 1 a 10 com correção de erro nível M).
- Nenhuma chamada para APIs externas de QR Code (Google Charts, qrserver.com, quickchart, etc.) existe no código-fonte, eliminando o risco de interceptação do token público opaco por terceiros.

---

## 3. Verificações Executadas no QA Gate

- **Suíte de Testes da Sprint 5 (`pytest`):**
  - Comando: `python -m pytest tests/test_s5_t01_certificacao.py tests/test_s5_t02_pdf.py tests/test_s5_t03_tokens.py tests/test_s5_t05_publico.py tests/test_s5_t06_qa_gate.py -v`
  - Total: **42 passed in 1.66s** (0 falhas, 100% verde).
- **Suíte Combinada Sprint 4 + Sprint 5 (`pytest`):**
  - Total: **119 passed in 1.95s** (0 regressões).
- **Linter Python (`flake8`):**
  - Comando: `python -m flake8 backend/app backend/tests`
  - Resultado: **0 erros / 0 advertências de PEP 8**.
- **Validação de Sintaxe Frontend (Node.js):**
  - Comando: `node --check wordpress/agrotracer-bridge/assets/js/agrotracer-screens.js`
  - Resultado: **Sintaxe válida, sem erros**.
- **Bugs P1/P2 em Aberto:** **0** bloqueadores ou críticos relacionados ao fluxo de emissão, PDF, QR Code ou consulta pública.

---

## 4. Conclusão do QA Gate e Homologação

A **Sprint 5 (Certificado PDF, QR e Consulta Pública)** atende integralmente a todos os critérios de aceite:
- Emissão atômica e idempotente homologada com trava de clique duplo (SEC-08);
- 3 tokens testados e aprovados (válido, revogado e inexistente com RN-13);
- DTO público blindado sem vazamento de CPF/CNPJ, e-mail, telefone, chaves, notas internas ou metadados de infraestrutura (SEC-07);
- Proteção contra BOLA aprovada com resposta anti-enumeração;
- Geração local de QR Code validada;
- Todos os testes automatizados da camada backend e evidências anexadas em `docs/evidencias/sprint-5/`.

**Status Final:** **HOMOLOGADO E APROVADO NO QA GATE (SPRINT 5)**  
Desbloqueia formalmente as tarefas **S6-T01** e **S6-T02**.

---
*QA Lead — Equipe AgroTracer*
