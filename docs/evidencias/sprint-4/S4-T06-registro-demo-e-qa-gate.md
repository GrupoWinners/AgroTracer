# S4-T06 — Registro Oficial da Demo com Fator SYNTHETIC e QA Gate (Sprint 4)

> **Épico:** `[EP-S4] Sprint 4 — Fechamento e CarbonEngine`  
> **Task:** `S4-T06 — Demo do cálculo com fator SYNTHETIC rotulado e QA Gate da Sprint 4`  
> **Custódia:** Product Owner (João Vitor Santos de Souza) — Tarefa de equipe  
> **Dependências concluídas:** `S4-T01` (PR #33), `S4-T02` (PR #34), `S4-T03` (PR #35), `S4-T04` (PR #36), `S4-T05` (PR #37)  
> **Desbloqueia:** `S5-T03`  
> **Data:** 15/11/2026  
> **Resultado:** **APROVADO NO QA GATE DA SPRINT 4**

---

## 1. Matriz de Critérios de Aceite da Sprint 4

| Task | Entrega | Evidência Principal | Status |
|---|---|---|---|
| **S4-T01** | `CarbonEngine` puro com `Decimal` (`ctx.prec = 80`), dias inclusivos e fatores versionados | `backend/app/services/carbon_engine.py`, `S4-T01-metodo.md` | Aprovado |
| **S4-T02** | Pré-condições de fechamento (RN-04, RN-09, RN-10, RN-16, RN-19) e erro `422` sem `ZeroDivisionError` | `S4-T02-contrato.md`, `test_s4_t02_fechamento.py` | Aprovado |
| **S4-T03** | Snapshot imutável e transação atômica com triggers `DEFERRABLE` no PostgreSQL | `S4-T03-resumo.md`, `ADR S4-T01-T03`, `test_s4_t03_snapshot.py` | Aprovado |
| **S4-T04** | Tela de fechamento no WordPress com unidades claras, prevenção de clique duplo e erros acionáveis | `fechamento.php`, `S4-T04-resumo.md`, `ADR S4-T04` | Aprovado |
| **S4-T05** | Tabela de *expected results* versionada, 51 testes de casos limite e ADR de validade matemática vs. científica | `S4-T05-expected-results.md`, `ADR S4-T05`, `test_s4_t05_casos_limite.py` | Aprovado |
| **S4-T06** | Demo com fator `SYNTHETIC` rotulado, premissas/limitações explícitas e QA Gate | `fechamento.php`, `test_s4_t06_qa_gate.py`, este documento | Aprovado |

---

## 2. Roteiro da Demo do Cálculo com Fator `[SYNTHETIC]` Rotulado

### 2.1. Cenário de Referência Auditado (`CARBONENGINE-MVP-1.0`)
- **Conjunto de Parâmetros:** `DEMO-SYNTHETIC-2026-01` (`source_type: "SYNTHETIC"`, `source_uri: null`, `backend/examples/parametros_demo.json`).
- **Período 1 (Confinamento):** `2026-01-01` a `2026-03-31` (`90` dias inclusivos) × `50` cabeças × `2.10` kg CO2e/cab/dia = **`9.450` kg CO2e**.
- **Período 2 (Pastagem):** `2026-04-01` a `2026-05-30` (`60` dias inclusivos) × `50` cabeças × `1.40` kg CO2e/cab/dia = **`4.200` kg CO2e**.
- **Emissão Total Acumulada:** **`13.650` kg CO2e**.
- **Abate:** `50` cabeças × `540` kg peso vivo médio × `0.53` rendimento de carcaça = **`14.310` kg carcaça**.
- **Intensidade de Emissões:** `13.650 / 14.310` = `0.953878...` (**`0,954` kg CO2e / kg carcaça**).
- **Caso Negativo / Segurança Numérica:** Denominador zero (`0` animais abatidos, peso `0` ou rendimento `0`) retorna `None` em `calcular_intensidade` e HTTP `422` na camada de domínio, sem `ZeroDivisionError` e sem certificação.

### 2.2. Premissas e Limitações (Para a Banca — Sem Alegação Ambiental Exagerada)
1. **Validade Matemática vs. Validade Científica (`docs/adr/S4-T05-validade-matematica-vs-cientifica.md`):**
   - O `CarbonEngine` garante **validade matemática** (aritmética determinística em `Decimal` com 80 dígitos de precisão, sem `float` binário e sem arredondamento intermediário).
   - A **validade científica** depende exclusivamente da governança dos conjuntos de parâmetros versionados (`ParametroSet`/`Fator` com `source_type` e `source_uri` auditados).
2. **Rotulagem Explícita na Interface e nos Artefatos:**
   - Na tela de fechamento (`wordpress/agrotracer-bridge/templates/fechamento.php`), o conjunto exibe a badge `v1.0-2026 [SYNTHETIC]` e o painel de resultado exibe o aviso `#fechamento-aviso-sintetico` (`data-source-type="SYNTHETIC"`), informando que os valores não representam inventário oficial (IPCC/Embrapa), medição direta em campo ou certificação ambiental definitiva.
   - No `preview.html` e em `parametros_demo.json`, os fatores são explicitamente classificados como `SYNTHETIC` e didáticos.
3. **Escopo do MVP na Sprint 4:**
   - O fechamento persiste snapshot imutável e registra auditoria atômica, **sem emitir certificado PDF/QR** (escopo exclusivo da Sprint 5).
   - O contrato atual suporta exatamente um `parametro_set_id` por fechamento (`S4-T02-contrato.md`).

---

## 3. Verificações Executadas no QA Gate

- **Suíte Backend Sprint 4 + Proveniência (`pytest`):**
  - Comando: `python -m pytest -v tests/test_s4_t01_carbon_engine.py tests/test_s4_t02_fechamento.py tests/test_s4_t03_snapshot.py tests/test_s4_t05_casos_limite.py tests/test_s4_t06_qa_gate.py tests/test_s3_t06_demo.py`
  - Resultado: **82 passed in 0.84s** (0 falhas).
- **Linter Python (`flake8`):**
  - Comando: `python -m flake8 app tests`
  - Resultado: **0 violações** de estilo/PEP 8.
- **Bugs P1/P2 em Aberto:** **0** bloqueadores ou críticos relacionados à Sprint 4.

---

## 4. Conclusão do Gate

A **Sprint 4 (Fechamento e CarbonEngine)** atende aos critérios de aceite do Guia e à Definição de Pronto (DoD), com cálculo determinístico validado, casos limite cobertos, snapshot imutável implementado e rotulagem `SYNTHETIC` explícita sem alegações ambientais exageradas, desbloqueando a task **S5-T03**.

**João Vitor Santos de Souza**  
*Product Owner & Front-end Lead*
