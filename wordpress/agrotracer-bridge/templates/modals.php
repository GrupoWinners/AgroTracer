<?php
/**
 * AgroTracer Modals Template (Sprint 2 - Task S2-T04 / S2-T05)
 * Modais Obrigatórios:
 * 1. Erro de Validação de Domínio (Conflito 409 sem JSON técnico)
 * 2. Confirmação Crítica / Destrutiva (Desassociação e Exclusão)
 * 3. Cadastro de Novo Lote de Manejo (RN-04)
 * 4. Cadastro de Novo Animal (RN-05)
 * 5. Histórico Temporal do Animal (Rastreabilidade Completa RN-06 / RN-07)
 * 6. Formulário de Registro de Movimentação XOR (RN-07 / ADR-003) - S2-T05
 * 7. Formulário de Encerramento de Associação Temporal (RN-06) - S2-T05
 *
 * Cuidado de Engenharia S2-T05: Identidade NÃO vem de hidden fields (zero input hidden de user_id/produtor_id).
 */
if (!defined('ABSPATH')) {
    // Direct access security fallback
}
?>

<!-- 1. MODAL: ERRO DE VALIDAÇÃO (CONFLITO DE ASSOCIAÇÃO TEMPORAL 409 SEM JSON TÉCNICO) -->
<div id="modal-validation-error" class="agro-modal-backdrop" role="dialog" aria-labelledby="val-modal-title" aria-modal="true">
  <div class="agro-modal">
    <div class="agro-modal-header">
      <div class="agro-modal-header-left">
        <div class="agro-modal-icon-badge danger">
          <svg viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12" stroke="#ffffff" stroke-width="2.5"></line>
            <circle cx="12" cy="16" r="1.2" fill="#ffffff"></circle>
          </svg>
        </div>
        <h3 id="val-modal-title" class="agro-modal-title">Conflito de Regra de Negócio</h3>
      </div>
      <button type="button" id="btn-close-validation-modal" class="agro-drawer-close" aria-label="Fechar Modal">&times;</button>
    </div>

    <div class="agro-modal-body">
      <p style="font-weight: 600; color: var(--agro-text-primary); margin: 0 0 6px 0;" id="val-modal-headline">
        Não foi possível completar a associação temporal.
      </p>
      <p style="margin: 0; color: var(--agro-text-secondary);" id="val-modal-description">
        Alguns animais selecionados já possuem vínculo ativo com outro lote. Conforme a regra de rastreabilidade temporal (RN-06), um animal só pode pertencer a um lote por período.
      </p>

      <div class="agro-modal-conflict-box" id="val-modal-conflict-box">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
        </svg>
        <div>
          <strong id="val-modal-conflict-code">Código do Conflito: ANIMAL_JA_ASSOCIADO_CONFLITO (HTTP 409)</strong>
          <span id="val-modal-conflict-detail">Animal <strong>BR-123456790-1</strong> já está ativo no lote LT-2026-003.</span>
        </div>
      </div>
    </div>

    <div class="agro-modal-footer">
      <button type="button" id="btn-understand-validation" class="agro-btn agro-btn-primary">
        Entendi e Desmarcar Conflitos
      </button>
    </div>
  </div>
</div>

<!-- 2. MODAL: CONFIRMAÇÃO DE AÇÃO CRÍTICA / DESTRUTIVA -->
<div id="modal-confirm-action" class="agro-modal-backdrop" role="dialog" aria-labelledby="confirm-modal-title" aria-modal="true">
  <div class="agro-modal">
    <div class="agro-modal-header">
      <div class="agro-modal-header-left">
        <div class="agro-modal-icon-badge warning">
          <svg viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
          </svg>
        </div>
        <h3 id="confirm-modal-title" class="agro-modal-title">Confirmar Operação</h3>
      </div>
      <button type="button" class="agro-drawer-close" id="btn-close-confirm-modal" aria-label="Fechar Modal">&times;</button>
    </div>

    <div class="agro-modal-body">
      <p id="confirm-modal-text" style="margin: 0; color: var(--agro-text-secondary); line-height: 1.5;">
        Tem certeza que deseja prosseguir com esta operação?
      </p>
    </div>

    <div class="agro-modal-footer">
      <button type="button" id="btn-cancel-confirm" class="agro-btn agro-btn-secondary">
        Cancelar
      </button>
      <button type="button" id="btn-confirm-action" class="agro-btn agro-btn-danger">
        Confirmar
      </button>
    </div>
  </div>
</div>

<!-- 3. MODAL: CADASTRO DE NOVO LOTE (TASK S2-T04 / RN-04) - SEM HIDDEN FIELD DE IDENTIDADE -->
<div id="modal-create-lot" class="agro-modal-backdrop" role="dialog" aria-labelledby="create-lot-modal-title" aria-modal="true">
  <div class="agro-modal" style="max-width: 520px;">
    <div class="agro-modal-header">
      <div class="agro-modal-header-left">
        <div class="agro-modal-icon-badge success" style="background-color: var(--agro-primary); color: #ffffff;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;">
            <circle cx="12" cy="11" r="5"></circle>
          </svg>
        </div>
        <h3 id="create-lot-modal-title" class="agro-modal-title">Criar Novo Lote de Manejo</h3>
      </div>
      <button type="button" id="btn-close-create-lot-modal" class="agro-drawer-close" aria-label="Fechar Modal">&times;</button>
    </div>

    <form id="form-create-lot" onsubmit="return false;">
      <div class="agro-modal-body">
        <p style="margin: 0 0 16px 0; color: var(--agro-text-secondary); font-size: 13px;">
          Cadastre um lote para rastrear animais e associar manejos nutricionais. O lote será iniciado como <strong>Rascunho</strong> ou <strong>Em manejo</strong>.
        </p>

        <!-- Código do Lote -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="new-lot-code">
            Código do Lote <span style="color:#ef4444;">*</span>
          </label>
          <input type="text" id="new-lot-code" class="agro-input" placeholder="Ex: LT-2026-005" required autocomplete="off">
          <span class="agro-form-hint">Identificador interno único do lote na propriedade.</span>
          <div id="error-lot-code" class="agro-form-error" style="display:none; color:#dc2626; font-size:12px; margin-top:4px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;display:inline-block;vertical-align:-2px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            <span id="error-lot-code-msg">Código já cadastrado (LOTE_CODIGO_DUPLICADO).</span>
          </div>
        </div>

        <!-- Fazenda -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="new-lot-farm-id">
            Fazenda de Manejo <span style="color:#ef4444;">*</span>
          </label>
          <select id="new-lot-farm-id" class="agro-input" required>
            <option value="1" selected>Fazenda Modelo (Aquidauana/MS)</option>
            <option value="2">Fazenda São Bento (Corumbá/MS)</option>
            <option value="3">Fazenda Boa Vista (Miranda/MS)</option>
            <option value="4">Fazenda Estrela do Sul (Bodoquena/MS)</option>
          </select>
        </div>

        <!-- Fase / Finalidade Zootécnica -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="new-lot-purpose">
            Finalidade Zootécnica / Sistema
          </label>
          <select id="new-lot-purpose" class="agro-input">
            <option value="Engorda Intensiva a Pasto" selected>Engorda Intensiva a Pasto</option>
            <option value="Recria com Suplementação">Recria com Suplementação</option>
            <option value="Cria e Reprodução">Cria e Reprodução</option>
            <option value="Confinamento / Terminação">Confinamento / Terminação</option>
          </select>
        </div>

        <!-- Data de Abertura / Entrada -->
        <div class="agro-form-group" style="margin-bottom: 6px;">
          <label class="agro-form-label" for="new-lot-entry-date">
            Data de Abertura do Lote
          </label>
          <input type="date" id="new-lot-entry-date" class="agro-input" value="2026-10-30">
        </div>
      </div>

      <div class="agro-modal-footer">
        <button type="button" id="btn-cancel-create-lot" class="agro-btn agro-btn-secondary">
          Cancelar
        </button>
        <button type="submit" id="btn-submit-create-lot" class="agro-btn agro-btn-primary">
          <span class="btn-text">Salvar Lote</span>
          <span class="agro-spinner" style="display:none; margin-left:6px;"></span>
        </button>
      </div>
    </form>
  </div>
</div>

<!-- 4. MODAL: CADASTRO DE NOVO ANIMAL (TASK S2-T04 / RN-05) - SEM HIDDEN FIELD DE IDENTIDADE -->
<div id="modal-create-animal" class="agro-modal-backdrop" role="dialog" aria-labelledby="create-animal-modal-title" aria-modal="true">
  <div class="agro-modal" style="max-width: 520px;">
    <div class="agro-modal-header">
      <div class="agro-modal-header-left">
        <div class="agro-modal-icon-badge success" style="background-color: var(--agro-primary); color: #ffffff;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
        </div>
        <h3 id="create-animal-modal-title" class="agro-modal-title">Cadastrar Animal no Rebanho</h3>
      </div>
      <button type="button" id="btn-close-create-animal-modal" class="agro-drawer-close" aria-label="Fechar Modal">&times;</button>
    </div>

    <form id="form-create-animal" onsubmit="return false;">
      <div class="agro-modal-body">
        <p style="margin: 0 0 16px 0; color: var(--agro-text-secondary); font-size: 13px;">
          O animal é cadastrado individualmente com identificação oficial (SISBOV/Brinco) e vínculo temporal independente (RN-05 e ADR-003).
        </p>

        <!-- Identificador Oficial SISBOV -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="new-animal-identifier">
            Identificador Único / Brinco (SISBOV) <span style="color:#ef4444;">*</span>
          </label>
          <input type="text" id="new-animal-identifier" class="agro-input" placeholder="Ex: BR-123456805-2" required autocomplete="off">
          <span class="agro-form-hint">Formato canônico nacional oficial do rebanho.</span>
          <div id="error-animal-identifier" class="agro-form-error" style="display:none; color:#dc2626; font-size:12px; margin-top:4px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;display:inline-block;vertical-align:-2px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            <span id="error-animal-identifier-msg">Identificador já cadastrado (ANIMAL_IDENTIFICADOR_DUPLICADO).</span>
          </div>
        </div>

        <!-- Chip RFID Opcional -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="new-animal-rfid">
            Chip Eletrônico / Transponder RFID (Opcional)
          </label>
          <input type="text" id="new-animal-rfid" class="agro-input" placeholder="Ex: 982000365892105 (15 dígitos)" maxlength="15" autocomplete="off">
          <span class="agro-form-hint">Número ISO 11784/11785 de bastão leitor eletrônico.</span>
        </div>

        <!-- Categoria Zootécnica -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="new-animal-category">
            Categoria Zootécnica <span style="color:#ef4444;">*</span>
          </label>
          <select id="new-animal-category" class="agro-input" required>
            <option value="Bovino Macho" selected>Bovino Macho</option>
            <option value="Bovino Fêmea">Bovino Fêmea</option>
            <option value="Bezerro(a)">Bezerro(a)</option>
            <option value="Novilho(a)">Novilho(a)</option>
            <option value="Touro Reprodutor">Touro Reprodutor</option>
            <option value="Matriz / Vaca">Matriz / Vaca</option>
          </select>
        </div>

        <!-- Data de Nascimento Estimada -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="new-animal-birthdate">
            Data de Nascimento Estimada
          </label>
          <input type="date" id="new-animal-birthdate" class="agro-input" value="2023-04-15">
        </div>

        <!-- Fazenda de Origem -->
        <div class="agro-form-group" style="margin-bottom: 6px;">
          <label class="agro-form-label" for="new-animal-farm">
            Propriedade de Origem
          </label>
          <select id="new-animal-farm" class="agro-input">
            <option value="Fazenda Modelo" selected>Fazenda Modelo (Aquidauana/MS)</option>
            <option value="Fazenda São Bento">Fazenda São Bento (Corumbá/MS)</option>
            <option value="Fazenda Boa Vista">Fazenda Boa Vista (Miranda/MS)</option>
          </select>
        </div>
      </div>

      <div class="agro-modal-footer">
        <button type="button" id="btn-cancel-create-animal" class="agro-btn agro-btn-secondary">
          Cancelar
        </button>
        <button type="submit" id="btn-submit-create-animal" class="agro-btn agro-btn-primary">
          <span class="btn-text">Salvar Animal</span>
          <span class="agro-spinner" style="display:none; margin-left:6px;"></span>
        </button>
      </div>
    </form>
  </div>
</div>

<!-- 5. MODAL: HISTÓRICO TEMPORAL DO ANIMAL (TASK S2-T04 / RN-06 / RN-07) -->
<div id="modal-animal-history" class="agro-modal-backdrop" role="dialog" aria-labelledby="history-modal-title" aria-modal="true">
  <div class="agro-modal" style="max-width: 600px;">
    <div class="agro-modal-header">
      <div class="agro-modal-header-left">
        <div class="agro-modal-icon-badge" style="background-color: var(--agro-info-bg); color: var(--agro-info-text);">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <div>
          <h3 id="history-modal-title" class="agro-modal-title">Histórico Temporal do Animal</h3>
          <p id="history-modal-subtitle" style="font-size: 12px; color: var(--agro-text-muted); margin: 0;">BR-123456789-0 · Bovino Macho</p>
        </div>
      </div>
      <button type="button" id="btn-close-animal-history-modal" class="agro-drawer-close" aria-label="Fechar Modal">&times;</button>
    </div>

    <div class="agro-modal-body">
      <!-- Card Resumo de Status Atual do Animal -->
      <div style="background-color:#f8fafc; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:12px 16px; margin-bottom:18px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-size:11px; color:var(--agro-text-muted); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Status Temporal</div>
          <div style="margin-top:3px;" id="history-current-status-badge">
            <span class="agro-badge info" style="font-size:11.5px;">Ativo no Lote LT-2026-001</span>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:11px; color:var(--agro-text-muted); font-weight:600;">Chip RFID</div>
          <div style="font-family:monospace; font-size:13px; color:var(--agro-text-primary);" id="history-current-rfid">982000365892101</div>
        </div>
      </div>

      <!-- Timeline Cronológica -->
      <h4 style="font-size:13px; font-weight:700; color:var(--agro-text-primary); margin:0 0 12px 0;">Linha do Tempo de Manejo & Associações</h4>
      
      <div class="agro-timeline" id="animal-history-timeline-container">
        <!-- Itens populados dinamicamente via JS -->
      </div>
    </div>

    <div class="agro-modal-footer">
      <button type="button" id="btn-close-history-footer" class="agro-btn agro-btn-primary">
        Concluído
      </button>
    </div>
  </div>
</div>

<!-- =========================================================================
     6. MODAL: REGISTRAR MOVIMENTAÇÃO COM ALVO XOR E CRONOLOGIA (TASK S2-T05 / RN-07)
     CUIDADO CRÍTICO: IDENTIDADE NÃO VEM DE HIDDEN FIELD (ZERO USER_ID HIDDEN)
     ========================================================================= -->
<div id="modal-create-movement" class="agro-modal-backdrop" role="dialog" aria-labelledby="movement-modal-title" aria-modal="true">
  <div class="agro-modal" style="max-width: 580px;">
    <div class="agro-modal-header">
      <div class="agro-modal-header-left">
        <div class="agro-modal-icon-badge" style="background-color: #dbeafe; color: #1e40af;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;">
            <polyline points="17 1 21 5 17 9"></polyline>
            <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
            <polyline points="7 23 3 19 7 15"></polyline>
            <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
          </svg>
        </div>
        <div>
          <h3 id="movement-modal-title" class="agro-modal-title">Registrar Movimentação de Manejo</h3>
          <p style="font-size:12px; color:var(--agro-text-muted); margin:0;">Regra RN-07: Alvo exclusivo (XOR), trajeto e ordem cronológica</p>
        </div>
      </div>
      <button type="button" id="btn-close-movement-modal" class="agro-drawer-close" aria-label="Fechar Modal">&times;</button>
    </div>

    <!-- FORMULÁRIO SEM NENHUM CAMPO HIDDEN DE IDENTIDADE (CUIDADO DE ENGENHARIA S2-T05) -->
    <form id="form-create-movement" onsubmit="return false;">
      <div class="agro-modal-body">

        <!-- SELETOR DE ALVO EXCLUSIVO XOR (LOTE OU ANIMAL) -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" style="font-weight:700;">
            Tipo de Alvo da Movimentação (Regra XOR) <span style="color:#ef4444;">*</span>
          </label>
          <div style="display:flex; gap:16px; margin-top:6px; padding:8px 12px; background-color:#f8fafc; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md);">
            <label style="display:flex; align-items:center; gap:8px; cursor:pointer; font-size:13.5px; font-weight:600; color:var(--agro-text-primary);">
              <input type="radio" name="movement_target_type" id="radio-target-lot" value="lote" checked class="agro-radio">
              <span>Lote de Manejo Completo</span>
            </label>
            <label style="display:flex; align-items:center; gap:8px; cursor:pointer; font-size:13.5px; font-weight:600; color:var(--agro-text-primary);">
              <input type="radio" name="movement_target_type" id="radio-target-animal" value="animal" class="agro-radio">
              <span>Animal Individual</span>
            </label>
          </div>
          <span class="agro-form-hint">A movimentação zootécnica é aplicada estritamente a um lote ou a um animal individual.</span>
        </div>

        <!-- Alvo: Lote Selecionável (XOR) -->
        <div class="agro-form-group" id="group-movement-lot" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="movement-select-lot">
            Selecionar Lote de Manejo <span style="color:#ef4444;">*</span>
          </label>
          <select id="movement-select-lot" class="agro-input">
            <option value="1" data-code="LT-2026-001" selected>LT-2026-001 (Fazenda Modelo · 50 animais)</option>
            <option value="2" data-code="LT-2026-003">LT-2026-003 (Fazenda São Bento · 100 animais)</option>
            <option value="3" data-code="LT-2025-090">LT-2025-090 (Fazenda Boa Vista · 75 animais)</option>
          </select>
        </div>

        <!-- Alvo: Animal Selecionável (XOR) -->
        <div class="agro-form-group" id="group-movement-animal" style="margin-bottom: 14px; display:none;">
          <label class="agro-form-label" for="movement-select-animal">
            Selecionar Animal do Rebanho <span style="color:#ef4444;">*</span>
          </label>
          <select id="movement-select-animal" class="agro-input" disabled>
            <option value="1" data-id="BR-123456789-0">BR-123456789-0 (Bovino Macho · Lote LT-2026-001)</option>
            <option value="2" data-id="BR-123456790-1">BR-123456790-1 (Bovino Fêmea · Lote LT-2026-001)</option>
            <option value="3" data-id="BR-123456791-2">BR-123456791-2 (Bovino Macho · Lote LT-2026-001)</option>
            <option value="4" data-id="BR-123456800-7">BR-123456800-7 (Bovino Macho · Disponível)</option>
          </select>
        </div>

        <!-- Tipo de Movimentação -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="movement-type">
            Tipo de Movimentação / Manejo <span style="color:#ef4444;">*</span>
          </label>
          <select id="movement-type" class="agro-input" required>
            <option value="ROTACAO_PIQUETE" selected>Rotação de Pastagem / Piquete</option>
            <option value="TRANSFERENCIA_PASTAGEM">Transferência entre Pastagens</option>
            <option value="CONFINAMENTO">Entrada em Confinamento / Terminação</option>
            <option value="PESAGEM">Manejo de Pesagem e Triagem</option>
            <option value="TRATAMENTO_SANITARIO">Vacinação / Manejo Sanitário</option>
          </select>
        </div>

        <!-- Origem e Destino de Talhão/Piquete (Validação Origem != Destino) -->
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:14px;">
          <div class="agro-form-group">
            <label class="agro-form-label" for="movement-origin-paddock">
              Talhão de Origem <span style="color:#ef4444;">*</span>
            </label>
            <select id="movement-origin-paddock" class="agro-input" required>
              <option value="01" selected>Piquete 01 (Braquiária)</option>
              <option value="02">Piquete 02 (Mombaça)</option>
              <option value="03">Piquete 03 (Andropogon)</option>
              <option value="04">Piquete 04 (Tifton 85)</option>
            </select>
          </div>

          <div class="agro-form-group">
            <label class="agro-form-label" for="movement-dest-paddock">
              Talhão de Destino <span style="color:#ef4444;">*</span>
            </label>
            <select id="movement-dest-paddock" class="agro-input" required>
              <option value="02" selected>Piquete 02 (Mombaça)</option>
              <option value="01">Piquete 01 (Braquiária)</option>
              <option value="03">Piquete 03 (Andropogon)</option>
              <option value="04">Piquete 04 (Tifton 85)</option>
            </select>
          </div>
        </div>

        <!-- Feedback de Erro Amigável de Trajeto (Sem JSON) -->
        <div id="error-movement-route" class="agro-form-error" style="display:none; color:#dc2626; font-size:12.5px; background-color:#fee2e2; border:1px solid #fecaca; border-radius:var(--agro-radius-sm); padding:8px 12px; margin-bottom:14px;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;display:inline-block;vertical-align:-2px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <span id="error-movement-route-msg">Origem e destino não podem ser iguais (Regra RN-07).</span>
        </div>

        <!-- Data e Hora com Validação Cronológica RN-07 -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="movement-datetime">
            Data e Hora do Evento <span style="color:#ef4444;">*</span>
          </label>
          <input type="datetime-local" id="movement-datetime" class="agro-input" required>
          <span class="agro-form-hint">A movimentação deve respeitar a ordem cronológica do histórico do alvo.</span>
          
          <!-- Feedback de Conflito Cronológico 409 sem JSON Técnico -->
          <div id="error-movement-date" class="agro-form-error" style="display:none; color:#991b1b; font-size:12.5px; background-color:#fee2e2; border:1px solid #fecaca; border-radius:var(--agro-radius-sm); padding:8px 12px; margin-top:6px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;display:inline-block;vertical-align:-2px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            <span id="error-movement-date-msg">A data informada é anterior à última movimentação registrada (MOVIMENTACAO_FORA_DE_ORDEM).</span>
          </div>
        </div>

        <!-- Observações de Campo -->
        <div class="agro-form-group" style="margin-bottom: 6px;">
          <label class="agro-form-label" for="movement-notes">
            Observações de Campo (Opcional)
          </label>
          <textarea id="movement-notes" class="agro-input" rows="2" maxlength="500" placeholder="Ex: Pastagem vedada há 40 dias; animais com boa taxa de ganho médio diário."></textarea>
        </div>

      </div>

      <div class="agro-modal-footer">
        <button type="button" id="btn-cancel-create-movement" class="agro-btn agro-btn-secondary">
          Cancelar
        </button>
        <button type="submit" id="btn-submit-create-movement" class="agro-btn agro-btn-primary">
          <span class="btn-text">Confirmar Movimentação</span>
          <span class="agro-spinner" style="display:none; margin-left:6px;"></span>
        </button>
      </div>
    </form>
  </div>
</div>

<!-- =========================================================================
     7. MODAL: ENCERRAMENTO DE ASSOCIAÇÃO TEMPORAL (TASK S2-T05 / RN-06)
     CUIDADO CRÍTICO: IDENTIDADE NÃO VEM DE HIDDEN FIELD
     ========================================================================= -->
<div id="modal-disassociate-animal" class="agro-modal-backdrop" role="dialog" aria-labelledby="disassociate-modal-title" aria-modal="true">
  <div class="agro-modal" style="max-width: 520px;">
    <div class="agro-modal-header">
      <div class="agro-modal-header-left">
        <div class="agro-modal-icon-badge danger" style="background-color: #fee2e2; color: #991b1b;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        </div>
        <div>
          <h3 id="disassociate-modal-title" class="agro-modal-title">Encerrar Associação Temporal</h3>
          <p style="font-size:12px; color:var(--agro-text-muted); margin:0;">Regra RN-06: Preservação histórica sem exclusão física</p>
        </div>
      </div>
      <button type="button" id="btn-close-disassociate-modal" class="agro-drawer-close" aria-label="Fechar Modal">&times;</button>
    </div>

    <!-- FORMULÁRIO SEM CAMPOS HIDDEN DE USUÁRIO/PRODUTOR -->
    <form id="form-disassociate-animal" onsubmit="return false;">
      <div class="agro-modal-body">
        
        <!-- Cartão de Contexto do Vínculo a ser Encerrado -->
        <div style="background-color:#f8fafc; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:12px 16px; margin-bottom:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:11px; text-transform:uppercase; color:var(--agro-text-muted); font-weight:700;">Animal Alvo</div>
              <strong id="disassociate-modal-animal-id" style="font-size:15px; color:var(--agro-text-primary);">BR-123456789-0</strong>
            </div>
            <div style="text-align:right;">
              <div style="font-size:11px; text-transform:uppercase; color:var(--agro-text-muted); font-weight:700;">Lote Atual</div>
              <span id="disassociate-modal-lot-code" class="agro-badge info" style="font-size:11px;">LT-2026-001</span>
            </div>
          </div>
          <div style="margin-top:8px; font-size:12px; color:var(--agro-text-secondary);" id="disassociate-modal-period-text">
            Associado desde 20/06/2026 10:24 (72 dias de permanência regular).
          </div>
        </div>

        <!-- Motivo do Encerramento -->
        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="disassociate-reason">
            Motivo do Encerramento <span style="color:#ef4444;">*</span>
          </label>
          <select id="disassociate-reason" class="agro-input" required>
            <option value="TRANSFERENCIA" selected>Transferência para outro lote de manejo</option>
            <option value="CONCLUSAO_CICLO">Conclusão regular do ciclo zootécnico</option>
            <option value="PESAGEM_CLASSIFICACAO">Reclassificação em pesagem periódica</option>
            <option value="DESTINACAO_ABATE">Destinação para abate / Frigorífico</option>
            <option value="TRATAMENTO_ISOLADO">Encaminhamento para quarentena sanitária</option>
          </select>
        </div>

        <!-- Data do Encerramento Temporal -->
        <div class="agro-form-group" style="margin-bottom: 12px;">
          <label class="agro-form-label" for="disassociate-datetime">
            Data e Hora do Encerramento <span style="color:#ef4444;">*</span>
          </label>
          <input type="datetime-local" id="disassociate-datetime" class="agro-input" required>
          <span class="agro-form-hint">O horário é registrado transacionalmente no campo <code>desassociado_em</code>.</span>
        </div>

        <div style="background-color:#eff6ff; border:1px solid #bfdbfe; border-radius:var(--agro-radius-sm); padding:10px 12px; font-size:12px; color:#1e40af;">
          <strong>Garantia de Integridade (RN-06):</strong> O encerramento não remove o animal do histórico do lote. O vínculo passa para a tabela de associações encerradas com a contagem exata de dias permanecidos.
        </div>
      </div>

      <div class="agro-modal-footer">
        <button type="button" id="btn-cancel-disassociate" class="agro-btn agro-btn-secondary">
          Cancelar
        </button>
        <button type="submit" id="btn-submit-disassociate" class="agro-btn agro-btn-danger">
          <span class="btn-text">Confirmar Encerramento</span>
          <span class="agro-spinner" style="display:none; margin-left:6px;"></span>
        </button>
      </div>
    </form>
  </div>
</div>
