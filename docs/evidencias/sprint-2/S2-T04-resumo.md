# S2-T04 — Páginas Lotes e Animais com filtros e status

## Entregas Realizadas

- **Navegação em Sub-abas (Lotes vs Inventário Geral do Rebanho)**:
  - Alternador ergonômico `#tab-btn-lotes` e `#tab-btn-animais` com contadores de registros atualizados.
- **Gestão de Lotes de Manejo (`templates/lots.php`)**:
  - Modal de cadastro de novo lote (`#modal-create-lot`) com validação inline e prevenção de código duplicado (`LOTE_CODIGO_DUPLICADO` - HTTP 409).
  - Listagem Master-Detail à esquerda com contagem de animais e badges semânticos de status (`Rascunho`, `Em manejo`, `Fechado`, `Certificado`, `Abatido`).
  - Filtros multifatoriais: busca textual por código, filtro por fazenda e filtro seletivo por status do lote.
  - Tabela de animais atualmente vinculados ao lote com brinco SISBOV, transponder RFID, categoria e data de associação.
  - Tabela histórica colapsável de associações encerradas (preservação histórica RN-06).
- **Inventário Individual do Rebanho (Animais)**:
  - Faixa de métricas rápidas (KPIs) com badges do Design System: total cadastrado (1.250), alocados em lotes (1.180), disponíveis para associação (70).
  - Modal de cadastro de animal (`#modal-create-animal`) com validação inline e tratamento de duplicidade (`ANIMAL_IDENTIFICADOR_DUPLICADO` - HTTP 409).
  - Filtros multifatoriais do rebanho: busca por SISBOV/RFID, categoria zootécnica, status de alocação, fazenda de origem e botão "Limpar Filtros".
  - Tabela completa de animais do rebanho com identificadores, categoria, status, lote ativo e ações contextuais.
- **Histórico Temporal do Animal (`#modal-animal-history`)**:
  - Modal de rastreabilidade temporal com linha do tempo gráfica (`.agro-timeline`) exibindo marcos cronológicos de associação, movimentação e cadastro (RN-06/RN-07).
- **Cuidado de Engenharia — Sem Dependência de Hover para Ações Importantes**:
  - Todas as ações críticas (`+ Novo Lote`, `+ Cadastrar Animal`, `+ Associar Animais`, `Ver Histórico`, `Desassociar`, `Editar Lote`, `+ Registrar Movimentação`, `Alocar em Lote`) possuem rótulo textual legível e contextualizado, visíveis imediatamente na interface sem qualquer necessidade de hover do mouse.
  - Regra CSS explícita `.agro-table-actions` e `.agro-btn-sm` com `visibility: visible !important;` e `opacity: 1 !important;`, assegurando acessibilidade para uso rural e em tablets/dispositivos touch de campo.
- **Design System Aplicado**:
  - Aderência estrita aos tokens oficiais de design (`tokens.json` e `agrotracer-screens.css`): paleta florestal (`--agro-primary: #1b4332`), superfícies neutras e feedback semântico (`agro-badge success/danger/warning/info/neutral`).
- **Bridge REST Controller & Proxy HMAC (`class-agrotracer-bridge.php`)**:
  - Endpoints WordPress REST adicionados: `POST/GET /agrotracer/v1/lotes` e `POST/GET /agrotracer/v1/animais`.
  - Encaminhamento com headers assinados HMAC via `AgroTracer_Http_Client`, com fallback controlado para preview offline.

## Qualidade e Testes

- **Testes Automatizados de Frontend e Contrato**:
  - 6 testes específicos da S2-T04 aprovados em 100%:
    - `test_templates_exist_and_contain_required_identifiers`
    - `test_design_system_and_semantic_badges_applied`
    - `test_important_actions_are_visible_without_hover_dependency`
    - `test_expected_domain_error_codes_are_defined_and_mapped`
    - `test_filter_controls_are_present_for_lots_and_animals`
    - `test_bridge_controller_has_sprint2_handlers`
  - 8 testes de regressão da suite de segurança HMAC aprovados em 100%.
- **Linter PHP 8.2**:
  - 12 arquivos PHP auditados via `php.exe -l` com 0 erros de sintaxe.

## Evidências

- `S2-T04-testes-frontend.txt`: log da execução da suíte de testes unitários e de regressão.
- `S2-T04-php-linter.txt`: log da validação estática de sintaxe PHP 8.2.29.
- `wordpress/agrotracer-bridge/tests/test-s2-t04-lotes-animais.php`: código-fonte da suíte de testes.

## Pendências

- Code review e aprovação do Tech Lead / P.O. (João Vitor).
- QA Gate da Nadiny Martins (S2-T06).
- Desbloqueio da tarefa S2-T05 (Timeline e formulários de associação e movimentação).
