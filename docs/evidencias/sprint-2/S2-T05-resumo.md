# Evidência de Engenharia — Sprint 2 — Task S2-T05

**Épico:** `[EP-S2] Sprint 2 — Animais, lotes e rastreabilidade temporal`  
**Task:** `[S2-T05] Timeline e formulários de associação e movimentação`  
**Desenvolvedor Front-End & Product Owner (P.O.):** João Vitor Santos de Souza (Losel / LoselSpt)  
**Validação e Homologação QA:** SubAgent QA (Agente de IA)  
**Data:** 30 de Outubro de 2026  
**Status DoD:** Concluído e Aprovado  

---

## 1. Escopo Técnico da Entrega

A Task **S2-T05** consolida o núcleo de rastreabilidade temporal e movimentações agropecuárias da plataforma AgroTracer no ecossistema WordPress (Plugin Bridge e UI Desktop Rural):

1. **Timeline Cronológica Visual de Movimentações:**
   - Componente visual `lot-movements-timeline-card` contextual dentro da visão de detalhes de Lotes de Manejo (`lots.php`).
   - Visão global em aba dedicada `view-timeline-container` com filtros combinados de busca, tipo de manejo e alvo (Lote vs Animal).
   - Componentes visuais estilizados segundo os tokens semânticos do Design System (`.agro-timeline`, `.agro-timeline-item`, `.agro-timeline-dot`, `.agro-timeline-route`).

2. **Formulário de Movimentação com Validação Estrita XOR (RN-07):**
   - Modal acessível `#modal-create-movement` com rádio exclusivo de seleção de alvo: Lote ou Animal Individual (regra XOR onde `(animal_id is None) != (lote_id is None)`).
   - Validação imediata de rota no cliente e no servidor: Talhão de Origem ≠ Talhão de Destino (`MOVIMENTACAO_ORIGEM_DESTINO_IGUAIS`), impedindo redundância de registro.
   - Validação cronológica temporal (`MOVIMENTACAO_FORA_DE_ORDEM`): impede que o produtor registre uma movimentação com timestamp retroativo anterior ao último evento registrado para o alvo.

3. **Cuidado Crítico de Engenharia — Identidade Segura sem Hidden Inputs:**
   - **Zero vazamento de identidade no DOM:** Nenhum formulário (`form-create-movement`, `form-disassociate-animal`, `form-create-lot`, `form-create-animal`, drawer de associação) expõe ou consome `<input type="hidden" name="user_id">` ou `<input type="hidden" name="produtor_id">`.
   - A identidade do produtor autenticado é estritamente resolvida no servidor através da sessão nativa do WordPress (`get_current_user_id()`) e injetada com assinatura criptográfica HMAC-SHA256 (`X-AgroTracer-User-ID`, `X-AgroTracer-Signature`) conforme a especificação **ADR-002**.

4. **Tratamento de Conflitos 409 Sem JSON Técnico:**
   - Neutralização total de vazamento de payloads JSON crus (`{"detail": ...}`, `{"error": ...}`, rastros de banco ou exceções do backend) na interface do produtor rural.
   - Exibição de modal amigável `#modal-validation-error` com título zootécnico claro, descrição orientadora do conflito, código formal do erro de domínio e `X-Correlation-ID` para rastreabilidade de suporte.

5. **Encerramento de Associação Temporal (RN-06):**
   - Modal `#modal-disassociate-animal` para encerramento de vínculo temporal entre animal e lote, preenchendo a data de desassociação e registrando o motivo zootécnico, preservando o histórico integral do rebanho sem deleção física no banco.

---

## 2. Critérios de Aceite e Matriz de Verificação

| Critério de Aceite | Implementação | Verificação Automatizada | Status |
| :--- | :--- | :--- | :---: |
| **1. Conflito sem JSON técnico** | Interceptação em `agrotracer-screens.js`, modal semântico `modal-validation-error` | `test_conflict_feedback_without_technical_json` | **APROVADO** |
| **2. Identidade NÃO vem de campo hidden** | Zero inputs hidden de `user_id`/`produtor_id`; identidade via `get_current_user_id()` e HMAC | `test_zero_hidden_identity_inputs_in_all_forms` | **APROVADO** |
| **3. Alvo XOR de movimentação** | Rádio exclusivo `#radio-target-lot` vs `#radio-target-animal`, alternância condicional no DOM | `test_movement_form_xor_target_and_route_validation` | **APROVADO** |
| **4. Rota origem ≠ destino** | Validação antes do dispatch com mensagem de erro amigável contextualizada | `test_movement_form_xor_target_and_route_validation` | **APROVADO** |
| **5. Timeline visual e rastreabilidade** | Card contextual em lotes e aba global de timeline com badges e setas de trajeto | `test_timeline_structure_and_visibility` | **APROVADO** |
| **6. Encerramento temporal RN-06** | Formulário de desassociação sem deleção física, preservação histórica completa | `test_temporal_association_closure_form_rn06` | **APROVADO** |
| **7. Endpoints Bridge e HMAC** | Handlers REST `handle_create_movement`, `handle_get_movements`, `handle_disassociate_animal` | `test_bridge_controller_movement_and_disassociation_handlers` | **APROVADO** |

---

## 3. Evidências de Testes Anexadas

- **Linter PHP (Sintaxe Limpa):** [`S2-T05-php-linter.txt`](file:///C:/Users/joaov/Programação/AgroTracer/AgroTracer/docs/evidencias/sprint-2/S2-T05-php-linter.txt)
- **Execução das Suítes Automatizadas:** [`S2-T05-testes-frontend.txt`](file:///C:/Users/joaov/Programação/AgroTracer/AgroTracer/docs/evidencias/sprint-2/S2-T05-testes-frontend.txt)
- **Suíte de Testes da Task:** [`test-s2-t05-timeline-movimentacao.php`](file:///C:/Users/joaov/Programação/AgroTracer/AgroTracer/wordpress/agrotracer-bridge/tests/test-s2-t05-timeline-movimentacao.php)

---

## 4. Declaração de Definição de Pronto (DoD)

- [x] Implementação versionada na branch `feature/S2-T05`.
- [x] Zero credenciais ou segredos em código cliente/templates.
- [x] Testes da camada passando 100% (6/6 na suíte da task e 6/6 na suíte de não-regressão da S2-T04).
- [x] Evidências anexadas no diretório oficial `docs/evidencias/sprint-2/`.
- [x] Erros esperados de negócio com códigos mapeados e tratados de forma amigável ao usuário.
- [x] Nenhum bug P1/P2 aberto relacionado à funcionalidade.
