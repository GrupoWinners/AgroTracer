# S6-T04 — QA Desktop (1366x768 e 1920x1080 em Chrome/Edge)

Responsável: João Vitor Santos de Souza
Área: QA / Front-end (Sprint 6)
Dependência: S6-T01
Critérios de Aceite:
- Homologar `1366x768` e `1920x1080` em Google Chrome e Microsoft Edge.
- Sem clipping/overflow crítico.
- Screenshots como evidência em `docs/evidencias/sprint-6/`.

## 1. Matriz Homologada (Headless CDP — 32/32 Checks)
- **Navegadores:** Google Chrome e Microsoft Edge.
- **Viewports:** `1366x768` e `1920x1080`.
- **Telas verificadas:** `dashboard`, `fazendas`, `lotes`, `animais`, `manejo`, `fechamento`, `certificados` e `publico` (`/certificado/`).
- **Critério automatizado de DOM/Layout:** `document.documentElement.scrollWidth <= window.innerWidth`, cards/cabeçalhos/botões sem recorte horizontal e verificação visual direta dos PNGs capturados.
- **Resultado após correções:** `32/32` combinações aprovadas com `docOverflow <= 0` e zero clipping crítico.

## 2. Defeitos Identificados e Corrigidos na Homologação
1. **Clipping/overflow horizontal nos KPIs de Manejo (`wordpress/agrotracer-bridge/assets/css/agrotracer-screens.css`):**
   - **Problema observado antes da correção:** Na tela `#screen-manejo`, os 4 cards KPI ultrapassavam o contêiner (`1343px > 1295px` em `1366x768` e `1410px > 1384px` em `1920x1080`), causando recorte lateral no último card (*Consistência da Timeline*).
   - **Correção:** Adição de `min-width: 0;` em `.agro-kpi-card` e layout vertical (`flex-direction: column; gap: 6px;`) para `#screen-manejo .agro-kpi-card`.
2. **Alinhamento de cabeçalhos de tela e ações (`wordpress/agrotracer-bridge/assets/css/agrotracer-screens.css`):**
   - **Problema observado antes da correção:** Ausência de regras para `.agro-screen-header` e `.agro-screen-header-actions` fazia botões de ação em `Manejo`, `Fechamento` e `Certificados` quebrarem desalinhados abaixo do subtítulo.
   - **Correção:** Definição de `.agro-screen-header` (`display: flex; flex-wrap: wrap; justify-content: space-between;`), `.agro-screen-header-left`, `.agro-screen-badge-container`, `.agro-screen-title`, `.agro-screen-subtitle` e `.agro-screen-header-actions` (`flex-shrink: 0;`).
3. **Navegação por hash no mesmo documento (`wordpress/agrotracer-bridge/assets/js/agrotracer-screens.js`):**
   - **Problema observado:** Alterações de hash (`#dashboard`, `#fazendas`, `#lotes`, `#manejo`, `#fechamento`, `#certificados`) e histórico do navegador não alternavam a tela ativa.
   - **Correção:** Extração de `applyHashScreen()` e registro de `window.addEventListener('hashchange', applyHashScreen);` em `init()`.

## 3. Evidências Visuais (Screenshots PNG)
Capturas salvas em `docs/evidencias/sprint-6/screenshots/`:
- **Chrome `1366x768`:** `chrome-1366x768-{dashboard,fazendas,lotes,animais,manejo,fechamento,certificados,publico}.png`
- **Chrome `1920x1080`:** `chrome-1920x1080-{dashboard,fazendas,lotes,animais,manejo,fechamento,certificados,publico}.png`
- **Edge `1366x768`:** `edge-1366x768-{dashboard,lotes,manejo,fechamento,certificados,publico}.png`
- **Edge `1920x1080`:** `edge-1920x1080-{dashboard,lotes,manejo,fechamento,certificados,publico}.png`
