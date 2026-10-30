<?php
/**
 * AgroTracer Herd & Lots Screen Template (Sprint 2 - Task S2-T04)
 * Módulo C: Gestão do Rebanho e Lotes (Cadastro, Listagem, Filtros, Badges e Histórico)
 * Cuidado de Engenharia: Design System rigoroso e Ações importantes 100% visíveis sem hover.
 */
if (!defined('ABSPATH')) {
    // Direct access security fallback
}
?>
<section id="screen-lotes" class="agro-screen" aria-labelledby="lots-module-title">

  <!-- Sub-navegação em Abas: Lotes vs Inventário de Animais -->
  <div class="agro-subnav-tabs" role="tablist" aria-label="Visões de Lotes e Animais">
    <button type="button" class="agro-tab-btn active" id="tab-btn-lotes" role="tab" aria-selected="true" aria-controls="view-lotes-container">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="11" r="5"></circle>
        <path d="M17 10h.01"></path>
        <path d="M7 10h.01"></path>
        <path d="M4 14c0 3 3 5 8 5s8-2 8-5"></path>
      </svg>
      <span>Lotes de Manejo</span>
      <span class="agro-tab-counter" id="tab-counter-lots">4</span>
    </button>

    <button type="button" class="agro-tab-btn" id="tab-btn-animais" role="tab" aria-selected="false" aria-controls="view-animais-container">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="16" y1="2" x2="16" y2="6"></line>
        <line x1="8" y1="2" x2="8" y2="6"></line>
        <line x1="3" y1="10" x2="21" y2="10"></line>
      </svg>
      <span>Inventário do Rebanho (Animais)</span>
      <span class="agro-tab-counter" id="tab-counter-animals">1.250</span>
    </button>
  </div>

  <!-- =========================================================================
       VISÃO 1: LOTES DE MANEJO (MASTER-DETAIL)
       ========================================================================= -->
  <div id="view-lotes-container" class="agro-tab-panel active" role="tabpanel" aria-labelledby="tab-btn-lotes">
    <div class="agro-master-detail-grid">
      <!-- Coluna Esquerda: Lista de Lotes -->
      <aside class="agro-sidebar-card" aria-label="Lista de Lotes">
        <div class="agro-sidebar-header">
          <h2 id="lots-module-title" class="agro-sidebar-title">Meus Lotes</h2>
          <button type="button" class="agro-btn agro-btn-primary agro-sidebar-action-btn" id="btn-open-create-lot-modal">
            + Novo Lote
          </button>
        </div>

        <div class="agro-search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" id="search-lot-input" class="agro-search-input" placeholder="Buscar lote por código..." aria-label="Buscar lote por código">
        </div>

        <div class="agro-form-group" style="margin-bottom: 10px;">
          <label class="agro-form-label" for="filter-lot-farm" style="font-size:12px;">Fazenda</label>
          <select id="filter-lot-farm" class="agro-input" style="padding: 7px 10px; font-size: 13px;">
            <option value="all" selected>Todas as fazendas</option>
            <option value="Fazenda Modelo">Fazenda Modelo</option>
            <option value="Fazenda São Bento">Fazenda São Bento</option>
            <option value="Fazenda Boa Vista">Fazenda Boa Vista</option>
            <option value="Fazenda Estrela do Sul">Fazenda Estrela do Sul</option>
          </select>
        </div>

        <div class="agro-form-group" style="margin-bottom: 14px;">
          <label class="agro-form-label" for="filter-lot-status" style="font-size:12px;">Status do Lote</label>
          <select id="filter-lot-status" class="agro-input" style="padding: 7px 10px; font-size: 13px;">
            <option value="all" selected>Todos os status</option>
            <option value="Em manejo">Em manejo</option>
            <option value="Fechado">Fechado</option>
            <option value="Certificado">Certificado</option>
            <option value="Abatido">Abatido</option>
            <option value="Rascunho">Rascunho</option>
          </select>
        </div>

        <div class="agro-list-items" id="lots-list-items-container">
          <!-- Lote 1: LT-2026-001 (Selected) -->
          <div class="agro-list-item selected" data-lot-code="LT-2026-001" data-farm-name="Fazenda Modelo" data-lot-status="Em manejo">
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
                <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">50 animais ativos</div>
              </div>
            </div>
            <div class="agro-list-item-chevron">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </div>
          </div>

          <!-- Lote 2: LT-2026-003 -->
          <div class="agro-list-item" data-lot-code="LT-2026-003" data-farm-name="Fazenda São Bento" data-lot-status="Fechado">
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
                <div class="agro-list-item-sub">Fazenda São Bento - Corumbá/MS</div>
                <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">100 animais ativos</div>
              </div>
            </div>
            <div class="agro-list-item-chevron">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </div>
          </div>

          <!-- Lote 3: LT-2025-090 -->
          <div class="agro-list-item" data-lot-code="LT-2025-090" data-farm-name="Fazenda Boa Vista" data-lot-status="Certificado">
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
                <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">75 animais ativos</div>
              </div>
            </div>
            <div class="agro-list-item-chevron">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </div>
          </div>

          <!-- Lote 4: LT-2024-087 -->
          <div class="agro-list-item" data-lot-code="LT-2024-087" data-farm-name="Fazenda Estrela do Sul" data-lot-status="Abatido">
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
                <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">0 animais ativos</div>
              </div>
            </div>
            <div class="agro-list-item-chevron">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </div>
          </div>
        </div>

        <div class="agro-sidebar-footer" id="lots-sidebar-footer-count">
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
            Visão Geral de Lotes
          </a>
        </div>

        <!-- Header do Lote com Ações Sempre Visíveis (Sem Hover) -->
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

          <!-- Ações Importantes Visíveis Imediatamente sem Hover -->
          <div class="agro-detail-actions">
            <button type="button" class="agro-btn agro-btn-secondary" id="btn-edit-lot" onclick="AgroTracer.showToast('Edição dos parâmetros do lote habilitada.')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
              <span>Editar Lote</span>
            </button>
            <button type="button" class="agro-btn agro-btn-primary" id="btn-movement-lot" onclick="AgroTracer.showToast('Fluxo de movimentação de lote iniciado.')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
              <span>+ Registrar Movimentação</span>
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
                <p class="agro-card-subtitle" id="lot-active-animals-subtitle">50 animais ativos associados a este lote.</p>
              </div>
            </div>
            <!-- Botão de ação visível sem hover -->
            <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" id="btn-open-associate-drawer">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
              <span>+ Associar Animais</span>
            </button>
          </div>

          <div class="agro-card-body">
            <div class="agro-table-responsive">
              <table class="agro-table" aria-label="Tabela de animais do lote">
                <thead>
                  <tr>
                    <th>Identificador Único (SISBOV)</th>
                    <th>Chip RFID</th>
                    <th>Categoria</th>
                    <th>Data Nasc.</th>
                    <th>Associado em</th>
                    <th>Ações Disponíveis</th>
                  </tr>
                </thead>
                <tbody id="current-animals-tbody">
                  <tr>
                    <td><strong>BR-123456789-0</strong></td>
                    <td><span style="font-family:monospace; color:var(--agro-text-secondary);">982000365892101</span></td>
                    <td>Bovino Macho</td>
                    <td>12/03/2022</td>
                    <td>20/06/2026 10:24</td>
                    <td>
                      <!-- AÇÕES 100% VISÍVEIS SEM HOVER -->
                      <div class="agro-table-actions">
                        <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="BR-123456789-0">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                          <span>Ver Histórico</span>
                        </button>
                        <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal" data-animal-id="BR-123456789-0">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                          <span>Desassociar</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>BR-123456790-1</strong></td>
                    <td><span style="font-family:monospace; color:var(--agro-text-secondary);">982000365892102</span></td>
                    <td>Bovino Fêmea</td>
                    <td>05/05/2022</td>
                    <td>21/06/2026 14:32</td>
                    <td>
                      <div class="agro-table-actions">
                        <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="BR-123456790-1">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                          <span>Ver Histórico</span>
                        </button>
                        <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal" data-animal-id="BR-123456790-1">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                          <span>Desassociar</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>BR-123456791-2</strong></td>
                    <td><span style="font-family:monospace; color:var(--agro-text-secondary);">982000365892103</span></td>
                    <td>Bovino Macho</td>
                    <td>18/07/2022</td>
                    <td>22/06/2026 09:12</td>
                    <td>
                      <div class="agro-table-actions">
                        <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="BR-123456791-2">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                          <span>Ver Histórico</span>
                        </button>
                        <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal" data-animal-id="BR-123456791-2">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                          <span>Desassociar</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>BR-123456792-3</strong></td>
                    <td><span style="font-family:monospace; color:var(--agro-text-secondary);">982000365892104</span></td>
                    <td>Bovino Fêmea</td>
                    <td>20/08/2022</td>
                    <td>22/06/2026 11:45</td>
                    <td>
                      <div class="agro-table-actions">
                        <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="BR-123456792-3">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                          <span>Ver Histórico</span>
                        </button>
                        <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal" data-animal-id="BR-123456792-3">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                          <span>Desassociar</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="agro-table-footer">
              <span id="current-lot-animals-count">Mostrando 1 a 4 de 50 animais</span>
              <div class="agro-pagination">
                <button type="button" class="agro-pagination-btn" disabled>&lt;</button>
                <button type="button" class="agro-pagination-btn active">1</button>
                <button type="button" class="agro-pagination-btn">2</button>
                <button type="button" class="agro-pagination-btn">3</button>
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
                <h3 class="agro-card-title">Histórico de Associações Encerradas no Lote</h3>
                <p class="agro-card-subtitle">Animais que já pertenceram a este lote (preservação histórica RN-06).</p>
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
              <table class="agro-table" aria-label="Histórico de animais encerrados no lote">
                <thead>
                  <tr>
                    <th>Identificador Animal</th>
                    <th>Categoria</th>
                    <th>Data Associação</th>
                    <th>Data Desassociação</th>
                    <th>Dias Permanecidos</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>BR-987654321-0</strong></td>
                    <td>Bovino Macho</td>
                    <td>10/01/2026 08:15</td>
                    <td>20/03/2026 17:32</td>
                    <td>69 dias</td>
                    <td>
                      <!-- Ação com texto explícito e visível sem hover -->
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="BR-987654321-0">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        <span>Ver Histórico</span>
                      </button>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>BR-987654322-1</strong></td>
                    <td>Bovino Fêmea</td>
                    <td>15/01/2026 10:24</td>
                    <td>05/04/2026 09:18</td>
                    <td>80 dias</td>
                    <td>
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="BR-987654322-1">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        <span>Ver Histórico</span>
                      </button>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>BR-987654323-2</strong></td>
                    <td>Bovino Macho</td>
                    <td>22/01/2026 14:50</td>
                    <td>12/05/2026 16:40</td>
                    <td>110 dias</td>
                    <td>
                      <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="BR-987654323-2">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        <span>Ver Histórico</span>
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
  </div>

  <!-- =========================================================================
       VISÃO 2: INVENTÁRIO GERAL DO REBANHO (ANIMAIS)
       ========================================================================= -->
  <div id="view-animais-container" class="agro-tab-panel" role="tabpanel" aria-labelledby="tab-btn-animais" style="display:none;">
    
    <!-- Faixa de Métricas do Rebanho (KPIs com Badges do DS) -->
    <div class="agro-metrics-strip">
      <div class="agro-metric-pill">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;color:var(--agro-primary);"><circle cx="12" cy="11" r="5"></circle></svg>
        <span>Rebanho Cadastrado: <strong>1.250</strong></span>
      </div>
      <div class="agro-metric-pill">
        <span class="agro-badge info" style="font-size:11px;">Em Lotes Ativos</span>
        <span>Alocados: <strong>1.180</strong></span>
      </div>
      <div class="agro-metric-pill">
        <span class="agro-badge success" style="font-size:11px;">Disponíveis</span>
        <span>Sem Lote: <strong>70</strong></span>
      </div>
      <div class="agro-metric-pill">
        <span class="agro-badge neutral" style="font-size:11px;">Conflitos Concorrentes</span>
        <span>Pendências: <strong>0</strong></span>
      </div>
    </div>

    <!-- Card Principal de Animais -->
    <div class="agro-card">
      <div class="agro-card-header">
        <div class="agro-card-header-left">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <div>
            <h3 class="agro-card-title">Inventário Individual de Animais</h3>
            <p class="agro-card-subtitle">Cadastro zootécnico oficial, rastreabilidade temporal e consulta histórica.</p>
          </div>
        </div>

        <!-- Ação Primária Visível Sem Hover -->
        <button type="button" class="agro-btn agro-btn-primary" id="btn-open-create-animal-modal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          <span>+ Cadastrar Animal</span>
        </button>
      </div>

      <div class="agro-card-body">
        
        <!-- Barra de Filtros Multifatoriais -->
        <div class="agro-filter-bar">
          <div class="agro-filter-search-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" id="search-animals-input" placeholder="Buscar por SISBOV ou chip RFID..." aria-label="Buscar animal por SISBOV ou RFID">
          </div>

          <div class="agro-filter-group">
            <label class="agro-filter-label" for="filter-animal-category">Categoria:</label>
            <select id="filter-animal-category" class="agro-filter-select">
              <option value="all" selected>Todas as categorias</option>
              <option value="Bovino Macho">Bovino Macho</option>
              <option value="Bovino Fêmea">Bovino Fêmea</option>
              <option value="Bezerro(a)">Bezerro(a)</option>
              <option value="Novilho(a)">Novilho(a)</option>
            </select>
          </div>

          <div class="agro-filter-group">
            <label class="agro-filter-label" for="filter-animal-status">Status de Alocação:</label>
            <select id="filter-animal-status" class="agro-filter-select">
              <option value="all" selected>Todos os status</option>
              <option value="Disponível">Disponível (Sem Lote)</option>
              <option value="Em Lote">Em Lote Ativo</option>
            </select>
          </div>

          <div class="agro-filter-group">
            <label class="agro-filter-label" for="filter-animal-farm">Fazenda:</label>
            <select id="filter-animal-farm" class="agro-filter-select">
              <option value="all" selected>Todas as fazendas</option>
              <option value="Fazenda Modelo">Fazenda Modelo</option>
              <option value="Fazenda São Bento">Fazenda São Bento</option>
              <option value="Fazenda Boa Vista">Fazenda Boa Vista</option>
            </select>
          </div>

          <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" id="btn-clear-animal-filters">
            <span>Limpar Filtros</span>
          </button>
        </div>

        <!-- Tabela do Inventário de Animais -->
        <div class="agro-table-responsive">
          <table class="agro-table" id="all-animals-table" aria-label="Tabela do Inventário de Animais">
            <thead>
              <tr>
                <th>Identificador SISBOV</th>
                <th>Chip RFID</th>
                <th>Categoria</th>
                <th>Status Atual</th>
                <th>Lote Vinculado</th>
                <th>Fazenda</th>
                <th>Data Nasc. Estimada</th>
                <th>Ações Contextuais</th>
              </tr>
            </thead>
            <tbody id="all-animals-tbody">
              <!-- Linhas populadas dinamicamente via JS / Mock inicial conforme contratos -->
            </tbody>
          </table>
        </div>

        <div class="agro-table-footer">
          <span id="animals-inventory-footer-count">Mostrando 1 a 8 de 1.250 animais</span>
          <div class="agro-pagination">
            <button type="button" class="agro-pagination-btn" disabled>&lt;</button>
            <button type="button" class="agro-pagination-btn active">1</button>
            <button type="button" class="agro-pagination-btn">2</button>
            <button type="button" class="agro-pagination-btn">3</button>
            <button type="button" class="agro-pagination-btn">4</button>
            <button type="button" class="agro-pagination-btn">&gt;</button>
          </div>
        </div>

      </div>
    </div>
  </div>

</section>

<!-- =========================================================================
     DRAWER LATERAL: ASSOCIAR ANIMAIS AO LOTE ATIVO
     ========================================================================= -->
<div id="associate-animals-drawer" class="agro-drawer-overlay" aria-hidden="true">
  <div class="agro-drawer" role="dialog" aria-labelledby="drawer-animals-title">
    <div class="agro-drawer-header">
      <h3 id="drawer-animals-title" class="agro-drawer-title">Associar Animais ao Lote</h3>
      <button type="button" id="btn-close-associate-drawer" class="agro-drawer-close" aria-label="Fechar Painel">&times;</button>
    </div>

    <div class="agro-drawer-body">
      <div class="agro-search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="drawer-search-input" class="agro-search-input" placeholder="Buscar por identificador..." aria-label="Buscar animal">
      </div>

      <div class="agro-form-group" style="margin-bottom: 16px;">
        <label class="agro-form-label" for="drawer-filter-cat">Filtrar por Categoria</label>
        <select id="drawer-filter-cat" class="agro-input">
          <option value="all" selected>Todas as categorias</option>
          <option value="Macho">Bovino Macho</option>
          <option value="Fêmea">Bovino Fêmea</option>
        </select>
      </div>

      <table class="agro-selectable-table" aria-label="Animais disponíveis para seleção">
        <thead>
          <tr>
            <th style="width: 32px;"><input type="checkbox" class="agro-checkbox" id="select-all-drawer" aria-label="Selecionar todos"></th>
            <th>Identificador</th>
            <th>Categoria</th>
            <th>Status Temporal</th>
          </tr>
        </thead>
        <tbody id="drawer-animals-tbody">
          <!-- Populado dinamicamente -->
        </tbody>
      </table>
    </div>

    <div class="agro-drawer-footer">
      <span id="drawer-selected-count" style="font-size:13px; font-weight:600; color:var(--agro-text-secondary);">Selecionados: 0</span>
      <button type="button" id="btn-add-animals-to-list" class="agro-btn agro-btn-primary">
        + Adicionar ao Lote
      </button>
    </div>
  </div>
</div>
