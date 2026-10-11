# 🎨 Guia de Design System e UI/UX - AgroTracer

Este documento formaliza as diretrizes de interface do utilizador, a arquitetura de informação e as regras de feedback para as telas desktop da plataforma AgroTracer.

## 1. Especificações de Viewport e Layout
- **Resoluções Suportadas:** Desktop 1366x768 e 1920x1080 (Navegadores: Google Chrome e Microsoft Edge).
- **Grid de Espaçamento:** Base proporcional em múltiplos de 8px (8px, 16px, 24px, 32px).
- **Arquitetura de Tela:** Menu lateral fixo (Verde Primário), cabeçalho de navegação contextual e área de trabalho sobre fundo neutro (`surface`).

## 2. Tipografia
- **Família Principal:** `Inter`, sans-serif.
- **Títulos (H1/H2):** Bold (700), tamanhos de 24px a 32px.
- **Subtítulos (H3/H4):** Semi-bold (600), tamanhos de 18px a 20px.
- **Corpo (Body):** Regular (400), 14px a 16px.
- **Tabelas / Legendas:** Regular (400), 12px a 13px.

## 3. Padrões de Interface e Regras de Formulário
- **Formulários:** Labels organizados acima dos campos, indicação clara de obrigatoriedade (*) e unidades visíveis explicitamente (ex: `kg`, `ha`, `kg CO2e`).
- **Estados de Feedback:**
  - **Sucesso (`success`):** Notificações e confirmações de ações efetuadas.
  - **Erro/Validação (`danger`):** Erros de preenchimento inline ou modais de bloqueio com mensagem orientadora.
  - **Atenção (`warning`):** Alertas de sobreposição temporal ou de pendências no lote.
- **Notificações:** Exibição de Toast no canto inferior da tela, contendo sempre o `Correlation ID` visível para suporte técnico.
- **Prevenção de Clique Duplo:** Botões de envio entram em estado de *loading* e ficam desabilitados durante a requisição, garantindo a idempotência.