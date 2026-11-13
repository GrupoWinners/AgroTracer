# S4-T04 — Tela de Fechamento de Lote, Prevenção de Dupla Submissão e Erros Acionáveis

## Épico
[EP-S4] Sprint 4 — Fechamento e CarbonEngine

## Objetivo da Sprint
Fechar lote com pré-condições explícitas e cálculo determinístico, versionado e sem divisão por zero.

## Escopo Técnico Entregue
Tela de fechamento/abate com resumo, unidades e confirmação; prevenção de clique duplo; erro acionável.

---

## 1. Entregas Realizadas

### 1.1. Tela de Fechamento de Lote (`templates/fechamento.php`)
- **Container da Tela (`#screen-fechamento`):** Integrado à barra de navegação superior (`data-screen="fechamento"`).
- **Acesso Rápido na Tela de Lotes:** Botão `Fechar Lote` (`#btn-open-fechamento-from-lot`) visível no cabeçalho de detalhe do lote, permitindo transição direta com seleção automática.
- **Seletor Reativo de Lotes (`#select-fechamento-lote`):** Alternância instantânea de lote com recarregamento dos dados de manejo, checklist de pré-condições e status do lote.
- **Painel de Resumo do Lote (`#resumo-lote-codigo`):** Exibe código, fazenda, animais comprovados no último manejo, datas do período zootécnico e conjunto versionado.
- **Aviso de Irreversibilidade:** Destaque semântico para as regras RN-11 e RN-21, informando a geração de snapshot imutável no PostgreSQL e bloqueio de novos manejos.

### 1.2. Campos e Unidades Claras (Critério de Aceite 1)
- **Data do Abate (`#fechamento-data-abate`):** Input tipo date em formato ISO (`AAAA-MM-DD`), acompanhado da indicação explícita da data mínima permitida (conclusão do último período de manejo).
- **Animais Abatidos (`#fechamento-animais-abate`):** Input numérico inteiro acompanhado da unidade `cabeças (cab)` e indicação do limite máximo do lote.
- **Peso Médio de Abate (`#fechamento-peso-medio`):** Input numérico decimal com unidade `kg / cabeça (kg vivo)`.
- **Rendimento de Carcaça (`#fechamento-rendimento`):** Input percentual com unidade `%` e exibição dinâmica da fração decimal (`0.53`) enviada à API.
- **Pré-visualização Zootécnica Dinâmica:** Atualização instantânea ao digitar:
  - Peso Total Vivo em quilogramas (`kg`).
  - Massa Total de Carcaça estimada (`kg carcaça`).
- **Métricas Finais no Resultado:** Exibição com unidades regulatórias:
  - Emissão Total: `kg CO₂e`.
  - Intensidade de Emissões: `kg CO₂e / kg carcaça`.

### 1.3. Prevenção de Duplo Clique / Dupla Submissão (Critério de Aceite 3 & Cuidado de Engenharia)
- **Trava Síncrona via JavaScript:** Flag booleana `isSubmitting = true` no módulo, rejeitando cliques repetidos ou submissões via tecla Enter durante a requisição.
- **Desabilitação Imediata do Botão:**
  - Botão `#btn-submit-fechamento` desabilitado imediatamente no primeiro clique (`disabled = true`).
  - Exibição de spinner animado (`.agro-spinner`).
  - Alteração do texto para *"Processando cálculo e fechamento..."*.
- **Modal de Confirmação (`#modal-confirm-fechamento`):** Apresenta resumo dos dados de abate antes da persistência definitiva, com bloqueio similar no botão de confirmação (`#btn-execute-confirm-fechamento`).
- **Estilos CSS:** Regra `.agro-btn:disabled` aplicando opacidade reduzida, cursor `not-allowed` e `pointer-events: none`.

### 1.4. Tratamento Acionável de Erros de Domínio (Critério de Aceite 2)
- **Banner Semântico (`#fechamento-actionable-error-banner`):** Caixa de destaque visual com código de erro, mensagem técnica e container de orientação acionável:
  - `ABATE_SUPERIOR_AOS_ANIMAIS` (HTTP 422): Orienta que a quantidade abatida excede os animais do manejo e fornece botão para ajustar automaticamente o campo para o limite do lote.
  - `ABATE_ANTERIOR_AO_MANEJO` (HTTP 422): Alerta que a data de abate é anterior ao fim do manejo e oferece botão para preencher a data final do manejo.
  - `ASSOCIACOES_PARCIAIS` (HTTP 422): Explica a regra RN-09/10 (mudança de animais durante o período) e oferece botão para navegar diretamente à tela de **Manejo** para particionar o período.
  - `MANEJO_OBRIGATORIO` (HTTP 422): Informa que o lote não possui períodos cadastrados e redireciona para a tela de Manejo.
  - `LOTE_JA_FECHADO` (HTTP 409): Esclarece a imutabilidade do fechamento histórico e exibe o card de resultados consolidado.

### 1.5. Endpoints e Integração Bridge REST HMAC WordPress
- Registro dos endpoints REST oficiais:
  - `POST /agrotracer/v1/fechamentos`
  - `POST /agrotracer/v1/lotes/{lote_id}/fechamento`
  - `GET /agrotracer/v1/fechamentos`
- Despacho assinado HMAC-SHA256 (`X-AgroTracer-Signature`) via `AgroTracer_Http_Client::post()` para `POST /api/v1/lotes/{lote_id}/fechamento`.
- Propagação íntegra de Correlation ID e códigos de erro.
- Fallback determinístico para preview offline garantindo resultados idênticos ao motor oficial (13.650 kg CO₂e e 0,954 kg CO₂e/kg carcaça).

---

## 2. Qualidade e Cobertura de Testes

### 2.1. Testes de Frontend e Contrato WordPress (`test-s4-t04-fechamento-tela.php`)
- `test_templates_and_screen_structure_exist`: **APROVADO**
- `test_fields_and_units_clarity`: **APROVADO**
- `test_actionable_error_components_and_guidance`: **APROVADO**
- `test_double_submission_prevention_engineering`: **APROVADO**
- `test_bridge_controller_has_sprint4_fechamento_handlers`: **APROVADO**
- **Resultado:** **5 testes aprovados em 3.81 ms (100% de sucesso)**.

### 2.2. Testes de Regressão de Segurança HMAC (`test-agrotracer-http-client.php`)
- 8 testes aprovados em 0.75 ms, 72 asserções sem falhas (**100% de sucesso**).

### 2.3. Testes de Regressão das Sprints Anteriores
- `test-s3-t04-timeline-manejo.php`: 5 testes aprovados (**100% de sucesso**).
- `test-s2-t04-lotes-animais.php`: 6 testes aprovados (**100% de sucesso**).

### 2.4. Testes Backend Pytest (FastAPI / CarbonEngine)
- 28 testes aprovados em 0.97s cobrindo `test_s4_t01_carbon_engine.py`, `test_s4_t02_fechamento.py` e `test_s4_t03_snapshot.py` (**100% de sucesso**).

### 2.5. Auditoria de Linter PHP 8.2 e Python Flake8
- 19 arquivos PHP auditados via `php -l`: **0 erros de sintaxe**.
- Código Python auditado via `flake8`: **0 violações PEP8**.

---

## 3. Conformidade com a Definição de Pronto (DoD)

- [x] **Implementação versionada e sem segredo:** Zero credenciais ou segredos em código cliente/templates.
- [x] **Testes adequados à camada passando:** 100% da suíte frontend e de regressão executada com sucesso.
- [x] **Evidências anexadas em `docs/evidencias/sprint-4/`:**
  - `S4-T04-testes-frontend.txt`
  - `S4-T04-php-linter.txt`
  - `S4-T04-pytest.txt`
  - `S4-T04-resumo.md`
- [x] **Erro esperado com código/mensagem definidos:** Códigos `ABATE_SUPERIOR_AOS_ANIMAIS`, `ABATE_ANTERIOR_AO_MANEJO`, `ASSOCIACOES_PARCIAIS`, `MANEJO_OBRIGATORIO`, `LOTE_JA_FECHADO` com orientação acionável.
- [x] **docs/ADR atualizados:** Criado `docs/adr/S4-T04-tela-fechamento-lote.md`.
- [x] **Nenhum P1/P2 aberto relacionado à task:** Código enxuto, testado e aderente ao padrão de governança.
