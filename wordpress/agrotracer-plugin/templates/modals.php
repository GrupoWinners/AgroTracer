<?php
/**
 * AgroTracer Modals Template (Task S1-T03)
 * Modais Obrigatórios: Erro de Validação de Domínio & Confirmação Crítica
 */
?>
<!-- MODAL: ERRO DE VALIDAÇÃO (CONFLITO DE ASSOCIAÇÃO TEMPORAL) -->
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
        <h3 id="val-modal-title" class="agro-modal-title">Erro de Valida&ccedil;&atilde;o</h3>
      </div>
      <button type="button" id="btn-close-validation-modal" class="agro-drawer-close" aria-label="Fechar Modal">&times;</button>
    </div>

    <div class="agro-modal-body">
      <p style="font-weight: 600; color: var(--agro-text-primary); margin: 0 0 6px 0;">
        N&atilde;o foi poss&iacute;vel completar a associa&ccedil;&atilde;o.
      </p>
      <p style="margin: 0; color: var(--agro-text-secondary);">
        Alguns animais foram associados concorrentemente em outros lotes. Recarregue a lista.
      </p>

      <div class="agro-modal-conflict-box">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
        </svg>
        <div>
          <strong>Exemplo de conflito:</strong>
          <span>Animal <strong>BR-123456790-1</strong> j&aacute; possui associa&ccedil;&atilde;o ativa em outro lote.</span>
        </div>
      </div>
    </div>

    <div class="agro-modal-footer">
      <button type="button" id="btn-understand-validation" class="agro-btn agro-btn-primary">
        Entendi
      </button>
    </div>
  </div>
</div>

<!-- MODAL: CONFIRMAÇÃO DE AÇÃO CRÍTICA / DESTRUTIVA -->
<div id="modal-confirm-action" class="agro-modal-backdrop" role="dialog" aria-labelledby="confirm-modal-title" aria-modal="true">
  <div class="agro-modal">
    <div class="agro-modal-header">
      <div class="agro-modal-header-left">
        <div class="agro-modal-icon-badge warning">
          <svg viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
          </svg>
        </div>
        <h3 id="confirm-modal-title" class="agro-modal-title">Confirmar A&ccedil;&atilde;o</h3>
      </div>
      <button type="button" class="agro-drawer-close" onclick="document.getElementById('modal-confirm-action').classList.remove('active')" aria-label="Fechar Modal">&times;</button>
    </div>

    <div class="agro-modal-body">
      <p id="confirm-modal-text" style="margin: 0; color: var(--agro-text-secondary); line-height: 1.5;">
        Tem certeza que deseja prosseguir com esta opera&ccedil;&atilde;o?
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
