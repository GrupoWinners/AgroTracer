/**
 * AgroTracer Interactive Frontend Engine
 * Version: 3.0.0
 * Architecture: Task S1-T03 - Interface Desktop Rural WordPress
 * Lead UI/UX: Nadiny Martins | Dev: João Vitor (Grupo Winners)
 */

(function () {
  'use strict';

  // Master State Store
  const AgroState = {
    currentScreen: 'dashboard',
    selectedFarmId: 1,
    selectedLotId: 'LT-2026-001',
    correlationId: '8d7c3f2a-9e4b',
    farms: [
      {
        id: 1,
        name: 'Fazenda Modelo',
        city: 'Aquidauana',
        uf: 'MS',
        car: 'MS-5002708-1234.5678.9ABC.DEF0.1234.5678',
        coordinates: '-20.4683, -55.7847',
        carHasConflict: true,
        paddocks: [
          { id: '01', name: 'Piquete 01', area: '25,50', pasture: 'Braquiária', updated: '12/09/2026 14:32' },
          { id: '02', name: 'Piquete 02', area: '18,75', pasture: 'Mombaça', updated: '10/09/2026 09:15' },
          { id: '03', name: 'Piquete 03', area: '32,00', pasture: 'Andropogon', updated: '08/09/2026 16:47' },
          { id: '04', name: 'Piquete 04', area: '12,30', pasture: 'Tifton 85', updated: '05/09/2026 11:20' }
        ]
      },
      {
        id: 2,
        name: 'Fazenda São Bento',
        city: 'Corumbá',
        uf: 'MS',
        car: 'MS-5003201-9876.5432.1FED.CBA9.8765.4321',
        coordinates: '-19.0061, -57.6533',
        carHasConflict: false,
        paddocks: [
          { id: '01', name: 'Piquete A1', area: '45,00', pasture: 'Braquiária', updated: '15/09/2026 10:10' },
          { id: '02', name: 'Piquete A2', area: '38,20', pasture: 'Panicum', updated: '14/09/2026 16:00' }
        ]
      },
      {
        id: 3,
        name: 'Fazenda Boa Vista',
        city: 'Miranda',
        uf: 'MS',
        car: 'MS-5001905-1122.3344.5566.7788.9900.1122',
        coordinates: '-20.2412, -56.3789',
        carHasConflict: false,
        paddocks: [
          { id: '01', name: 'Pastagem Norte', area: '50,00', pasture: 'Mombaça', updated: '01/09/2026 08:30' }
        ]
      },
      {
        id: 4,
        name: 'Fazenda Estrela do Sul',
        city: 'Bodoquena',
        uf: 'MS',
        car: 'MS-5004509-4433.2211.8877.6655.2211.3344',
        coordinates: '-20.5367, -56.7161',
        carHasConflict: false,
        paddocks: []
      },
      {
        id: 5,
        name: 'Fazenda Recanto Verde',
        city: 'Coxim',
        uf: 'MS',
        car: 'MS-5008901-7788.9900.1122.3344.5566.7788',
        coordinates: '-18.5067, -54.7600',
        carHasConflict: false,
        paddocks: []
      }
    ],
    lots: [
      {
        code: 'LT-2026-001',
        status: 'Em manejo',
        statusType: 'warning',
        farm: 'Fazenda Modelo - Aquidauana/MS',
        farmShort: 'Fazenda Modelo (Aquidauana/MS)',
        animalsCount: 50,
        entryDate: '20/06/2026',
        daysInManagement: 72,
        readiness: 90,
        lastManagement: 'Pastagem v1.0 · termina 30/09'
      },
      {
        code: 'LT-2026-003',
        status: 'Fechado',
        statusType: 'info',
        farm: 'Fazenda São Bento - Corumbá/MS',
        farmShort: 'Fazenda São Bento (Corumbá/MS)',
        animalsCount: 100,
        entryDate: '15/04/2026',
        daysInManagement: 110,
        readiness: 100,
        lastManagement: 'Dieta base v1.0 · fim 15/09'
      },
      {
        code: 'LT-2025-090',
        status: 'Certificado',
        statusType: 'success',
        farm: 'Fazenda Boa Vista - Miranda/MS',
        farmShort: 'Fazenda Boa Vista (Miranda/MS)',
        animalsCount: 75,
        entryDate: '10/01/2025',
        daysInManagement: 180,
        readiness: 100,
        lastManagement: '—'
      },
      {
        code: 'LT-2024-087',
        status: 'Abatido',
        statusType: 'neutral',
        farm: 'Fazenda Estrela do Sul - Bodoquena/MS',
        farmShort: 'Fazenda Estrela do Sul (Bodoquena/MS)',
        animalsCount: 0,
        entryDate: '01/08/2024',
        daysInManagement: 210,
        readiness: 100,
        lastManagement: 'Finalizado'
      }
    ],
    drawerAnimals: [
      { id: 'BR-123456800-7', category: 'Macho', available: true, status: 'Disponível' },
      { id: 'BR-123456801-8', category: 'Fêmea', available: true, status: 'Disponível' },
      { id: 'BR-123456802-9', category: 'Macho', available: true, status: 'Disponível' },
      { id: 'BR-123456790-1', category: 'Fêmea', available: false, status: 'Já em outro lote' },
      { id: 'BR-123456803-0', category: 'Fêmea', available: true, status: 'Disponível' },
      { id: 'BR-123456804-1', category: 'Macho', available: true, status: 'Disponível' }
    ]
  };

  // Helper: Generate clean Correlation ID
  function generateCorrelationId() {
    return '8d' + Math.random().toString(36).substring(2, 6) + '-' + Math.random().toString(36).substring(2, 6);
  }

  // Toast Notification System
  function showToast(message, correlationId) {
    const corrId = correlationId || AgroState.correlationId;
    let container = document.getElementById('agro-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'agro-toast-container';
      container.className = 'agro-toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'agro-toast';
    toast.innerHTML = `
      <div class="agro-toast-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:15px;height:15px;">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </div>
      <div class="agro-toast-content">
        <p class="agro-toast-title">${message}</p>
        <div class="agro-toast-correlation">ID da requisição: ${corrId}</div>
      </div>
      <button type="button" class="agro-toast-close" aria-label="Fechar">&times;</button>
    `;

    toast.querySelector('.agro-toast-close').addEventListener('click', () => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 200);
    });

    container.appendChild(toast);

    // Auto dismiss after 6 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 200);
      }
    }, 6000);
  }

  // Screen Switching
  function switchScreen(screenName) {
    if (!['dashboard', 'fazendas', 'lotes'].includes(screenName)) return;
    AgroState.currentScreen = screenName;

    // Update navigation active states
    document.querySelectorAll('.agro-nav-item').forEach(btn => {
      const target = btn.getAttribute('data-screen');
      if (target === screenName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update screens visibility
    document.querySelectorAll('.agro-screen').forEach(scr => {
      if (scr.id === `screen-${screenName}`) {
        scr.classList.add('active');
      } else {
        scr.classList.remove('active');
      }
    });

    window.location.hash = screenName;
  }

  // Setup Event Listeners
  function init() {
    // 1. Navigation items
    document.querySelectorAll('.agro-nav-item[data-screen]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const screen = btn.getAttribute('data-screen');
        switchScreen(screen);
      });
    });

    // Check hash on load
    if (window.location.hash) {
      const hashScreen = window.location.hash.replace('#', '');
      if (['dashboard', 'fazendas', 'lotes'].includes(hashScreen)) {
        switchScreen(hashScreen);
      }
    }

    // 2. Setup Farm selection & search
    setupFarmsModule();

    // 3. Setup Lots module & Drawer & Validation Modal
    setupLotsModule();

    // 4. Setup Modals close
    setupModals();
  }

  // Farms Module Handlers
  function setupFarmsModule() {
    const farmItems = document.querySelectorAll('.agro-list-item[data-farm-id]');
    farmItems.forEach(item => {
      item.addEventListener('click', () => {
        const farmId = parseInt(item.getAttribute('data-farm-id'), 10);
        selectFarm(farmId);
      });
    });

    // Search Farms
    const searchInput = document.getElementById('search-farms-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        document.querySelectorAll('.agro-list-item[data-farm-id]').forEach(card => {
          const text = card.textContent.toLowerCase();
          card.style.display = text.includes(query) ? 'flex' : 'none';
        });
      });
    }

    // Save Farm Form with Double-Click Prevention (Idempotência)
    const saveFarmBtn = document.getElementById('btn-save-farm');
    const formFarm = document.getElementById('form-edit-farm');
    if (saveFarmBtn && formFarm) {
      formFarm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Prevent double click: loading state
        if (saveFarmBtn.disabled) return;
        saveFarmBtn.disabled = true;
        const originalContent = saveFarmBtn.innerHTML;
        saveFarmBtn.innerHTML = `<span class="agro-spinner"></span> Salvando...`;

        // Simulate async request with idempotency
        setTimeout(() => {
          saveFarmBtn.disabled = false;
          saveFarmBtn.innerHTML = originalContent;
          const newCorrelation = generateCorrelationId();
          AgroState.correlationId = newCorrelation;
          
          // Update footer correlation ID as well
          const footerCorr = document.querySelector('.agro-correlation-id');
          if (footerCorr) footerCorr.textContent = newCorrelation;

          showToast('Fazenda atualizada com sucesso!', newCorrelation);
        }, 700);
      });
    }

    // Delete farm button
    const deleteFarmBtn = document.getElementById('btn-delete-farm');
    if (deleteFarmBtn) {
      deleteFarmBtn.addEventListener('click', () => {
        openConfirmModal(
          'Excluir Fazenda',
          'Tem certeza que deseja excluir a Fazenda Modelo? Esta ação removerá os vínculos e talhões associados.',
          () => {
            showToast('Operação simulada: exclusão de fazenda cancelada por segurança.', AgroState.correlationId);
          }
        );
      });
    }
  }

  function selectFarm(farmId) {
    AgroState.selectedFarmId = farmId;
    const farm = AgroState.farms.find(f => f.id === farmId);
    if (!farm) return;

    // Highlight selected card in sidebar
    document.querySelectorAll('.agro-list-item[data-farm-id]').forEach(card => {
      if (parseInt(card.getAttribute('data-farm-id'), 10) === farmId) {
        card.classList.add('selected');
      } else {
        card.classList.remove('selected');
      }
    });

    // Update details title and header
    const detailTitle = document.getElementById('farm-detail-name');
    const detailLocation = document.getElementById('farm-detail-location');
    if (detailTitle) detailTitle.textContent = farm.name;
    if (detailLocation) detailLocation.textContent = `${farm.city} - ${farm.uf}`;

    // Update form fields
    const inputName = document.getElementById('farm-input-name');
    const inputCar = document.getElementById('farm-input-car');
    const selectCity = document.getElementById('farm-select-city');
    const selectUf = document.getElementById('farm-select-uf');
    const inputCoord = document.getElementById('farm-input-coord');
    const carError = document.getElementById('farm-car-error');

    if (inputName) inputName.value = farm.name;
    if (inputCar) {
      inputCar.value = farm.car;
      if (farm.carHasConflict) {
        inputCar.classList.add('error');
        if (carError) carError.style.display = 'flex';
      } else {
        inputCar.classList.remove('error');
        if (carError) carError.style.display = 'none';
      }
    }
    if (selectCity) selectCity.value = farm.city;
    if (selectUf) selectUf.value = farm.uf;
    if (inputCoord) inputCoord.value = farm.coordinates;

    // Update Paddocks Table
    renderPaddocksTable(farm.paddocks);
  }

  function renderPaddocksTable(paddocks) {
    const tbody = document.getElementById('paddocks-tbody');
    const countLabel = document.getElementById('paddocks-count-label');
    if (!tbody) return;

    if (!paddocks || paddocks.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center; padding: 28px;">
            <div class="agro-empty-state" style="padding: 10px;">
              <div class="agro-empty-icon" style="width:40px;height:40px;margin-bottom:8px;">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
              </div>
              <p class="agro-empty-title" style="font-size:14px;">Nenhum talhão cadastrado</p>
              <p class="agro-empty-text" style="font-size:12px;margin-bottom:10px;">Cadastre piquetes ou pastagens para mapear a área desta fazenda.</p>
              <button type="button" class="agro-btn agro-btn-primary agro-btn-sm">+ Adicionar Primeiro Talhão</button>
            </div>
          </td>
        </tr>
      `;
      if (countLabel) countLabel.textContent = 'Mostrando 0 talhões';
      return;
    }

    let rowsHtml = '';
    paddocks.forEach(p => {
      rowsHtml += `
        <tr>
          <td style="font-weight: 500;">${p.name}</td>
          <td>${p.area}</td>
          <td>${p.pasture}</td>
          <td style="color: var(--agro-text-muted); font-size: 12.5px;">${p.updated}</td>
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
      `;
    });

    tbody.innerHTML = rowsHtml;
    if (countLabel) countLabel.textContent = `Mostrando 1 a ${paddocks.length} de ${paddocks.length} talhões`;
  }

  // Lots Module Handlers
  function setupLotsModule() {
    // Select Lot from sidebar
    document.querySelectorAll('.agro-list-item[data-lot-code]').forEach(item => {
      item.addEventListener('click', () => {
        const lotCode = item.getAttribute('data-lot-code');
        selectLot(lotCode);
      });
    });

    // Search Lots
    const searchLotInput = document.getElementById('search-lot-input');
    if (searchLotInput) {
      searchLotInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        document.querySelectorAll('.agro-list-item[data-lot-code]').forEach(card => {
          const text = card.textContent.toLowerCase();
          card.style.display = text.includes(query) ? 'flex' : 'none';
        });
      });
    }

    // Collapsible historical table
    const collapseHeader = document.getElementById('historical-collapse-header');
    const collapseContent = document.getElementById('historical-collapse-content');
    if (collapseHeader && collapseContent) {
      collapseHeader.addEventListener('click', () => {
        const isCollapsed = collapseContent.classList.contains('collapsed');
        if (isCollapsed) {
          collapseContent.classList.remove('collapsed');
          collapseHeader.classList.remove('collapsed');
        } else {
          collapseContent.classList.add('collapsed');
          collapseHeader.classList.add('collapsed');
        }
      });
    }

    // Drawer Open / Close
    const btnOpenDrawer = document.getElementById('btn-open-associate-drawer');
    const drawerOverlay = document.getElementById('associate-animals-drawer');
    const btnCloseDrawer = document.getElementById('btn-close-associate-drawer');

    if (btnOpenDrawer && drawerOverlay) {
      btnOpenDrawer.addEventListener('click', () => {
        drawerOverlay.classList.add('active');
      });
    }

    if (btnCloseDrawer && drawerOverlay) {
      btnCloseDrawer.addEventListener('click', () => {
        drawerOverlay.classList.remove('active');
      });
    }

    // Close on overlay backdrop click
    if (drawerOverlay) {
      drawerOverlay.addEventListener('click', (e) => {
        if (e.target === drawerOverlay) {
          drawerOverlay.classList.remove('active');
        }
      });
    }

    // Drawer Animals Selection Checkboxes
    const drawerCheckboxes = document.querySelectorAll('.drawer-animal-checkbox');
    const selectedCountLabel = document.getElementById('drawer-selected-count');
    const btnAddToList = document.getElementById('btn-add-animals-to-list');

    function updateSelectedCount() {
      const checkedCount = document.querySelectorAll('.drawer-animal-checkbox:checked').length;
      if (selectedCountLabel) {
        selectedCountLabel.textContent = `Selecionados: ${checkedCount}`;
      }
    }

    drawerCheckboxes.forEach(cb => {
      cb.addEventListener('change', updateSelectedCount);
    });

    // Add Animals Action -> Triggers Validation Error Modal or Success
    if (btnAddToList) {
      btnAddToList.addEventListener('click', () => {
        const selectedCheckboxes = Array.from(document.querySelectorAll('.drawer-animal-checkbox:checked'));
        
        if (selectedCheckboxes.length === 0) {
          alert('Selecione ao menos um animal disponível na lista.');
          return;
        }

        // Check if any selected has conflict simulation
        const hasConflict = selectedCheckboxes.some(cb => cb.getAttribute('data-conflict') === 'true');

        if (hasConflict) {
          // Open the Validation Conflict Modal
          openValidationErrorModal();
        } else {
          drawerOverlay.classList.remove('active');
          showToast(`${selectedCheckboxes.length} animais associados ao lote com sucesso!`, generateCorrelationId());
          // Uncheck all
          drawerCheckboxes.forEach(cb => cb.checked = false);
          updateSelectedCount();
        }
      });
    }

    // Disassociate animal button click
    document.querySelectorAll('.btn-disassociate-animal').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const row = e.target.closest('tr');
        const animalId = row ? row.querySelector('td').textContent.trim() : 'Animal';
        openConfirmModal(
          'Confirmar Desassociação',
          `Deseja realmente desassociar o animal ${animalId} do lote ${AgroState.selectedLotId}? O histórico temporal será registrado automaticamente.`,
          () => {
            showToast(`Animal ${animalId} desassociado com sucesso.`, generateCorrelationId());
          }
        );
      });
    });
  }

  function selectLot(lotCode) {
    AgroState.selectedLotId = lotCode;
    const lot = AgroState.lots.find(l => l.code === lotCode);
    if (!lot) return;

    // Highlight in sidebar
    document.querySelectorAll('.agro-list-item[data-lot-code]').forEach(card => {
      if (card.getAttribute('data-lot-code') === lotCode) {
        card.classList.add('selected');
      } else {
        card.classList.remove('selected');
      }
    });

    // Update lot detail view
    const headerTitle = document.getElementById('lot-detail-title');
    const headerBadge = document.getElementById('lot-detail-badge');
    const headerFarm = document.getElementById('lot-detail-farm');
    const headerEntry = document.getElementById('lot-detail-entry');
    const headerDays = document.getElementById('lot-detail-days');

    if (headerTitle) headerTitle.textContent = `Lote: ${lot.code}`;
    if (headerBadge) {
      headerBadge.textContent = lot.status;
      headerBadge.className = `agro-badge ${lot.statusType}`;
    }
    if (headerFarm) headerFarm.textContent = lot.farmShort;
    if (headerEntry) headerEntry.textContent = `Entrada: ${lot.entryDate}`;
    if (headerDays) headerDays.textContent = `Dias em manejo: ${lot.daysInManagement}`;
  }

  // Modals management
  function setupModals() {
    // Validation Error Modal Close
    const validationModal = document.getElementById('modal-validation-error');
    const btnCloseValidation = document.getElementById('btn-close-validation-modal');
    const btnUnderstand = document.getElementById('btn-understand-validation');

    if (btnCloseValidation && validationModal) {
      btnCloseValidation.addEventListener('click', () => validationModal.classList.remove('active'));
    }
    if (btnUnderstand && validationModal) {
      btnUnderstand.addEventListener('click', () => validationModal.classList.remove('active'));
    }

    // Confirmation Modal Close
    const confirmModal = document.getElementById('modal-confirm-action');
    const btnCancelConfirm = document.getElementById('btn-cancel-confirm');
    if (btnCancelConfirm && confirmModal) {
      btnCancelConfirm.addEventListener('click', () => confirmModal.classList.remove('active'));
    }
  }

  function openValidationErrorModal() {
    const modal = document.getElementById('modal-validation-error');
    if (modal) {
      modal.classList.add('active');
    }
  }

  function openConfirmModal(title, message, onConfirmCallback) {
    const modal = document.getElementById('modal-confirm-action');
    if (!modal) return;

    const modalTitle = document.getElementById('confirm-modal-title');
    const modalText = document.getElementById('confirm-modal-text');
    const confirmBtn = document.getElementById('btn-confirm-action');

    if (modalTitle) modalTitle.textContent = title;
    if (modalText) modalText.textContent = message;

    modal.classList.add('active');

    // Remove previous listeners
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

    newConfirmBtn.addEventListener('click', () => {
      modal.classList.remove('active');
      if (typeof onConfirmCallback === 'function') {
        onConfirmCallback();
      }
    });
  }

  // Public API
  window.AgroTracer = {
    switchScreen,
    showToast,
    openValidationErrorModal,
    openConfirmModal,
    state: AgroState
  };

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
