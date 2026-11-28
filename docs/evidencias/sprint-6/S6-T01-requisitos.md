# S6-T01 — Revisão de Menus, Breadcrumbs, Estados e Design System

Responsável: João Vitor Santos de Souza
Área: Integração (Sprint 6)
Critérios de Aceite:
- Revisar menus, breadcrumbs e estados.
- Nenhum JSON cru ou link quebrado.
- Design system aplicado (`docs/design-system/tokens.json` e `docs/design/design_guide.md`).

## Escopo Implementado

### 1. Menus e Navegação (`header.php`, `page-agrotracer.php`, `dashboard.php`, `certificados.php`, `agrotracer-screens.js`)
- Ativação real da tela `Certificados` (`#screen-certificados` em `templates/certificados.php`), corrigindo o item morto `data-screen="certificados"` no menu superior e habilitando roteamento por hash (`#certificados`).
- Popovers interativos e acessíveis para notificações (`#agro-notifications-popover`) e menu do produtor (`#agro-user-dropdown`), com exibição do nome do usuário autenticado via WordPress (`wp_get_current_user()`).
- Correção de botões inativos ou com destino incorreto em `dashboard.php` (`Registrar abate` -> `openLotInFechamento(1)`, `Manejo` -> `manejo`, `Ver nova versão` -> `manejo`, `Emitir certificado` -> `openLotInFechamento(2)`, `Baixar PDF`/`Ver QR` -> `certificados`).

### 2. Breadcrumbs (`page-agrotracer.php`, `certificado-publico.php`, `agrotracer-screens.js`, `agrotracer-screens.css`)
- Implementação de `<nav id="agro-breadcrumb" class="agro-breadcrumb" aria-label="Breadcrumb">` atualizado dinamicamente em `updateBreadcrumb()` para todas as telas, sub-abas (`Lotes de Manejo` vs `Inventário do Rebanho`), fazendas e lotes selecionados.
- Inclusão de breadcrumb na página pública `/certificado/` (`AgroTracer / Consulta Pública de Certificado`).
- Substituição de links redundantes (`Voltar para Fazendas` em `farms.php` e `Visão Geral de Lotes` em `lots.php`) por retorno funcional ao Dashboard.

### 3. Estados Completos de UX e Zero JSON Cru / Link Quebrado
- Criação de `formatSafeUiError()` e `escapeHtml()` em `agrotracer-screens.js` para bloquear exibição de JSON bruto, SQL ou tracebacks em toasts e banners, somado à sanitização server-side de `AgroTracer_Http_Client::format_api_response()`.
- Correção de chamada `showToast()` em `setupManejoModule()` (parâmetro `correlationId` corrompido) e remoção do toast estático `#initial-demo-toast` no carregamento inicial.
- Substituição de `alert()` nativo em `setupAssociateDrawer()` pelo modal semântico `openValidationErrorModal()`.
- Inclusão de estados vazios ausentes (`#farms-empty-state`, `#paddocks-empty-state`, `#lots-empty-state`, `#certificados-empty-state`), estado de loading em `#certificados-loading-state` e feedback de carregamento na consulta pública (`certificado-publico.php`), além de atualização dinâmica dos KPIs/status de manejo e fechamento por lote.

### 4. Design System Aplicado (`agrotracer-screens.css`)
- Correção de `.agro-alert.info` (que utilizava `#f0fdf4` verde) para os tokens oficiais `info` (`--agro-info-bg`, `--agro-info-border`, `--agro-info-text`) de `docs/design-system/tokens.json`.
- Padronização de `.agro-alert.success`, `.agro-alert.danger`, `.agro-alert.warning`, `.agro-breadcrumb`, `.agro-header-popover` e `.agro-toast` semânticos com tokens do Design System.
