<?php
/**
 * AgroTracer Modals Template (Sprint 2 - Task S2-T04)
 * Modais Obrigatórios:
 * 1. Erro de Validação de Domínio (Conflito de Associação Temporal RN-06)
 * 2. Confirmação Crítica / Destrutiva (Desassociação e Exclusão)
 * 3. Cadastro de Novo Lote de Manejo (RN-04)
 * 4. Cadastro de Novo Animal (RN-05)
 * 5. Histórico Temporal do Animal (Rastreabilidade Completa RN-06 / RN-07)
 */
if (!defined('ABSPATH')) {
    // Direct access security fallback
}
?>

<!-- 1. MODAL: ERRO DE VALIDAÇÃO (CONFLITO DE ASSOCIAÇÃO TEMPORAL RN-06) -->
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
        <h3 id="val-modal-title" class="agro-modal-title">Erro de Validação de Regra de Negócio</h3>
      </div>
      <button type="button" id="btn-close-validation-modal" class="agro-drawer-close" aria-label="Fechar Modal">&times;</button>
    </div>

    <div class="agro-modal-body">
      <p style="font-weight: 600; color: var(--agro-text-primary); margin: 0 0 6px 0;" id="val-modal-headline">
        Não foi possível completar a associação temporal.
      </p>
      <p style="margin: 0; color: var(--agro-text-secondary);" id="val-modal-description">
        Alguns animais selecionados já possuem uma associação ativa com outro lote. Conforme a regra de negócio (RN-06), um animal só pode pertencer a um único lote simultaneamente.
      </p>

      <div class="agro-modal-conflict-box" id="val-modal-conflict-box">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
        </svg>
        <div>
          <strong id="val-modal-conflict-code">Código de Erro: ANIMAL_JA_ASSOCIADO_CONFLITO (HTTP 409)</strong>
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

<!-- 3. MODAL: CADASTRO DE NOVO LOTE (TASK S2-T04 / RN-04) -->
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

<!-- 4. MODAL: CADASTRO DE NOVO ANIMAL (TASK S2-T04 / RN-05) -->
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
