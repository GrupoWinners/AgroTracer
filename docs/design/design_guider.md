# Guia de Design - AgroTracer

Este documento formaliza os Design Tokens e o Guia de Estilo a serem utilizados em toda a aplicação para garantir consistência visual.

## 1. Tokens de Cores (Color Palette)

As cores de feedback são essenciais para comunicar o estado do sistema ao utilizador de forma clara.

* **Sucesso (Success)**
  * Referência: Ações concluídas, guardadas com sucesso.
  * Token CSS: `--color-success: #22c55e;` (Verde)
  * Texto sobre a cor: Branco (`#ffffff`)

* **Erro (Error)**
  * Referência: Falhas, validações incorretas, ações destrutivas.
  * Token CSS: `--color-error: #ef4444;` (Vermelho)
  * Texto sobre a cor: Branco (`#ffffff`)

* **Atenção (Warning)**
  * Referência: Avisos, ações que requerem cuidado antes de prosseguir.
  * Token CSS: `--color-warning: #f59e0b;` (Amarelo/Laranja)
  * Texto sobre a cor: Preto (`#000000`) ou Cinzento Escuro (`#1f2937`)

* **Informação (Info)** *(Opcional, mas recomendado)*
  * Referência: Notas informativas, dicas.
  * Token CSS: `--color-info: #3b82f6;` (Azul)

## 2. Tokens de Tipografia (Typography)

A tipografia deve ser legível e hierárquica. (Sugestão: família de fontes *Inter* ou *Roboto*).

* **Família de Fontes:**
  * Token: `--font-family-base: 'Inter', sans-serif;`

* **Pesos (Font Weights):**
  * Normal: `400` (Textos corridos)
  * Médio: `500` (Botões e subtítulos)
  * Negrito: `700` (Títulos principais)

* **Tamanhos (Font Sizes):**
  * `--text-xs`: `0.75rem` (12px) - Notas de rodapé, pequenas etiquetas.
  * `--text-sm`: `0.875rem` (14px) - Dicas de formulários (hints).
  * `--text-base`: `1rem` (16px) - Texto padrão de parágrafos.
  * `--text-lg`: `1.25rem` (20px) - Subtítulos.
  * `--text-xl`: `1.5rem` (24px) - Títulos de secção.

  ## 3. Padrões de Interface e Formulários (Desktop)
- **Formulários:** Labels acima dos campos, asterisco (*) para obrigatórios e unidades visíveis (ex: `kg`, `ha`, `kg CO2e`)[cite: 18, 23].
- **Prevenção de Erros:** Botões de envio entram em estado de *loading* e ficam desabilitados no clique para evitar duplicidade (Idempotência)[cite: 18, 30].
- **Mensagens de Erro/Sucesso:** Exibidas em caixas de alerta ou Toast com o `Correlation ID` visível para suporte[cite: 18, 20].