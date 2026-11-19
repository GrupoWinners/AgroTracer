<?php
/**
 * AgroTracer Certificates Directory & Verification Hub (Sprint 6 - Task S6-T01)
 * Módulo F: Central de Certificados Emitidos, Consulta Pública e Download Seguro
 */
if (!defined('ABSPATH')) {
    // Direct access security fallback
}

$public_cert_base_url = function_exists('home_url')
    ? home_url('/certificado/')
    : '/certificado/';
?>
<section id="screen-certificados" class="agro-screen" aria-labelledby="certificados-screen-title">

  <!-- Cabeçalho do Módulo de Certificados -->
  <div class="agro-screen-header">
    <div class="agro-screen-header-left">
      <div class="agro-screen-badge-container">
        <span class="agro-badge info" style="font-size: 11px; padding: 2px 8px;">Certificação &amp; Rastreabilidade</span>
        <span class="agro-badge neutral" style="font-size: 11px; padding: 2px 8px;">RN-13 / Idempotência</span>
      </div>
      <h1 id="certificados-screen-title" class="agro-screen-title" style="margin-top: 4px;">
        Certificados Emitidos &amp; Verificação
      </h1>
      <p class="agro-screen-subtitle">
        Acompanhe o status dos certificados gerados por lote fechado, valide integridade SHA-256 e acesse a página pública de verificação.
      </p>
    </div>

    <div class="agro-screen-header-actions" style="display: flex; flex-wrap: wrap; gap: 10px;">
      <a href="<?php echo esc_url($public_cert_base_url); ?>" target="_blank" rel="noopener noreferrer" class="agro-btn agro-btn-secondary" id="btn-certificados-open-public-page">
        <span>Abrir Consulta Pública</span>
      </a>
      <button type="button" class="agro-btn agro-btn-primary" id="btn-certificados-new-emission" onclick="AgroTracer.switchScreen('fechamento')">
        <span>+ Emitir Novo Certificado</span>
      </button>
    </div>
  </div>

  <!-- Aviso de Proveniência e Política de Token Único (Estado: Aviso) -->
  <div class="agro-alert warning" data-source-type="SYNTHETIC" style="margin-bottom: 20px; display: flex; align-items: flex-start; gap: 12px;" role="note">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;flex-shrink:0;margin-top:2px;">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
      <line x1="12" y1="9" x2="12" y2="13"></line>
      <line x1="12" y1="17" x2="12.01" y2="17"></line>
    </svg>
    <div style="font-size: 12.5px; line-height: 1.45;">
      <strong>Proveniência [SYNTHETIC] &amp; Segurança de Token:</strong>
      Certificados emitidos no ambiente demonstrativo utilizam fatores didáticos. Por segurança (RN-13), o token público bruto é exibido apenas em memória no ato da emissão na tela de Fechamento.
    </div>
  </div>

  <!-- Banner de Erro Seguro (Estado: Erro — sem JSON cru) -->
  <div id="certificados-error-banner" class="agro-alert danger" style="display: none; margin-bottom: 20px;" role="alert">
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;">
      <div>
        <strong id="certificados-error-title" style="display:block; margin-bottom:4px;">Falha ao consultar certificados</strong>
        <p id="certificados-error-message" style="margin:0 0 6px 0;">Não foi possível carregar os certificados no momento. Tente novamente em instantes.</p>
        <span style="font-size:11.5px; opacity:0.85;">ID de Correlação: <code id="certificados-error-correlation">—</code></span>
      </div>
      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" id="btn-retry-certificados">Tentar Novamente</button>
    </div>
  </div>

  <!-- Barra de Filtros -->
  <div class="agro-filter-bar" style="margin-bottom: 20px; background: #fff; padding: 16px 20px; border: 1px solid var(--agro-border); border-radius: var(--agro-radius-md);">
    <div class="agro-filter-search-box" style="flex:1; min-width:240px;">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input type="text" id="search-certificados-input" placeholder="Buscar por lote ou ID do certificado..." aria-label="Buscar certificado por lote ou ID">
    </div>

    <div class="agro-filter-group">
      <label class="agro-filter-label" for="filter-certificados-status">Status:</label>
      <select id="filter-certificados-status" class="agro-filter-select">
        <option value="all" selected>Todos os status</option>
        <option value="VALIDO">Válido</option>
        <option value="REVOGADO">Revogado / Invalidado</option>
      </select>
    </div>

    <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" id="btn-clear-certificados-filters">
      Limpar Filtros
    </button>
  </div>

  <!-- Estado de Carregamento (Estado: Loading) -->
  <div id="certificados-loading-state" style="display: none; text-align: center; padding: 48px 24px; background: #fff; border: 1px solid var(--agro-border); border-radius: var(--agro-radius-md);">
    <div class="agro-spinner" style="margin: 0 auto 12px auto; width: 32px; height: 32px; border: 3px solid rgba(27,67,50,0.15); border-top-color: var(--agro-primary); border-radius: 50%; animation: agro-spin 0.8s linear infinite;"></div>
    <p style="font-size: 13px; color: var(--agro-text-secondary); margin: 0;">Carregando registros de certificados emitidos...</p>
  </div>

  <!-- Estado Vazio (Estado: Vazio) -->
  <div id="certificados-empty-state" class="agro-empty-state" style="display: none; background: #fff; border: 1px dashed var(--agro-border); border-radius: var(--agro-radius-md);">
    <div class="agro-empty-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
      </svg>
    </div>
    <h3 class="agro-empty-title">Nenhum certificado encontrado</h3>
    <p class="agro-empty-text">Ajuste os filtros de busca ou conclua o fechamento de um lote para emitir um novo certificado de pegada de carbono.</p>
    <div style="display:flex; gap:10px; flex-wrap:wrap; justify-content:center;">
      <button type="button" class="agro-btn agro-btn-secondary" id="btn-reset-certificados-empty">Limpar Filtros</button>
      <button type="button" class="agro-btn agro-btn-primary" onclick="AgroTracer.switchScreen('fechamento')">Ir para Fechamento</button>
    </div>
  </div>

  <!-- Lista de Certificados (Estado: Sucesso / Dados) -->
  <div id="certificados-list-card" class="agro-card">
    <div class="agro-card-header">
      <div class="agro-card-header-left">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          <polyline points="9 12 11 14 15 10"></polyline>
        </svg>
        <div>
          <h3 class="agro-card-title">Registro de Certificados</h3>
          <p class="agro-card-subtitle" id="certificados-count-subtitle">Certificados rastreados e auditáveis por snapshot imutável.</p>
        </div>
      </div>
    </div>

    <div class="agro-card-body">
      <div class="agro-table-responsive">
        <table class="agro-table" aria-label="Tabela de certificados emitidos">
          <thead>
            <tr>
              <th>Certificado</th>
              <th>Lote</th>
              <th>Status</th>
              <th>Emitido em</th>
              <th>Snapshot SHA-256</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody id="certificados-tbody">
            <!-- Preenchido dinamicamente via JS -->
          </tbody>
        </table>
      </div>
    </div>
  </div>

</section>
