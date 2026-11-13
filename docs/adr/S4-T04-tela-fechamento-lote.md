# ADR — S4-T04: Tela de Fechamento de Lote, Prevenção de Submissão Dupla e Erros Acionáveis

## Status

Implementado, validado por suíte automatizada e pronto para revisão por pares e QA Gate (S4-T05).

## Contexto

A conclusão do ciclo zootécnico de um lote bovino para abate exige a consolidação dos dados de manejo pelo motor determinístico **CarbonEngine** (S4-T01), a validação rigorosa de pré-condições temporais e integridade de animais (S4-T02 / RN-09 e RN-10) e a persistência de um snapshot histórico imutável protegido por triggers no PostgreSQL (S4-T03 / RN-11 e RN-21).

Por se tratar de uma operação irreversível com impacto direto na certificação de pegada de carbono, o produtor rural necessita de uma interface intuitiva, segura e com tolerância a falhas operacionais:
1. Campos com unidades explícitas e pré-visualização zootécnica em tempo real.
2. Garantia absoluta contra submissões acidentais duplicadas (prevenção de duplo clique / duplo submit).
3. Respostas de erro acionáveis, orientando exatamente como resolver eventuais inconsistências em vez de mensagens genéricas.

## Decisões Arquiteturais

1. **Tela Dedicada e Modal de Confirmação (`templates/fechamento.php` e `templates/modals.php`)**:
   - Criação da tela principal `#screen-fechamento` integrada à barra de navegação desktop (`data-screen="fechamento"`) e botão de ação rápida acessível a partir da visão detalhada de lotes.
   - Apresentação de checklist visual das pré-condições de fechamento (status `EM_MANEJO`, manejo nutricional contínuo, ausência de lacunas temporais, parâmetros publicados).
   - Diálogo modal de confirmação (`#modal-confirm-fechamento`) antes da submissão definitiva, detalhando a massa total de carcaça estimada e ressaltando a imutabilidade do registro.

2. **Campos e Unidades Zootécnicas Claras (Critério de Aceite 1)**:
   - **Data de Abate:** Campo de data em formato ISO (AAAA-MM-DD), com indicação explícita da data mínima permitida (igual ou posterior ao encerramento do último período de manejo).
   - **Quantidade de Animais Abatidos:** Entrada numérica inteira com unidade clara `cabeças (cab)` e indicação do limite máximo comprovado no último manejo.
   - **Peso Médio de Abate:** Entrada com duas casas decimais e unidade `kg / cabeça (kg vivo)`.
   - **Rendimento de Carcaça (RC):** Entrada percentual com unidade `%` (ex: `53,00%`), acompanhada da fração decimal correspondente (`0.53`) transmitida ao backend sem float.
   - **Cálculo de Pré-visualização:** Exibição dinâmica em tempo real do peso total vivo e da massa de carcaça estimada:
     $$\text{Carcaca}_{\text{total}} = \text{Animais} \times \text{Peso} \times (\text{Rendimento} / 100)$$

3. **Prevenção Estrita de Dupla Submissão (Critério de Aceite 3 & Cuidado de Engenharia)**:
   - Implementação de trava dupla no front-end: flag booleana síncrona `isSubmitting = true` combinada com desabilitação imediata dos botões de ação (`btnSubmit.disabled = true; btnDoConfirm.disabled = true;`).
   - Feedback visual imediato com spinner animado (`.agro-spinner`) e alteração do texto do botão para *"Processando cálculo e fechamento..."*.
   - Tratamento de ciclo de vida: restauração controlada do estado e reabilitação dos botões exclusivamente caso o backend retorne erro ou haja falha de rede.

4. **Tratamento Acionável de Erros de Domínio (Critério de Aceite 2)**:
   - Banner semântico destacado (`#fechamento-actionable-error-banner`) com código técnico, explicação clara e botão de resolução direta:
     - `ABATE_SUPERIOR_AOS_ANIMAIS` (422): instrui o ajuste da quantidade e oferece botão de auto-correção para o total do lote.
     - `ABATE_ANTERIOR_AO_MANEJO` (422): indica que o abate não pode preceder o manejo e oferece botão para preencher a data final do manejo.
     - `ASSOCIACOES_PARCIAIS` (422): explica a regra RN-09/10 e direciona o usuário para a tela de **Manejo** para particionar o período conforme as movimentações.
     - `MANEJO_OBRIGATORIO` (422): orienta que lotes sem histórico nutricional não podem ser fechados e oferece atalho para cadastro.
     - `LOTE_JA_FECHADO` (409): informa a imutabilidade do fechamento histórico com exibição direta do card de resultados.

5. **Integração Bridge REST HMAC WordPress**:
   - Criação da rota `POST /agrotracer/v1/fechamentos` (e `/agrotracer/v1/lotes/{lote_id}/fechamento`).
   - Encaminhamento com headers assinados `X-AgroTracer-Signature` (HMAC-SHA256) via `AgroTracer_Http_Client`.
   - Propagação íntegra de status codes HTTP (201, 404, 409, 422, 503) e envelopes de erro enriquecidos com Correlation ID.

## Consequências

- Eliminação completa de chamadas duplicadas no fechamento, protegendo o banco contra concorrência e garantindo a atomicidade exigida na RN-21.
- O usuário produtor compreende com exatidão as grandezas físicas informadas e, em caso de erro, recebe o caminho de correção em apenas um clique.
- A equipe de QA (Nadiny Martins) dispõe de um fluxo coeso e auditável para homologação no QA Gate da Sprint 4 (S4-T05).
