# S1-T06 — Registro Oficial de Homologação da Demo e QA Gate (Sprint 1)

> **Épico:** `[EP-S1] Sprint 1 — Fundação de dados e identidade`  
> **Task:** `S1-T06 — Demo login -> fazenda -> talhão e QA Gate da Sprint`  
> **Custódia Técnica:** Product Owner (João Vitor) & QA Lead (Nadiny Martins)  
> **Data de Homologação:** 24 de Outubro de 2026  
> **Resultado:** 🟢 **APROVADO UNANIMEMENTE PELO QA GATE E P.O.**  
> **Condição de Release:** Autorizado o merge em `main` após este Gate.

---

## 1. 📋 Matriz de Critérios de Aceite da Sprint 1

| Critério de Aceite | Requisito / Guia v3.0 | Evidência Técnica | Status |
|---|---|---|:---:|
| **Identidade Server-Side** | Princípio 0.1 / RF-01 / RF-02 | `produtores.wordpress_user_id` sem senha em Python | ✅ Aprovado |
| **Modelagem & DDL** | RN-01, RN-02, RN-03 / S1-T01 | `Fazenda` (nome, mun, uf, CAR único), `Talhao` (identificador, ha) | ✅ Aprovado |
| **Integridade Histórica** | Seção 8.3 / R09 | `ON DELETE RESTRICT` em 100% das Chaves Estrangeiras | ✅ Aprovado |
| **Interface Desktop Rural** | S1-T03 / 5 Estados de UX | `farms.php`, `dashboard.php`, `preview.html`, toasts de Correlation ID | ✅ Aprovado |
| **Bridge HMAC-SHA256** | S1-T04 / ADR-002 | `class-agrotracer-http-client.php` com anti-replay e TTL 660s | ✅ Aprovado |
| **Matriz CRUD & BOLA** | S1-T05 / RF-03 / RF-04 | 4 testes cobrindo criação encadeada, unicidade e barreira 404 de BOLA | ✅ Aprovado |
| **Segurança Bridge (SEC-01 a SEC-04)** | S1-T05 / RNF-04 | 4 testes cobrindo adulteração HMAC, TTL expirado, replay e UserID=0 | ✅ Aprovado |
| **Regressão Zero** | DoD / Seção 16 | 41 testes automatizados passando; 0 falhas | ✅ Aprovado |
| **Bugs Bloqueadores** | DoD | Nenhum bug P1 (bloqueador) ou P2 (crítico) aberto | ✅ Aprovado |

---

## 2. 🎬 Roteiro Demonstrável da Demo Ponta a Ponta

O fluxo demonstrável da Sprint 1 integra os 3 componentes da arquitetura de referência:

```
[ Navegador Desktop ] 
         │ (1) Login WP & Sessão Segura
         ▼
[ WordPress / agrotracer-bridge ] 
         │ (2) Assinatura HMAC-SHA256 + Nonce + X-Correlation-ID + X-AgroTracer-User-Id
         ▼
[ FastAPI / Nucleo Python ] 
         │ (3) Validação Criptográfica + Autorização BOLA por Objeto
         ▼
[ PostgreSQL Relacional ]
         └── (4) Persistência com Constraints (UNIQUE, CHECK, RESTRICT) & Auditoria JSONB
```

### Passo a Passo Executável da Demo:
1. **Autenticação:** O produtor realiza login nativo no WordPress. A identidade (`wordpress_user_id = 42`) é preservada na sessão do servidor.
2. **Navegação no Dashboard (`S1-T03`):** O produtor visualiza seus KPIs consolidados (12 lotes ativos, 1.250 cabeças, 8 certificados) e a recomendação de próxima ação.
3. **Gestão de Fazendas (`S1-T03` / `S1-T04` / `S1-T02`):**
   * O produtor clica em `+ Nova Fazenda` e preenche Nome (`Fazenda Modelo`), Município (`Aquidauana`), UF (`MS`) e CAR (`MS-5401209-F38A89BC10D44A6890EF21AA4589CC10`).
   * O Bridge PHP assina a requisição `POST /api/v1/fazendas` com HMAC-SHA256 e propaga o `X-Correlation-ID`.
   * O FastAPI valida a assinatura, garante que o CAR não está em duplicidade (**RN-02**), persiste o registro com `produtor_id` associado e grava o evento em `auditoria_eventos`.
   * O front-end exibe o toast de sucesso com o identificador de correlação rastreável.
4. **Gestão de Talhões:**
   * Na mesma tela master-detail, o produtor seleciona a fazenda e adiciona os piquetes (`Piquete 01` com `25.5000 ha`).
   * A API valida a área estritamente positiva (**RN-03**), impede nomes duplicados na mesma fazenda e retorna `201 Created`.
5. **Cenário Negativo Demonstrado (Defesa BOLA):**
   * Tentativas de acesso ou cadastro de talhões em fazendas pertencentes a outro produtor são barradas com `404 Not Found`, impedindo enumeração e vazamento de metadados.

---

## 3. 🛡️ Resultados Oficiais da Suíte de Testes (QA Gate)

* **Total de Testes Executados:** 41 aprovados (1 pulado condicionalmente ao banco remoto).
* **Testes de Segurança da Bridge (SEC-01 a SEC-04):** 100% de sucesso.
* **Testes de Canonicalização e HMAC PHP × Python:** 100% de sucesso.
* **Testes de Integridade Estrutural e Modelos:** 100% de sucesso.
* **Flake8 / Linting:** 0 violações de PEP 8.
* **Classificação de Bugs em Aberto:**
  * P1 (Bloqueador): **0**
  * P2 (Crítico): **0**
  * P3 (Médio/Melhoria): **0**
  * P4 (Cosmético): **0**

---

## 4. 📝 Declaração Formal de Aprovação e Conclusão

Os signatários abaixo declaram que a **Sprint 1 (Fundação de Dados e Identidade)** atingiu 100% de sua Definição de Pronto (DoD), com critérios de aceite testados, evidências anexadas e arquitetura alinhada ao Guia v3.0.

Fica **AUTORIZADO** o merge formal das branches de integração da Sprint 1 na branch **`main`**, desbloqueando o início da **Sprint 2 (Lotes, Rebanho e Associação Temporal)**.

**João Vitor Santos de Souza**  
*Product Owner & Front-end Lead*  

**Nadiny Martins**  
*UI/UX & QA Lead*  

**Samela Maria**  
*Scrum Master & Back-end Lead*  
