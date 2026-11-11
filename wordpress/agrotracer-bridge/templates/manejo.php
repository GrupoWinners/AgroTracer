<?php
/**
 * AgroTracer Nutritional Management & Timeline Screen Template (Sprint 3 - Task S3-T04)
 * Épico: [EP-S3] Sprint 3 — Manejo nutricional e método de parâmetros
 * Escopo: Tela de timeline de manejo com cadastro de períodos e mensagem de conflito que identifica o período conflitante.
 * Critérios de aceite: Usuário identifica o período conflitante; Unidades e datas claras; Estados de UX completos.
 */
if (!defined('ABSPATH')) {
    // Direct access security fallback
}
?>
<section id="screen-manejo" class="agro-screen" aria-labelledby="manejo-screen-title">

  <!-- Cabeçalho do Módulo de Manejo -->
  <div class="agro-screen-header">
    <div class="agro-screen-header-left">
      <div class="agro-screen-badge-container">
        <span class="agro-badge info" style="font-size: 11px; padding: 2px 8px;">Sprint 3 — Manejo Nutricional</span>
        <span class="agro-badge neutral" style="font-size: 11px; padding: 2px 8px;">RN-08 / RN-16 / RN-22</span>
      </div>
      <h1 id="manejo-screen-title" class="agro-screen-title" style="margin-top: 4px;">Timeline de Manejo Nutricional</h1>
      <p class="agro-screen-subtitle">
        Controle cronológico de períodos alimentares por lote sem sobreposição de datas. Parâmetros versionados e auditáveis.
      </p>
    </div>

    <div class="agro-screen-header-actions">
      <button type="button" class="agro-btn agro-btn-primary" id="btn-open-create-manejo-modal" aria-haspopup="dialog">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="width:16px;height:16px;margin-right:6px;">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>+ Novo Período de Manejo</span>
      </button>
    </div>
  </div>

  <!-- Alerta de Transparência Científica (ADR S3-T02 / S3-T06) -->
  <div class="agro-alert info" style="margin-bottom: 20px; display: flex; align-items: flex-start; gap: 12px;" role="note">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;flex-shrink:0;margin-top:2px;">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="16" x2="12" y2="12"></line>
      <line x1="12" y1="8" x2="12.01" y2="8"></line>
    </svg>
    <div style="font-size: 12.5px; line-height: 1.45;">
      <strong>Transparência Científica &amp; Metodologia:</strong> Os fatores zootécnicos atualmente vinculados aos manejos utilizam o conjunto <strong>v1.0-2026 (Didático / Demonstrativo)</strong>. Conforme ADR S3-T02, fatores classificados como <code>SYNTHETIC</code> não constituem alegação científica oficial do IPCC ou da Embrapa e destinam-se exclusivamente à validação de integridade do sistema.
    </div>
  </div>

  <!-- Barra de Filtros e Seleção do Lote -->
  <div class="agro-filter-bar" style="margin-bottom: 20px; background: #fff; padding: 16px 20px; border: 1px solid var(--agro-border); border-radius: var(--agro-radius-md);">
    <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px;">
      <div style="display: flex; align-items: center; gap: 12px; flex: 1; min-width: 280px;">
        <label for="select-manejo-lote" style="font-size: 13px; font-weight: 600; color: var(--agro-text-primary); white-space: nowrap;">
          Selecionar Lote de Manejo:
        </label>
        <select id="select-manejo-lote" class="agro-select" style="min-width: 220px;">
          <option value="1" data-code="LT-2026-001" data-farm="Fazenda Modelo" data-animals="28">LT-2026-001 (Fazenda Modelo — 28 animais)</option>
          <option value="2" data-code="LT-2026-003" data-farm="Fazenda Santa Fé" data-animals="45">LT-2026-003 (Fazenda Santa Fé — 45 animais)</option>
          <option value="3" data-code="LT-2025-090" data-farm="Fazenda Esperança" data-animals="12">LT-2025-090 (Fazenda Esperança — 12 animais)</option>
          <option value="4" data-code="LT-2024-087" data-farm="Fazenda Alvorada" data-animals="0">LT-2024-087 (Fazenda Alvorada — Vazio)</option>
        </select>
      </div>

      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 12.5px; color: var(--agro-text-muted);">Status do Lote:</span>
        <span id="manejo-lote-status-badge" class="agro-badge warning" style="font-size: 11.5px;">Em manejo</span>
      </div>
    </div>
  </div>

  <!-- Cards de KPIs e Unidades Claras -->
  <div class="agro-kpi-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px;">
    <div class="agro-kpi-card" style="background:#fff; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:16px;">
      <span class="agro-kpi-label" style="font-size:12px; color:var(--agro-text-muted); font-weight:500;">Dias em Manejo Acumulados</span>
      <div style="display:flex; align-items:baseline; gap:6px; margin-top:4px;">
        <span id="kpi-manejo-dias" class="agro-kpi-value" style="font-size:24px; font-weight:700; color:var(--agro-text-primary);">30</span>
        <span style="font-size:13px; color:var(--agro-text-secondary); font-weight:500;">dias</span>
      </div>
      <span style="font-size:11.5px; color:var(--agro-text-muted);">Soma dos períodos registrados</span>
    </div>

    <div class="agro-kpi-card" style="background:#fff; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:16px;">
      <span class="agro-kpi-label" style="font-size:12px; color:var(--agro-text-muted); font-weight:500;">Consumo Médio Estimado (CMS)</span>
      <div style="display:flex; align-items:baseline; gap:6px; margin-top:4px;">
        <span id="kpi-manejo-cms" class="agro-kpi-value" style="font-size:24px; font-weight:700; color:var(--agro-primary);">9.50</span>
        <span style="font-size:13px; color:var(--agro-text-secondary); font-weight:500;">kg MS/cab/dia</span>
      </div>
      <span style="font-size:11.5px; color:var(--agro-text-muted);">Matéria seca por cabeça/dia</span>
    </div>

    <div class="agro-kpi-card" style="background:#fff; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:16px;">
      <span class="agro-kpi-label" style="font-size:12px; color:var(--agro-text-muted); font-weight:500;">Fator Emissão Entérica</span>
      <div style="display:flex; align-items:baseline; gap:6px; margin-top:4px;">
        <span id="kpi-manejo-fe" class="agro-kpi-value" style="font-size:24px; font-weight:700; color:var(--agro-text-primary);">56.00</span>
        <span style="font-size:13px; color:var(--agro-text-secondary); font-weight:500;">kg CH4/cab/ano</span>
      </div>
      <span style="font-size:11.5px; color:var(--agro-text-muted);">Parâmetro ativo v1.0-2026</span>
    </div>

    <div class="agro-kpi-card" style="background:#fff; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:16px;">
      <span class="agro-kpi-label" style="font-size:12px; color:var(--agro-text-muted); font-weight:500;">Consistência da Timeline</span>
      <div style="display:flex; align-items:center; gap:8px; margin-top:6px;">
        <span id="kpi-timeline-integrity-badge" class="agro-badge success" style="font-size:12px; padding:4px 10px;">
          ✓ Sem Conflitos (RN-08)
        </span>
      </div>
      <span style="font-size:11.5px; color:var(--agro-text-muted);">Períodos contíguos sem sobreposição</span>
    </div>
  </div>

  <!-- Banner de Identificação de Conflito de Manejo (HTTP 409 - MANEJO_SOBREPOSTO) -->
  <div id="manejo-conflict-banner" class="agro-alert danger" style="display: none; margin-bottom: 20px; border-left: 4px solid #e11d48; background-color: #fff1f2; padding: 14px 18px; border-radius: var(--agro-radius-md);" role="alert">
    <div style="display: flex; align-items: flex-start; gap: 12px;">
      <svg viewBox="0 0 24 24" fill="currentColor" style="width:22px;height:22px;color:#e11d48;flex-shrink:0;margin-top:2px;">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
      <div style="flex: 1;">
        <h4 style="margin: 0 0 4px 0; font-size: 13.5px; font-weight: 700; color: #9f1239;">
          Conflito de Manejo Detectado — Código: MANEJO_SOBREPOSTO (HTTP 409)
        </h4>
        <p id="manejo-conflict-banner-text" style="margin: 0; font-size: 13px; color: #be123c; line-height: 1.45;">
          Existe sobreposição com um manejo já registrado para este lote.
        </p>
        <div id="manejo-conflict-banner-details" style="margin-top: 8px; font-size: 12.5px; background: rgba(255,255,255,0.7); padding: 8px 12px; border-radius: 4px; border: 1px solid #fecdd3; color: #881337;">
          Período Conflitante Identificado: <strong id="conflict-period-range">01/11/2026 a 10/11/2026</strong> (Lote <span id="conflict-lot-code">LT-2026-001</span>).
        </div>
      </div>
      <button type="button" class="agro-btn agro-btn-sm" id="btn-dismiss-conflict-banner" style="background:#fff; border:1px solid #fecdd3; color:#9f1239; font-size:12px;">
        Fechar Alerta
      </button>
    </div>
  </div>

  <!-- Estado de Carregamento (Loading UX State) -->
  <div id="manejo-loading-state" style="display: none; text-align: center; padding: 48px 24px; background: #fff; border: 1px solid var(--agro-border); border-radius: var(--agro-radius-md);">
    <div class="agro-spinner" style="margin: 0 auto 12px auto; width: 32px; height: 32px; border: 3px solid rgba(27,67,50,0.15); border-top-color: var(--agro-primary); border-radius: 50%; animation: agro-spin 0.8s linear infinite;"></div>
    <p style="font-size: 13px; color: var(--agro-text-secondary); margin: 0;">Carregando histórico e timeline de períodos nutricionais...</p>
  </div>

  <!-- Estado Vazio (Empty UX State) -->
  <div id="manejo-empty-state" style="display: none; text-align: center; padding: 48px 24px; background: #fff; border: 1px dashed var(--agro-border); border-radius: var(--agro-radius-md);">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 48px; height: 48px; color: #94a3b8; margin: 0 auto 12px auto;">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
      <line x1="16" y1="2" x2="16" y2="6"></line>
      <line x1="8" y1="2" x2="8" y2="6"></line>
      <line x1="3" y1="10" x2="21" y2="10"></line>
    </svg>
    <h3 style="font-size: 15px; font-weight: 600; color: var(--agro-text-primary); margin: 0 0 6px 0;">Nenhum Período de Manejo Registrado</h3>
    <p style="font-size: 13px; color: var(--agro-text-muted); max-width: 440px; margin: 0 auto 16px auto;">
      Este lote ainda não possui registros nutricionais ou períodos alimentares cadastrados. Inicie cadastrando o primeiro período para acompanhar a timeline.
    </p>
    <button type="button" class="agro-btn agro-btn-primary" id="btn-empty-create-manejo">
      + Cadastrar Primeiro Manejo
    </button>
  </div>

  <!-- Container Principal da Timeline Cronológica de Manejo -->
  <div id="manejo-timeline-card" class="agro-card" style="background: #fff; border: 1px solid var(--agro-border); border-radius: var(--agro-radius-md); padding: 24px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid var(--agro-border); padding-bottom: 12px;">
      <div>
        <h3 style="font-size: 14.5px; font-weight: 700; color: var(--agro-text-primary); margin: 0 0 4px 0;">
          Linha do Tempo Contínua de Períodos
        </h3>
        <p style="font-size: 12px; color: var(--agro-text-muted); margin: 0;">
          Datas inclusivas. Cada período deve suceder o anterior sem lacunas sobrepostas (RN-08).
        </p>
      </div>

      <div style="display: flex; align-items: center; gap: 8px;">
        <span class="agro-badge neutral" id="manejo-count-badge" style="font-size: 11.5px;">2 períodos ativos</span>
      </div>
    </div>

    <!-- Lista Vertical da Timeline -->
    <div class="agro-timeline" id="manejo-timeline-container" style="padding-left: 28px; margin: 0;">
      <!-- Itens serão renderizados dinamicamente via JS ou exibidos pelo mock inicial -->
      
      <!-- Período 1: 01/11/2026 a 10/11/2026 -->
      <div class="agro-timeline-item" data-manejo-id="1" data-inicio="2026-11-01" data-fim="2026-11-10">
        <div class="agro-timeline-dot active" title="Período Vigente"></div>
        <div class="agro-timeline-content" style="background:#fafbfc; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:16px;">
          <div class="agro-timeline-header" style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <span class="agro-timeline-title" style="font-size:14px; font-weight:700; color:var(--agro-text-primary);">
                  Dieta: Pastagem (Brachiaria brizantha)
                </span>
                <span class="agro-badge success" style="font-size:10.5px; padding:2px 6px;">Concluído</span>
              </div>
              <div class="agro-timeline-date" style="font-size:12.5px; font-weight:600; color:var(--agro-primary); margin-top:3px;">
                Datas: <span class="format-date-range">01/11/2026 a 10/11/2026</span> (Duração: 10 dias inclusivos)
              </div>
            </div>

            <span class="agro-badge info" style="font-size:11px;">Parâmetro Set #1 (v1.0-2026)</span>
          </div>

          <!-- Unidades e Fatores Zootécnicos Claros -->
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:12px; margin-top:12px; background:#fff; padding:12px; border-radius:6px; border:1px solid #e2e8f0;">
            <div>
              <span style="font-size:11px; color:var(--agro-text-muted); display:block;">Consumo Diário (CMS)</span>
              <strong style="font-size:13px; color:var(--agro-text-primary);">9.50 kg MS/cab/dia</strong>
            </div>
            <div>
              <span style="font-size:11px; color:var(--agro-text-muted); display:block;">Conversão Metano (Ym)</span>
              <strong style="font-size:13px; color:var(--agro-text-primary);">6.50 % EB</strong>
            </div>
            <div>
              <span style="font-size:11px; color:var(--agro-text-muted); display:block;">Emissão Entérica</span>
              <strong style="font-size:13px; color:var(--agro-text-primary);">56.00 kg CH4/cab/ano</strong>
            </div>
            <div>
              <span style="font-size:11px; color:var(--agro-text-muted); display:block;">Classificação de Origem</span>
              <span class="agro-badge neutral" style="font-size:10px;">SYNTHETIC (Didático)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Período 2: 11/11/2026 a 30/11/2026 -->
      <div class="agro-timeline-item" data-manejo-id="2" data-inicio="2026-11-11" data-fim="2026-11-30">
        <div class="agro-timeline-dot active" title="Período Atual"></div>
        <div class="agro-timeline-content" style="background:#fafbfc; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:16px;">
          <div class="agro-timeline-header" style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <span class="agro-timeline-title" style="font-size:14px; font-weight:700; color:var(--agro-text-primary);">
                  Dieta: Suplementação Mineral a Pasto
                </span>
                <span class="agro-badge warning" style="font-size:10.5px; padding:2px 6px;">Em Andamento</span>
              </div>
              <div class="agro-timeline-date" style="font-size:12.5px; font-weight:600; color:var(--agro-primary); margin-top:3px;">
                Datas: <span class="format-date-range">11/11/2026 a 30/11/2026</span> (Duração: 20 dias inclusivos)
              </div>
            </div>

            <span class="agro-badge info" style="font-size:11px;">Parâmetro Set #1 (v1.0-2026)</span>
          </div>

          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:12px; margin-top:12px; background:#fff; padding:12px; border-radius:6px; border:1px solid #e2e8f0;">
            <div>
              <span style="font-size:11px; color:var(--agro-text-muted); display:block;">Consumo Diário (CMS)</span>
              <strong style="font-size:13px; color:var(--agro-text-primary);">10.20 kg MS/cab/dia</strong>
            </div>
            <div>
              <span style="font-size:11px; color:var(--agro-text-muted); display:block;">Conversão Metano (Ym)</span>
              <strong style="font-size:13px; color:var(--agro-text-primary);">6.20 % EB</strong>
            </div>
            <div>
              <span style="font-size:11px; color:var(--agro-text-muted); display:block;">Emissão Entérica</span>
              <strong style="font-size:13px; color:var(--agro-text-primary);">54.50 kg CH4/cab/ano</strong>
            </div>
            <div>
              <span style="font-size:11px; color:var(--agro-text-muted); display:block;">Classificação de Origem</span>
              <span class="agro-badge neutral" style="font-size:10px;">SYNTHETIC (Didático)</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>

</section>
