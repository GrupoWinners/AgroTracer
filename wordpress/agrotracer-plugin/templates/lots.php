<?php
/**
 * AgroTracer Herd Screen Template (Task S1-T03)
 * Módulo C: Gestão do Rebanho (Animais & Associação Temporal)
 */
?>
<section id="screen-lotes" class="agro-screen" aria-labelledby="lots-module-title">
  <div class="agro-master-detail-grid">
    <!-- Coluna Esquerda: Lista de Lotes -->
    <aside class="agro-sidebar-card" aria-label="Lista de Lotes">
      <div class="agro-sidebar-header">
        <h2 id="lots-module-title" class="agro-sidebar-title">Meus Lotes</h2>
        <button type="button" class="agro-btn agro-btn-primary agro-sidebar-action-btn" onclick="AgroTracer.showToast('Assistente de criação de lote inicializado.')">
          + Novo Lote
        </button>
      </div>

      <div class="agro-search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="search-lot-input" class="agro-search-input" placeholder="Buscar lote..." aria-label="Buscar lote">
      </div>

      <div class="agro-form-group" style="margin-bottom: 14px;">
        <label class="agro-form-label" for="filter-lot-farm" style="font-size:12px;">Fazenda</label>
        <select id="filter-lot-farm" class="agro-input" style="padding: 7px 10px; font-size: 13px;">
          <option value="all" selected>Todas as fazendas</option>
          <option value="1">Fazenda Modelo</option>
          <option value="2">Fazenda S&atilde;o Bento</option>
          <option value="3">Fazenda Boa Vista</option>
        </select>
      </div>

      <div class="agro-list-items">
        <!-- Lote 1: LT-2026-001 (Selected) -->
        <div class="agro-list-item selected" data-lot-code="LT-2026-001">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <circle cx="12" cy="11" r="5"></circle>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div style="display:flex; align-items:center; gap:6px;">
                <span class="agro-list-item-title">LT-2026-001</span>
                <span class="agro-badge warning" style="font-size:10px; padding:2px 6px;">Em manejo</span>
              </div>
              <div class="agro-list-item-sub">Fazenda Modelo - Aquidauana/MS</div>
              <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">50 animais</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>

        <!-- Lote 2: LT-2026-003 -->
        <div class="agro-list-item" data-lot-code="LT-2026-003">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <circle cx="12" cy="11" r="5"></circle>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div style="display:flex; align-items:center; gap:6px;">
                <span class="agro-list-item-title">LT-2026-003</span>
                <span class="agro-badge info" style="font-size:10px; padding:2px 6px;">Fechado</span>
              </div>
              <div class="agro-list-item-sub">Fazenda S&atilde;o Bento - Corumb&aacute;/MS</div>
              <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">100 animais</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>

        <!-- Lote 3: LT-2025-090 -->
        <div class="agro-list-item" data-lot-code="LT-2025-090">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <circle cx="12" cy="11" r="5"></circle>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div style="display:flex; align-items:center; gap:6px;">
                <span class="agro-list-item-title">LT-2025-090</span>
                <span class="agro-badge success" style="font-size:10px; padding:2px 6px;">Certificado</span>
              </div>
              <div class="agro-list-item-sub">Fazenda Boa Vista - Miranda/MS</div>
              <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">75 animais</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>

        <!-- Lote 4: LT-2024-087 -->
        <div class="agro-list-item" data-lot-code="LT-2024-087">
          <div class="agro-list-item-left">
            <div class="agro-list-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <circle cx="12" cy="11" r="5"></circle>
              </svg>
            </div>
            <div class="agro-list-item-info">
              <div style="display:flex; align-items:center; gap:6px;">
                <span class="agro-list-item-title">LT-2024-087</span>
                <span class="agro-badge neutral" style="font-size:10px; padding:2px 6px;">Abatido</span>
              </div>
              <div class="agro-list-item-sub">Fazenda Estrela do Sul - Bodoquena/MS</div>
              <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">0 animais</div>
            </div>
          </div>
          <div class="agro-list-item-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>
      </div>

      <div class="agro-sidebar-footer">
        Total de lotes: 4
      </div>
    </aside>

    <!-- Coluna Direita: Detalhes do Lote Selecionado & Rebanho -->
    <main class="agro-detail-main">
      <div class="agro-detail-top-bar">
        <a href="#lotes" class="agro-back-link" onclick="AgroTracer.switchScreen('lotes')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Voltar para Lotes
        </a>
      </div>

      <!-- Header do Lote -->
      <div class="agro-detail-header-card">
        <div class="agro-detail-title-group">
          <div class="agro-detail-hero-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:24px;height:24px;">
              <circle cx="12" cy="11" r="5"></circle>
            </svg>
          </div>
          <div>
            <div style="display:flex; align-items:center; gap:10px;">
              <h2 id="lot-detail-title" class="agro-detail-title">Lote: LT-2026-001</h2>
              <span id="lot-detail-badge" class="agro-badge warning" style="font-size:11.5px;">Em manejo</span>
            </div>
            <div class="agro-detail-meta">
              <span class="agro-detail-meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                <span id="lot-detail-entry">Entrada: 20/06/2026</span>
              </span>
              <span class="agro-detail-meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18"></path><path d="M5 21V7l8-4v18"></path></svg>
                <span id="lot-detail-farm">Fazenda Modelo (Aquidauana/MS)</span>
              </span>
              <span class="agro-detail-meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                <span id="lot-detail-days">Dias em manejo: 72</span>
              </span>
            </div>
          </div>
        </div>

        <div class="agro-detail-actions">
          <button type="button" class="agro-btn agro-btn-secondary" id="btn-edit-lot">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            Editar Lote
          </button>
          <button type="button" class="agro-btn agro-btn-primary" id="btn-movement-lot" onclick="AgroTracer.showToast('Fluxo de movimentação de lote iniciado.')">
            + Registrar Movimenta&ccedil;&atilde;o
          </button>
        </div>
      </div>

      <!-- Card: Animais Atualmente no Lote -->
      <div class="agro-card">
        <div class="agro-card-header">
          <div class="agro-card-header-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="11" r="5"></circle>
            </svg>
            <div>
              <h3 class="agro-card-title">Animais Atualmente no Lote</h3>
              <p class="agro-card-subtitle">50 animais ativos neste lote.</p>
            </div>
          </div>
          <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" id="btn-open-associate-drawer">
            + Associar Animais
          </button>
        </div>

        <div class="agro-card-body">
          <div class="agro-table-responsive">
            <table class="agro-table">
              <thead>
                <tr>
                  <th>Identificador &Uacute;nico</th>
                  <th>Categoria</th>
                  <th>Data Nasc.</th>
                  <th>Associado em</th>
                  <th>A&ccedil;&otilde;es</th>
                </tr>
              </thead>
              <tbody id="current-animals-tbody">
                <tr>
                  <td><strong>BR-123456789-0</strong></td>
                  <td>Bovino Macho</td>
                  <td>12/03/2022</td>
                  <td>20/06/2026 10:24</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm">Ver Hist&oacute;rico</button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal">Desassociar</button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td><strong>BR-123456790-1</strong></td>
                  <td>Bovino F&ecirc;mea</td>
                  <td>05/05/2022</td>
                  <td>21/06/2026 14:32</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm">Ver Hist&oacute;rico</button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal">Desassociar</button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td><strong>BR-123456791-2</strong></td>
                  <td>Bovino Macho</td>
                  <td>18/07/2022</td>
                  <td>22/06/2026 09:12</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm">Ver Hist&oacute;rico</button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal">Desassociar</button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td><strong>BR-123456792-3</strong></td>
                  <td>Bovino F&ecirc;mea</td>
                  <td>20/08/2022</td>
                  <td>22/06/2026 11:45</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm">Ver Hist&oacute;rico</button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal">Desassociar</button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td><strong>BR-123456793-4</strong></td>
                  <td>Bovino Macho</td>
                  <td>01/09/2022</td>
                  <td>23/06/2026 08:30</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm">Ver Hist&oacute;rico</button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal">Desassociar</button>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td><strong>BR-123456794-5</strong></td>
                  <td>Bovino F&ecirc;mea</td>
                  <td>15/09/2022</td>
                  <td>24/06/2026 15:00</td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm">Ver Hist&oacute;rico</button>
                      <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal">Desassociar</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="agro-table-footer">
            <span>Mostrando 1 a 6 de 50 animais</span>
            <div class="agro-pagination">
              <button type="button" class="agro-pagination-btn" disabled>&lt;</button>
              <button type="button" class="agro-pagination-btn active">1</button>
              <button type="button" class="agro-pagination-btn">2</button>
              <button type="button" class="agro-pagination-btn">3</button>
              <button type="button" class="agro-pagination-btn">4</button>
              <button type="button" class="agro-pagination-btn">5</button>
              <button type="button" class="agro-pagination-btn">&gt;</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Card: Histórico de Animais no Lote (Temporal Collapsible) -->
      <div class="agro-card">
        <div id="historical-collapse-header" class="agro-card-header agro-collapsible-header">
          <div class="agro-card-header-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <div>
              <h3 class="agro-card-title">Hist&oacute;rico de Animais no Lote</h3>
              <p class="agro-card-subtitle">Animais que j&aacute; estiveram neste lote (associa&ccedil;&otilde;es encerradas).</p>
            </div>
          </div>
          <div class="agro-collapsible-chevron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
              <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
          </div>
        </div>

        <div id="historical-collapse-content" class="agro-collapsible-content">
          <div class="agro-table-responsive">
            <table class="agro-table">
              <thead>
                <tr>
                  <th>Identificador Animal</th>
                  <th>Categoria</th>
                  <th>Data Associa&ccedil;&atilde;o</th>
                  <th>Data Desassocia&ccedil;&atilde;o</th>
                  <th>Dias Permanecidos</th>
                  <th style="width: 50px;"></th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>BR-987654321-0</strong></td>
                  <td>Bovino Macho</td>
                  <td>10/01/2026 08:15</td>
                  <td>20/03/2026 17:32</td>
                  <td>69</td>
                  <td>
                    <button type="button" class="agro-btn agro-btn-secondary agro-btn-icon-only" title="Ver Detalhes do Período">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    </button>
                  </td>
                </tr>
                <tr>
                  <td><strong>BR-987654322-1</strong></td>
                  <td>Bovino F&ecirc;mea</td>
                  <td>15/01/2026 10:24</td>
                  <td>05/04/2026 09:18</td>
                  <td>80</td>
                  <td>
                    <button type="button" class="agro-btn agro-btn-secondary agro-btn-icon-only" title="Ver Detalhes do Período">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    </button>
                  </td>
                </tr>
                <tr>
                  <td><strong>BR-987654323-2</strong></td>
                  <td>Bovino Macho</td>
                  <td>22/01/2026 14:50</td>
                  <td>12/05/2026 16:40</td>
                  <td>110</td>
                  <td>
                    <button type="button" class="agro-btn agro-btn-secondary agro-btn-icon-only" title="Ver Detalhes do Período">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  </div>
</section>

<!-- DRAWER LATERAL: ASSOCIAR ANIMAIS -->
<div id="associate-animals-drawer" class="agro-drawer-overlay" aria-hidden="true">
  <div class="agro-drawer" role="dialog" aria-labelledby="drawer-animals-title">
    <div class="agro-drawer-header">
      <h3 id="drawer-animals-title" class="agro-drawer-title">Associar Animais</h3>
      <button type="button" id="btn-close-associate-drawer" class="agro-drawer-close" aria-label="Fechar Painel">&times;</button>
    </div>

    <div class="agro-drawer-body">
      <!-- Filtro de Busca -->
      <div class="agro-search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" class="agro-search-input" placeholder="Buscar por identificador..." aria-label="Buscar animal">
      </div>

      <!-- Filtro Categoria -->
      <div class="agro-form-group" style="margin-bottom: 16px;">
        <label class="agro-form-label" for="drawer-filter-cat">Categoria</label>
        <select id="drawer-filter-cat" class="agro-input">
          <option value="all" selected>Todas</option>
          <option value="macho">Bovino Macho</option>
          <option value="femea">Bovino F&ecirc;mea</option>
        </select>
      </div>

      <!-- Lista Selecionável -->
      <table class="agro-selectable-table">
        <thead>
          <tr>
            <th style="width: 32px;"><input type="checkbox" class="agro-checkbox" id="select-all-drawer" aria-label="Selecionar todos"></th>
            <th>Identificador</th>
            <th>Categoria</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><input type="checkbox" class="agro-checkbox drawer-animal-checkbox" data-animal-id="BR-123456800-7"></td>
            <td><strong>BR-123456800-7</strong></td>
            <td>Macho</td>
            <td><span class="agro-badge success" style="font-size:11px;">Dispon&iacute;vel</span></td>
          </tr>
          <tr>
            <td><input type="checkbox" class="agro-checkbox drawer-animal-checkbox" data-animal-id="BR-123456801-8"></td>
            <td><strong>BR-123456801-8</strong></td>
            <td>F&ecirc;mea</td>
            <td><span class="agro-badge success" style="font-size:11px;">Dispon&iacute;vel</span></td>
          </tr>
          <tr>
            <td><input type="checkbox" class="agro-checkbox drawer-animal-checkbox" data-animal-id="BR-123456802-9"></td>
            <td><strong>BR-123456802-9</strong></td>
            <td>Macho</td>
            <td><span class="agro-badge success" style="font-size:11px;">Dispon&iacute;vel</span></td>
          </tr>
          <!-- Animal em conflito/ocupado (demonstrado no mockup com erro) -->
          <tr style="background-color: #fff9fa;">
            <td><input type="checkbox" class="agro-checkbox drawer-animal-checkbox" data-animal-id="BR-123456790-1" data-conflict="true"></td>
            <td><strong style="color: #991b1b;">BR-123456790-1</strong></td>
            <td>F&ecirc;mea</td>
            <td><span class="agro-badge danger" style="font-size:11px;">J&aacute; em outro lote</span></td>
          </tr>
          <tr>
            <td><input type="checkbox" class="agro-checkbox drawer-animal-checkbox" data-animal-id="BR-123456803-0"></td>
            <td><strong>BR-123456803-0</strong></td>
            <td>F&ecirc;mea</td>
            <td><span class="agro-badge success" style="font-size:11px;">Dispon&iacute;vel</span></td>
          </tr>
          <tr>
            <td><input type="checkbox" class="agro-checkbox drawer-animal-checkbox" data-animal-id="BR-123456804-1"></td>
            <td><strong>BR-123456804-1</strong></td>
            <td>Macho</td>
            <td><span class="agro-badge success" style="font-size:11px;">Dispon&iacute;vel</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="agro-drawer-footer">
      <span id="drawer-selected-count" style="font-size:13px; font-weight:600; color:var(--agro-text-secondary);">Selecionados: 0</span>
      <button type="button" id="btn-add-animals-to-list" class="agro-btn agro-btn-primary">
        + Adicionar &agrave; lista
      </button>
    </div>
  </div>
</div>
