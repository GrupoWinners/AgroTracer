# S3-T04 — Tela de Timeline de Manejo Nutricional e Prevenção de Conflitos

## Épico
[EP-S3] Sprint 3 — Manejo nutricional e método de parâmetros

## Objetivo da Sprint
Implementar timeline sem sobreposição e preparar conjuntos de parâmetros versionados sem alegação científica indevida.

## Escopo Técnico Entregue
Tela de timeline de manejo com cadastro de períodos e mensagem de conflito que identifica explicitamente o período conflitante.

---

## 1. Entregas Realizadas

- **Tela de Manejo Nutricional (`templates/manejo.php`)**:
  - Container `#screen-manejo` integrado ao menu superior (`data-screen="manejo"`).
  - Seletor de lote de manejo (`#select-manejo-lote`) com atualização dinâmica de métricas e status do lote.
  - Alerta metodológico de transparência científica (ADR S3-T02 / S3-T06): fatores identificados como `SYNTHETIC` (didáticos), prevenindo alegações científicas indevidas no MVP.
  - Ação principal de criação `+ Novo Período de Manejo` (`#btn-open-create-manejo-modal`) visível sem qualquer dependência de hover.

- **Timeline Contínua Sem Sobreposição (RN-08)**:
  - Renderização cronológica vertical de cada período alimentar do lote (`.agro-timeline`).
  - **Datas claras**: início e fim formatados em DD/MM/AAAA, indicação explícita de dias inclusivos acumulados.
  - **Unidades zootécnicas claras**:
    - Consumo Diário de Matéria Seca (CMS): `kg MS/cab/dia`
    - Conversão de Metano Entérico (Ym): `% EB`
    - Fator de Emissão Entérica: `kg CH4/cab/ano`
  - Vínculo auditável ao conjunto de parâmetros versionado (`v1.0-2026`).

- **Identificação do Período Conflitante & Prevenção de Clique Inválido**:
  - Validação em tempo real no formulário (`#modal-manejo-conflict-box`):
    - Conforme o usuário informa as datas, o sistema detecta sobreposição com períodos já cadastrados no lote (`inicio_a <= fim_b && inicio_b <= fim_a`).
    - Exibe mensagem com o período exato colidente: *"O período selecionado colide diretamente com o manejo já cadastrado de 01/11/2026 a 10/11/2026 (Pastagem)."*
    - Desabilita imediatamente o botão de salvar (`#btn-submit-create-manejo.disabled = true`), cumprindo o BDD de feedback e tolerância a falhas.
  - Banner de erro na interface principal (`#manejo-conflict-banner`):
    - Acionado em caso de erro HTTP 409 (`MANEJO_SOBREPOSTO`) retornado pela API.
    - Exibe o código do erro, correlation_id e destaca o card do período conflitante na timeline.

- **Estados de UX Completos (Cuidado de Engenharia)**:
  - **Estado Vazio (`#manejo-empty-state`)**: quando o lote não possui manejos cadastrados, com orientação clara e botão `+ Cadastrar Primeiro Manejo`.
  - **Estado de Carregamento (`#manejo-loading-state`)**: indicador animado (spinner) durante consultas assíncronas.
  - **Estado de Conflito**: feedback semântico imediato tanto no modal quanto na tela principal.
  - **Estado de Sucesso**: toast notification com ID de correlação (`X-Correlation-ID`) e inclusão reativa do novo período na timeline.

- **Endpoints e Integração Bridge REST HMAC**:
  - `POST /agrotracer/v1/manejos`: encaminha requisição assinada via HMAC-SHA256 para `POST /api/v1/lotes/{lote_id}/manejos` com fallback controlado para preview offline.
  - `GET /agrotracer/v1/manejos`: consulta os manejos cronológicos do lote via `GET /api/v1/lotes/{lote_id}/manejos`.
  - `GET /agrotracer/v1/parametros`: disponibiliza catálogo de parâmetros versionados com proveniência explícita.
  - No backend FastAPI (`backend/app/api/v1/manejos.py`), adicionada rota `GET /{lote_id}/manejos` ordenada cronologicamente e resposta enriquecida no erro 409 contendo detalhes do período conflitante.

---

## 2. Qualidade e Cobertura de Testes

- **Testes de Frontend e Contrato WordPress (`test-s3-t04-timeline-manejo.php`)**:
  - `test_templates_exist_and_contain_required_identifiers`: **APROVADO**
  - `test_conflict_identification_components_and_error_message`: **APROVADO**
  - `test_units_and_dates_clarity_and_scientific_transparency`: **APROVADO**
  - `test_complete_ux_states_present`: **APROVADO**
  - `test_bridge_controller_has_sprint3_handlers`: **APROVADO**
  - Total: 5 testes aprovados em 1.78 ms.

- **Testes de Regressão de Segurança HMAC (`test-agrotracer-http-client.php`)**:
  - 8 testes aprovados em 0.76 ms, 72 asserções sem falhas.

- **Testes de Regressão da Sprint 2 (`test-s2-t04-lotes-animais.php`)**:
  - 6 testes aprovados em 3.00 ms.

- **Testes Backend FastAPI (`test_s3_t04_api.py` + `test_s3_t03_api.py`)**:
  - 19 testes aprovados (100% de sucesso).
  - Cobertura: listagem cronológica, autorização por objeto / IDOR (404), identificação do período conflitante no 409, auditoria atômica e contratos HMAC.

- **Auditoria de Linter PHP 8.2 e Python Flake8**:
  - 17 arquivos PHP verificados via `php -l`: 0 erros de sintaxe.
  - Código Python verificado via `flake8`: 0 violações PEP8.

---

## 3. Conformidade com a Definição de Pronto (DoD)

- [x] **Implementação versionada e sem segredo**: Nenhum segredo em código; credenciais respeitam `.env` e constantes de teste.
- [x] **Testes adequados à camada passando**: Suíte PHP e Pytest executadas com 100% de sucesso.
- [x] **Evidências anexadas em `docs/evidencias/sprint-3/`**:
  - `S3-T04-testes-frontend.txt`
  - `S3-T04-php-linter.txt`
  - `S3-T04-pytest.txt`
  - `S3-T04-resumo.md`
- [x] **Erro esperado com código/mensagem definidos**: `MANEJO_SOBREPOSTO` (HTTP 409) com identificação do período conflitante.
- [x] **docs/ADR atualizados**: Criado `docs/adr/S3-T04-timeline-manejo.md`.
- [x] **Nenhum P1/P2 aberto**: Código limpo, cirúrgico e aderente à diretriz `otimizacao-diff-e-tokens`.
