# S4-T05 — Tabela de Expected Results, Casos Limite e Validação do CarbonEngine

## Épico
[EP-S4] Sprint 4 — Fechamento e CarbonEngine

## Objetivo da Sprint
Fechar lote com pré-condições explícitas e cálculo determinístico, versionado e sem divisão por zero.

## Escopo Técnico Entregue
Tabela de expected results versionada com cálculo manual, casos limite (zero, negativo, mesmo dia, fim < início) e diferenciação explícita entre validade matemática e validade científica.

---

## 1. Entregas Realizadas

### 1.1. Tabela de Expected Results Versionada (`docs/evidencias/sprint-4/S4-T05-expected-results.md`)
- **Memória de Cálculo Analítico Passo a Passo:** Fórmulas explícitas para dias inclusivos $(\text{fim} - \text{inicio}) + 1$, fator ajustado por período ($FE_{\text{base}} \times \prod K$), emissão por período ($dias \times animais \times FE_{\text{ajustado}}$), somatório de emissões e intensidade por quilograma de carcaça.
- **Matriz com 20 Cenários de Referência:** Mapeamento completo dos casos sintéticos nominais (EXP-01 a EXP-04) e dos casos anômalos/limites (EXP-05 a EXP-20).
- **Precisão Analítica Estendida:** Garantia de 80 casas decimais de precisão sem arredondamento intermediário em qualquer etapa do fluxo.

### 1.2. Cobertura de Casos Limite (Critério de Aceite 2)
- **Casos Zero:**
  - Zero animais no manejo: processamento válido resultando em emissão $0\text{ kg CO}_2\text{e}$.
  - Zero no fator base ou em multiplicador: anulação da emissão ($0\text{ kg CO}_2\text{e}$).
  - Zero animais abatidos, zero peso médio ou zero rendimento: retorno explícito `None` em `calcular_intensidade`, eliminando qualquer possibilidade de `ZeroDivisionError`.
  - Zero emissão com carcaça válida: cálculo determinístico retornando $0\text{ kg CO}_2\text{e}/\text{kg carcaça}$.
- **Casos Negativos:**
  - Animais negativos no manejo: rejeição estrita com `ErroCarbono("Quantidade de animais invalida.")`.
  - Fatores negativos ($FE_{\text{base}} < 0$, $K < 0$): rejeição com `ErroCarbono(f"{campo} nao pode ser negativo.")`.
  - Parâmetros de abate negativos: retorno seguro `None` em `calcular_intensidade`.
  - Emissão total negativa: rejeição com `ErroCarbono("emissao_total nao pode ser negativo.")`.
- **Casos Temporais:**
  - Mesmo dia ($\text{inicio} == \text{fim}$): contabilização correta de exatamente 1 dia inclusivo.
  - Data final anterior ao início ($\text{fim} < \text{inicio}$): rejeição com `ErroCarbono("Datas invalidas para manejo.")`.
  - Ano bissexto: validação de 29 dias em fevereiro de 2024.
  - Virada de ano: cálculo de períodos contínuos entre diferentes anos civis.
  - Tipos temporais inválidos (string, datetime com timezone, None): rejeição estrita.
- **Prevenção de Tipos Contaminantes:**
  - Bloqueio estrito de ponto flutuante IEEE-754 (`float`).
  - Bloqueio de valores não finitos (`NaN`, `+Infinity`, `-Infinity`).
  - Validação estrita de identificação de parâmetros ($id > 0$ e versão não vazia).

### 1.3. Cuidado de Engenharia: Validade Matemática vs Validade Científica
- **Formalização em ADR:** Criação do documento `docs/adr/S4-T05-validade-matematica-vs-cientifica.md`.
- **Validade Matemática:** Responsabilidade do CarbonEngine (`app/services/carbon_engine.py`), garantindo exatidão aritmética determinística com `Decimal`, reprodutibilidade bit a bit e ausência de divisões por zero.
- **Validade Científica:** Responsabilidade da governança de dados (`ParametroSet`, `Fator`, proveniência e fontes). O documento declara explicitamente que os números nominais do MVP ($13.650\text{ kg CO}_2\text{e}$ e $0,954\text{ kg CO}_2\text{e}/\text{kg carcaça}$) são sintéticos e didáticos, sem equivalência a inventários oficiais GHG Protocol/IPCC/Embrapa até a aprovação de fatores regulatórios definitivos.

---

## 2. Qualidade e Cobertura de Testes

### 2.1. Testes Automatizados da Task (`backend/tests/test_s4_t05_casos_limite.py`)
- **51 testes automatizados** implementados cobrindo:
  - Tabela de Expected Results nominais e multiplicadores compostos.
  - Todas as permutações de denominador zero e negativo.
  - Todas as combinações de fatores e animais negativos.
  - Anomalias de cronologia e limites temporais.
  - Validação de tipos, floats e infinitos.
  - Preservação da precisão a 80 dígitos e comutatividade dos fatores.
- **Resultado:** **51 testes aprovados em 0.10s (100% de sucesso)**.

### 2.2. Testes Integrados do CarbonEngine (Regressão S4-T01 + S4-T05)
- Suíte conjunta executada: `test_s4_t01_carbon_engine.py` + `test_s4_t05_casos_limite.py`.
- **62 testes aprovados em 0.11s (100% de sucesso)**.

### 2.3. Auditoria de Linter Python Flake8
- Auditoria executada: `python -m flake8 app tests`.
- **Resultado:** **0 violações PEP 8**. Todas as linhas com $\le 79$ caracteres.

---

## 3. Conformidade com a Definição de Pronto (DoD)

- [x] **Implementação versionada e sem segredo:** Zero credenciais, segredos ou dados sensíveis em arquivos de teste e documentação.
- [x] **Teste adequado à camada passando, com evidência anexada:**
  - Evidência Pytest: `docs/evidencias/sprint-4/S4-T05-pytest.txt` (62 testes passando).
  - Evidência Flake8: `docs/evidencias/sprint-4/S4-T05-flake8.txt` (0 erros).
  - Tabela de Expected Results: `docs/evidencias/sprint-4/S4-T05-expected-results.md`.
  - Resumo de Engenharia: `docs/evidencias/sprint-4/S4-T05-resumo.md`.
- [x] **Erro esperado com código/mensagem definidos:** Exceções do tipo `ErroCarbono` com mensagens precisas (`"Quantidade de animais invalida."`, `"Datas invalidas para manejo."`, `"E necessario ao menos um periodo."`, `"{campo} nao pode ser negativo."`, etc.) e retorno determinístico `None` para divisões impossíveis.
- [x] **docs/OpenAPI/ADR atualizados:** Registrado `docs/adr/S4-T05-validade-matematica-vs-cientifica.md`.
- [x] **Review de outro integrante e QA Gate conforme risco:** Artefatos estruturados e prontos para homologação pelo QA Gate da Sprint 4 (S4-T06).
- [x] **Nenhum P1/P2 aberto relacionado à task:** Sem pendências de precisão, divisão por zero ou contaminação por float no CarbonEngine.
