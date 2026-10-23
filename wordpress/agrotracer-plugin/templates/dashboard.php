<?php
/**
 * AgroTracer Dashboard Screen Template (Task S1-T03)
 * Módulo A: Dashboard do Produtor com Próxima Ação Recomendada
 */
?>
<section id="screen-dashboard" class="agro-screen active" aria-labelledby="dashboard-title">
  <!-- Top Greeting -->
  <div class="agro-welcome-section">
    <div class="agro-welcome-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path>
        <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path>
      </svg>
    </div>
    <div>
      <h1 id="dashboard-title" class="agro-welcome-title">Ol&aacute;, Jo&atilde;o Silva!</h1>
      <p class="agro-welcome-subtitle">Bem-vindo &agrave; vis&atilde;o geral da Fazenda Modelo (MS).</p>
    </div>
  </div>

  <!-- Próximas Ações Recomendadas (Diretriz Nadiny) -->
  <div class="agro-section-title-wrap">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
      <path d="M9 12h6"></path>
      <path d="M9 16h6"></path>
    </svg>
    <h2 class="agro-section-title">Pr&oacute;ximas a&ccedil;&otilde;es</h2>
  </div>

  <div class="agro-actions-grid">
    <!-- Action Card 1: Warning (Manejo/Abate) -->
    <div class="agro-action-card warning-card">
      <div class="agro-action-card-left">
        <div class="agro-action-card-icon">
          <svg viewBox="0 0 24 24" fill="currentColor" style="width:28px;height:28px;">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
          </svg>
        </div>
        <div class="agro-action-card-text">
          <strong>Aten&ccedil;&atilde;o:</strong> Per&iacute;odo de manejo do lote <strong>LT-2026-001</strong> termina em <strong>2 dias (30/09/2026)</strong>. Registre o fechamento/abate para iniciar a certifica&ccedil;&atilde;o.
        </div>
      </div>
      <button type="button" class="agro-btn agro-btn-primary" onclick="AgroTracer.switchScreen('lotes')">
        Registrar abate
      </button>
    </div>

    <!-- Action Card 2: Info (Método Didático) -->
    <div class="agro-action-card info-card">
      <div class="agro-action-card-left">
        <div class="agro-action-card-icon">
          <svg viewBox="0 0 24 24" fill="currentColor" style="width:28px;height:28px;">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
        </div>
        <div class="agro-action-card-text">
          <strong>Nova vers&atilde;o do m&eacute;todo did&aacute;tico v1.1 dispon&iacute;vel.</strong>
          <span>Consulte mudan&ccedil;as nas estimativas de teste.</span>
        </div>
      </div>
      <button type="button" class="agro-btn agro-btn-secondary">
        Ver nova vers&atilde;o
      </button>
    </div>
  </div>

  <!-- KPI Cards Grid (4 Cards) -->
  <div class="agro-kpi-grid">
    <!-- KPI 1 -->
    <div class="agro-kpi-card">
      <div class="agro-kpi-icon-wrap" title="Lotes Ativos">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 21h18"></path>
          <path d="M5 21V7l8-4v18"></path>
          <path d="M19 21V11l-6-3"></path>
          <path d="M9 9h1"></path>
          <path d="M9 13h1"></path>
        </svg>
      </div>
      <div class="agro-kpi-content">
        <div class="agro-kpi-label">Lotes ativos</div>
        <div class="agro-kpi-value">12</div>
      </div>
    </div>

    <!-- KPI 2 -->
    <div class="agro-kpi-card">
      <div class="agro-kpi-icon-wrap" title="Total de Animais">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17 10h.01"></path>
          <path d="M7 10h.01"></path>
          <path d="M4 14c0 3 3 5 8 5s8-2 8-5"></path>
          <circle cx="12" cy="11" r="5"></circle>
        </svg>
      </div>
      <div class="agro-kpi-content">
        <div class="agro-kpi-label">Total de animais</div>
        <div class="agro-kpi-value">1.250</div>
        <div class="agro-kpi-footnote">Em 150 hectares de pastagem</div>
      </div>
    </div>

    <!-- KPI 3 -->
    <div class="agro-kpi-card">
      <div class="agro-kpi-icon-wrap" title="Emissões Totais">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path>
          <path d="M2 21c0-3 1.85-5.36 5.08-6"></path>
        </svg>
      </div>
      <div class="agro-kpi-content">
        <div class="agro-kpi-label">Emiss&otilde;es totais (kg CO&#8322;e)</div>
        <div class="agro-kpi-value">13.650</div>
        <div class="agro-kpi-footnote">Par&acirc;metros did&aacute;ticos do AgroTracer MVP; n&atilde;o representam fator oficial.</div>
      </div>
    </div>

    <!-- KPI 4 -->
    <div class="agro-kpi-card">
      <div class="agro-kpi-icon-wrap" title="Certificados Válidos">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          <polyline points="9 12 11 14 15 10"></polyline>
        </svg>
      </div>
      <div class="agro-kpi-content">
        <div class="agro-kpi-label">Certificados v&aacute;lidos</div>
        <div class="agro-kpi-value">8</div>
        <div class="agro-kpi-pill success">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:12px;height:12px;"><polyline points="20 6 9 17 4 12"></polyline></svg>
          4 prontos para emiss&atilde;o
        </div>
      </div>
    </div>
  </div>

  <!-- Resumo dos Lotes em Destaque -->
  <div class="agro-card">
    <div class="agro-card-header">
      <div class="agro-card-header-left">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
          <polyline points="2 17 12 22 22 17"></polyline>
          <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
        <h3 class="agro-card-title">Resumo dos lotes em destaque</h3>
      </div>
    </div>

    <div class="agro-card-body">
      <div class="agro-table-responsive">
        <table class="agro-table">
          <thead>
            <tr>
              <th>C&oacute;digo do lote</th>
              <th>Status</th>
              <th>&Uacute;ltimo manejo</th>
              <th>Animais</th>
              <th>Prontid&atilde;o</th>
              <th style="text-align: right;">A&ccedil;&otilde;es</th>
            </tr>
          </thead>
          <tbody>
            <!-- Row 1: LT-2026-001 -->
            <tr>
              <td><strong>LT-2026-001</strong></td>
              <td>
                <span class="agro-badge warning">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
                  Em manejo
                </span>
              </td>
              <td style="color: var(--agro-text-secondary);">Pastagem v1.0 &middot; termina 30/09</td>
              <td>50</td>
              <td>
                <div class="agro-progress-wrap">
                  <div class="agro-progress-bar">
                    <div class="agro-progress-fill" style="width: 90%;"></div>
                  </div>
                  <span class="agro-progress-text">90%</span>
                </div>
              </td>
              <td style="text-align: right;">
                <div style="display:inline-flex; gap:8px;">
                  <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" onclick="AgroTracer.switchScreen('lotes')">
                    Ver detalhes
                  </button>
                  <button type="button" class="agro-btn agro-btn-primary agro-btn-sm" onclick="AgroTracer.switchScreen('lotes')">
                    Manejo
                  </button>
                </div>
              </td>
            </tr>

            <!-- Row 2: LT-2026-003 -->
            <tr>
              <td><strong>LT-2026-003</strong></td>
              <td>
                <span class="agro-badge info">
                  <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                  Fechado
                </span>
              </td>
              <td style="color: var(--agro-text-secondary);">Dieta base v1.0 &middot; fim 15/09</td>
              <td>100</td>
              <td>
                <div class="agro-progress-wrap">
                  <div class="agro-progress-bar">
                    <div class="agro-progress-fill" style="width: 100%;"></div>
                  </div>
                  <span class="agro-progress-text">100%</span>
                </div>
              </td>
              <td style="text-align: right;">
                <div style="display:inline-flex; gap:8px;">
                  <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" onclick="AgroTracer.switchScreen('lotes')">
                    Ver detalhes
                  </button>
                  <button type="button" class="agro-btn agro-btn-primary agro-btn-sm" onclick="AgroTracer.showToast('Certificado gerado com Idempotency-Key.')">
                    Emitir certificado
                  </button>
                </div>
              </td>
            </tr>

            <!-- Row 3: LT-2025-090 -->
            <tr>
              <td><strong>LT-2025-090</strong></td>
              <td>
                <span class="agro-badge success">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                  Certificado
                </span>
              </td>
              <td style="color: var(--agro-text-muted);">&mdash;</td>
              <td>75</td>
              <td>
                <div class="agro-progress-wrap">
                  <div class="agro-progress-bar">
                    <div class="agro-progress-fill" style="width: 100%;"></div>
                  </div>
                  <span class="agro-progress-text">100%</span>
                </div>
              </td>
              <td style="text-align: right;">
                <div style="display:inline-flex; gap:8px;">
                  <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" onclick="AgroTracer.switchScreen('lotes')">
                    Ver detalhes
                  </button>
                  <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm">
                    Baixar PDF
                  </button>
                  <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm">
                    Ver QR
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>
