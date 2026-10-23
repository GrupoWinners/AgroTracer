<?php
/**
 * AgroTracer Farms Screen Template (Task S1-T03)
 * Módulo B: Gestão de Propriedades Rurais (Fazendas & Talhões)
 */
?>
<section id="screen-fazendas" class="agro-screen" aria-labelledby="farms-module-title">
  <div class="agro-master-detail-grid">
    <!-- Coluna Esquerda: Lista de Propriedades -->
    <aside class="agro-sidebar-card" aria-label="Lista de Fazendas">
      <div class="agro-sidebar-header">
        <h2 id="farms-module-title" class="agro-sidebar-title">Minhas Propriedades</h2>
        <button type="button" class="agro-btn agro-btn-primary agro-sidebar-action-btn" onclick="AgroTracer.showToast('Formulário de nova fazenda ativado.')">
          + Nova Fazenda
        </button>
      </div>

      <div class="agro-search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="search-farms-input" class="agro-search-input" placeholder="Buscar Fazenda..." aria-label="Buscar Fazenda">
      </div>

      <div class="agro-list-items">
        <!-- Item 1: Fazenda Modelo (Selected) -->
        <div class="agro-list-item selected" data-farm-id="1">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div class="agro-list-item-title">Fazenda Modelo</div>
              <div class="agro-list-item-sub">Aquidauana - MS</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>

        <!-- Item 2: Fazenda São Bento -->
        <div class="agro-list-item" data-farm-id="2">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div class="agro-list-item-title">Fazenda S&atilde;o Bento</div>
              <div class="agro-list-item-sub">Corumb&aacute; - MS</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>

        <!-- Item 3: Fazenda Boa Vista -->
        <div class="agro-list-item" data-farm-id="3">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div class="agro-list-item-title">Fazenda Boa Vista</div>
              <div class="agro-list-item-sub">Miranda - MS</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>

        <!-- Item 4: Fazenda Estrela do Sul -->
        <div class="agro-list-item" data-farm-id="4">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div class="agro-list-item-title">Fazenda Estrela do Sul</div>
              <div class="agro-list-item-sub">Bodoquena - MS</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>

        <!-- Item 5: Fazenda Recanto Verde -->
        <div class="agro-list-item" data-farm-id="5">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div class="agro-list-item-title">Fazenda Recanto Verde</div>
              <div class="agro-list-item-sub">Coxim - MS</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>
      </div>
    </aside>

    <!-- Coluna Direita: Detalhes da Fazenda & Talhões -->
    <main class="agro-detail-main">
      <div class="agro-detail-top-bar">
        <a href="#fazendas" class="agro-back-link" onclick="AgroTracer.switchScreen('fazendas')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Voltar para Fazendas
        </a>
      </div>

      <!-- Header da Fazenda Selecionada -->
      <div class="agro-detail-header-card">
        <div class="agro-detail-title-group">
          <div class="agro-detail-hero-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:24px;height:24px;">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <div>
            <div style="display:flex; align-items:center; gap:10px;">
              <h2 id="farm-detail-name" class="agro-detail-title">Fazenda Modelo</h2>
              <span class="agro-badge success" style="font-size:11.5px;">Selecionada</span>
            </div>
            <div class="agro-detail-meta">
              <span class="agro-detail-meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                <span id="farm-detail-location">Aquidauana - MS</span>
              </span>
            </div>
          </div>
        </div>

        <div class="agro-detail-actions">
          <button type="button" class="agro-btn agro-btn-secondary" id="btn-cancel-farm">Cancelar</button>
          <button type="button" class="agro-btn agro-btn-secondary" id="btn-edit-farm">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            Editar
          </button>
          <button type="button" class="agro-btn agro-btn-danger" id="btn-delete-farm">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            Excluir fazenda
          </button>
        </div>
      </div>

      <!-- Card: Dados da Fazenda -->
      <div class="agro-card">
        <div class="agro-card-header">
          <div class="agro-card-header-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
              <path d="M9 12h6"></path>
              <path d="M9 16h6"></path>
            </svg>
            <h3 class="agro-card-title">Dados da Fazenda</h3>
          </div>
        </div>

        <form id="form-edit-farm">
          <div class="agro-form-grid">
            <!-- Nome da Propriedade -->
            <div class="agro-form-group">
              <label class="agro-form-label" for="farm-input-name">
                Nome da Propriedade <span class="required">*</span>
              </label>
              <input type="text" id="farm-input-name" class="agro-input" value="Fazenda Modelo" required>
            </div>

            <!-- Número do CAR (com erro/alerta demonstrativo) -->
            <div class="agro-form-group">
              <label class="agro-form-label" for="farm-input-car">
                N&uacute;mero do CAR <span class="required">*</span>
              </label>
              <div class="agro-input-wrap">
                <input type="text" id="farm-input-car" class="agro-input error has-icon" value="MS-5002708-1234.5678.9ABC.DEF0.1234.5678" required>
                <div class="agro-input-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;color:#dc2626;">
                    <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                  </svg>
                </div>
              </div>
              <div id="farm-car-error" class="agro-field-error">
                Este CAR j&aacute; est&aacute; cadastrado em outra fazenda.
              </div>
              <div class="agro-field-help">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:12px;height:12px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                Dado declarado pelo produtor. Verifique se o n&uacute;mero est&aacute; correto.
              </div>
            </div>

            <!-- Município & UF -->
            <div class="agro-form-group">
              <label class="agro-form-label" for="farm-select-city">
                Munic&iacute;pio <span class="required">*</span>
              </label>
              <select id="farm-select-city" class="agro-input">
                <option value="Aquidauana" selected>Aquidauana</option>
                <option value="Corumbá">Corumb&aacute;</option>
                <option value="Miranda">Miranda</option>
                <option value="Bodoquena">Bodoquena</option>
                <option value="Coxim">Coxim</option>
              </select>
            </div>

            <div class="agro-form-group">
              <label class="agro-form-label" for="farm-select-uf">
                UF <span class="required">*</span>
              </label>
              <select id="farm-select-uf" class="agro-input">
                <option value="MS" selected>MS</option>
                <option value="MT">MT</option>
                <option value="GO">GO</option>
                <option value="MG">MG</option>
                <option value="SP">SP</option>
              </select>
            </div>

            <!-- Coordenadas -->
            <div class="agro-form-group">
              <label class="agro-form-label" for="farm-input-coord">
                Coordenadas (opcional)
              </label>
              <div class="agro-input-wrap">
                <input type="text" id="farm-input-coord" class="agro-input has-icon" value="-20.4683, -55.7847">
                <div class="agro-input-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                </div>
              </div>
            </div>

            <!-- Callout Informativo Oficial CAR -->
            <div class="agro-form-group">
              <div class="agro-callout-info">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <div>
                  O CAR &eacute; um dado declarado pelo produtor e pode estar sujeito a valida&ccedil;&atilde;o externa pelos &oacute;rg&atilde;os competentes.
                </div>
              </div>
            </div>
          </div>

          <div class="agro-form-footer">
            <button type="submit" id="btn-save-farm" class="agro-btn agro-btn-primary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
              Salvar Altera&ccedil;&otilde;es
            </button>
          </div>
        </form>
      </div>

      <!-- Card: Talhões / Pastagens -->
      <div class="agro-card">
        <div class="agro-card-header">
          <div class="agro-card-header-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            <h3 class="agro-card-title">Talh&otilde;es / Pastagens</h3>
          </div>
          <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" onclick="AgroTracer.showToast('Novo talhão adicionado em rascunho.')">
            + Adicionar Talh&atilde;o
          </button>
        </div>

        <div class="agro-card-body">
          <div class="agro-table-responsive">
            <table class="agro-table">
              <thead>
                <tr>
                  <th>Identificador (Piquete)</th>
                  <th>&Aacute;rea (ha)</th>
                  <th>Tipo de Pastagem</th>
                  <th>&Uacute;ltima Atualiza&ccedil;&atilde;o</th>
                  <th>A&ccedil;&otilde;es</th>
                </tr>
              </thead>
              <tbody id="paddocks-tbody">
                <!-- Linhas inseridas dinamicamente via JS ou pré-renderizadas -->
                <tr>
                  <td style="font-weight: 500;">Piquete 01</td>
                  <td>25,50</td>
                  <td>Braqui&aacute;ria</td>
                  <td style="color: var(--agro-text-muted); font-size: 12.5px;">12/09/2026 14:32</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-icon-only" title="Editar Talhão">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#10b981;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                      </button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-icon-only" title="Excluir Talhão">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td style="font-weight: 500;">Piquete 02</td>
                  <td>18,75</td>
                  <td>Momba&ccedil;a</td>
                  <td style="color: var(--agro-text-muted); font-size: 12.5px;">10/09/2026 09:15</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-icon-only" title="Editar Talhão">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#10b981;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                      </button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-icon-only" title="Excluir Talhão">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td style="font-weight: 500;">Piquete 03</td>
                  <td>32,00</td>
                  <td>Andropogon</td>
                  <td style="color: var(--agro-text-muted); font-size: 12.5px;">08/09/2026 16:47</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-icon-only" title="Editar Talhão">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#10b981;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                      </button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-icon-only" title="Excluir Talhão">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td style="font-weight: 500;">Piquete 04</td>
                  <td>12,30</td>
                  <td>Tifton 85</td>
                  <td style="color: var(--agro-text-muted); font-size: 12.5px;">05/09/2026 11:20</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-icon-only" title="Editar Talhão">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#10b981;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                      </button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-icon-only" title="Excluir Talhão">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="agro-table-footer">
            <span id="paddocks-count-label">Mostrando 1 a 4 de 4 talh&otilde;es</span>
            <div class="agro-pagination">
              <button type="button" class="agro-pagination-btn" disabled>&lt;</button>
              <button type="button" class="agro-pagination-btn active">1</button>
              <button type="button" class="agro-pagination-btn" disabled>&gt;</button>
              <select class="agro-input" style="padding: 3px 8px; font-size: 12px; width: 68px; margin-left: 6px;">
                <option value="10" selected>10</option>
                <option value="25">25</option>
                <option value="50">50</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</section>
