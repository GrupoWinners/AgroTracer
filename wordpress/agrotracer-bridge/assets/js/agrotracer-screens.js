/**
 * AgroTracer Interactive Frontend Engine
 * Version: 3.2.0 (Sprint 2 - Task S2-T04: Gestão de Lotes, Animais, Filtros e Zero Hover Dependency)
 * Equipe: Grupo Winners | DEV Front-end & PO: João Vitor | Back-End: Samela Maria | QA Lead: Nadiny Martins
 */

(function () {
  'use strict';

  // Master State Store
  const AgroState = {
    currentScreen: 'dashboard',
    currentSubTab: 'lotes',
    selectedFarmId: 1,
    selectedLotId: 'LT-2026-001',
    correlationId: (typeof window.agrotracerConfig !== 'undefined' && window.agrotracerConfig.correlationId)
      ? window.agrotracerConfig.correlationId
      : '123e4567-e89b-42d3-a456-426614174000',

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

    animals: [
      {
        identifier: 'BR-123456789-0',
        rfid: '982000365892101',
        category: 'Bovino Macho',
        birthDate: '12/03/2022',
        farm: 'Fazenda Modelo',
        lotCode: 'LT-2026-001',
        associatedAt: '20/06/2026 10:24',
        status: 'Em Lote',
        timeline: [
          { date: '20/06/2026 10:24', title: 'Associação Ativa ao Lote LT-2026-001', meta: 'Fazenda Modelo (Aquidauana/MS) · Em manejo intensivo (72 dias)', active: true },
          { date: '15/02/2026 09:00', title: 'Manejo de Pastagem / Piquete 02', meta: 'Transferido para forrageira Mombaça após pesagem de 480 kg', active: false },
          { date: '10/01/2026 a 20/03/2026', title: 'Associação Encerrada - Lote LT-2025-090', meta: '69 dias de permanência regular · Preservação histórica RN-06', active: false },
          { date: '12/03/2022', title: 'Nascimento e Identificação SISBOV', meta: 'Cadastro inicial na Fazenda Modelo · Brinco oficial aplicado', active: false }
        ]
      },
      {
        identifier: 'BR-123456790-1',
        rfid: '982000365892102',
        category: 'Bovino Fêmea',
        birthDate: '05/05/2022',
        farm: 'Fazenda Modelo',
        lotCode: 'LT-2026-001',
        associatedAt: '21/06/2026 14:32',
        status: 'Em Lote',
        timeline: [
          { date: '21/06/2026 14:32', title: 'Associação Ativa ao Lote LT-2026-001', meta: 'Fazenda Modelo (Aquidauana/MS) · 71 dias em lote', active: true },
          { date: '05/05/2022', title: 'Nascimento e Registro Genealógico', meta: 'Fazenda Modelo · Categoria Matriz Nelore', active: false }
        ]
      },
      {
        identifier: 'BR-123456791-2',
        rfid: '982000365892103',
        category: 'Bovino Macho',
        birthDate: '18/07/2022',
        farm: 'Fazenda Modelo',
        lotCode: 'LT-2026-001',
        associatedAt: '22/06/2026 09:12',
        status: 'Em Lote',
        timeline: [
          { date: '22/06/2026 09:12', title: 'Associação Ativa ao Lote LT-2026-001', meta: 'Fazenda Modelo · 70 dias em manejo', active: true },
          { date: '18/07/2022', title: 'Nascimento e Brincagem SISBOV', meta: 'Fazenda Modelo', active: false }
        ]
      },
      {
        identifier: 'BR-123456792-3',
        rfid: '982000365892104',
        category: 'Bovino Fêmea',
        birthDate: '20/08/2022',
        farm: 'Fazenda Modelo',
        lotCode: 'LT-2026-001',
        associatedAt: '22/06/2026 11:45',
        status: 'Em Lote',
        timeline: [
          { date: '22/06/2026 11:45', title: 'Associação Ativa ao Lote LT-2026-001', meta: 'Fazenda Modelo · 70 dias em manejo', active: true },
          { date: '20/08/2022', title: 'Nascimento e Identificação', meta: 'Fazenda Modelo', active: false }
        ]
      },
      {
        identifier: 'BR-123456800-7',
        rfid: '982000365892105',
        category: 'Bovino Macho',
        birthDate: '10/01/2023',
        farm: 'Fazenda Modelo',
        lotCode: null,
        associatedAt: null,
        status: 'Disponível',
        timeline: [
          { date: '10/01/2023', title: 'Nascimento e Identificação', meta: 'Fazenda Modelo · Animal livre para alocação', active: false }
        ]
      },
      {
        identifier: 'BR-123456801-8',
        rfid: '982000365892106',
        category: 'Bovino Fêmea',
        birthDate: '14/02/2023',
        farm: 'Fazenda São Bento',
        lotCode: null,
        associatedAt: null,
        status: 'Disponível',
        timeline: [
          { date: '14/02/2023', title: 'Nascimento e Identificação', meta: 'Fazenda São Bento · Animal sem lote vinculado', active: false }
        ]
      },
      {
        identifier: 'BR-123456802-9',
        rfid: '982000365892107',
        category: 'Bovino Macho',
        birthDate: '20/03/2023',
        farm: 'Fazenda Boa Vista',
        lotCode: null,
        associatedAt: null,
        status: 'Disponível',
        timeline: [
          { date: '20/03/2023', title: 'Nascimento e Identificação', meta: 'Fazenda Boa Vista · Pronto para manejo', active: false }
        ]
      },
      {
        identifier: 'BR-987654321-0',
        rfid: '982000365892108',
        category: 'Bovino Macho',
        birthDate: '15/09/2021',
        farm: 'Fazenda Modelo',
        lotCode: 'LT-2026-003',
        associatedAt: '15/04/2026 08:30',
        status: 'Em Lote',
        timeline: [
          { date: '15/04/2026 08:30', title: 'Associação Ativa ao Lote LT-2026-003', meta: 'Fazenda São Bento · Confinamento', active: true },
          { date: '10/01/2026 a 20/03/2026', title: 'Associação Encerrada ao Lote LT-2026-001', meta: '69 dias de permanência · Desassociado por transferência', active: false },
          { date: '15/09/2021', title: 'Cadastro Inicial e SISBOV', meta: 'Fazenda Modelo', active: false }
        ]
      }
    ],

    drawerAnimals: [
      { id: 'BR-123456800-7', category: 'Bovino Macho', available: true, status: 'Disponível' },
      { id: 'BR-123456801-8', category: 'Bovino Fêmea', available: true, status: 'Disponível' },
      { id: 'BR-123456802-9', category: 'Bovino Macho', available: true, status: 'Disponível' },
      { id: 'BR-123456790-1', category: 'Bovino Fêmea', available: false, status: 'Já em outro lote' },
      { id: 'BR-123456803-0', category: 'Bovino Fêmea', available: true, status: 'Disponível' },
      { id: 'BR-123456804-1', category: 'Bovino Macho', available: true, status: 'Disponível' }
    ]
  };

  // Helper: UUID v4 Correlation ID
  function generateCorrelationId() {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID().toLowerCase();
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  // Toast Notification System
  function showToast(message, correlationId) {
    const corrId = correlationId || generateCorrelationId();
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
        <div class="agro-toast-correlation">X-Correlation-ID: ${corrId}</div>
      </div>
      <button type="button" class="agro-toast-close" aria-label="Fechar">&times;</button>
    `;

    toast.querySelector('.agro-toast-close').addEventListener('click', () => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 200);
    });

    container.appendChild(toast);

    setTimeout(() => {
      if (toast.parentElement) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 200);
      }
    }, 6000);
  }

  // Navigation between screens
  function switchScreen(screenName) {
    if (!['dashboard', 'fazendas', 'lotes'].includes(screenName)) return;
    AgroState.currentScreen = screenName;

    document.querySelectorAll('.agro-nav-item').forEach(btn => {
      const target = btn.getAttribute('data-screen');
      if (target === screenName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    document.querySelectorAll('.agro-screen').forEach(scr => {
      if (scr.id === `screen-${screenName}`) {
        scr.classList.add('active');
      } else {
        scr.classList.remove('active');
      }
    });

    window.location.hash = screenName;
  }

  // Switch Sub-tabs in Lotes/Animais screen
  function switchSubTab(subTabName) {
    if (!['lotes', 'animais'].includes(subTabName)) return;
    AgroState.currentSubTab = subTabName;

    const btnLotes = document.getElementById('tab-btn-lotes');
    const btnAnimais = document.getElementById('tab-btn-animais');
    const viewLotes = document.getElementById('view-lotes-container');
    const viewAnimais = document.getElementById('view-animais-container');

    if (subTabName === 'lotes') {
      if (btnLotes) { btnLotes.classList.add('active'); btnLotes.setAttribute('aria-selected', 'true'); }
      if (btnAnimais) { btnAnimais.classList.remove('active'); btnAnimais.setAttribute('aria-selected', 'false'); }
      if (viewLotes) viewLotes.style.display = 'block';
      if (viewAnimais) viewAnimais.style.display = 'none';
    } else {
      if (btnLotes) { btnLotes.classList.remove('active'); btnLotes.setAttribute('aria-selected', 'false'); }
      if (btnAnimais) { btnAnimais.classList.add('active'); btnAnimais.setAttribute('aria-selected', 'true'); }
      if (viewLotes) viewLotes.style.display = 'none';
      if (viewAnimais) viewAnimais.style.display = 'block';
      renderAllAnimalsTable();
    }
  }

  // =========================================================================
  // SETUP LOTS & HERD MODULE (TASK S2-T04)
  // =========================================================================
  function setupLotsModule() {
    // 1. Sub-nav tab switching
    const tabBtnLotes = document.getElementById('tab-btn-lotes');
    const tabBtnAnimais = document.getElementById('tab-btn-animais');

    if (tabBtnLotes) {
      tabBtnLotes.addEventListener('click', () => switchSubTab('lotes'));
    }
    if (tabBtnAnimais) {
      tabBtnAnimais.addEventListener('click', () => switchSubTab('animais'));
    }

    // 2. Select lot from sidebar
    setupLotListClicks();

    // 3. Search and filter lots in sidebar
    setupLotFilters();

    // 4. Collapsible historical table
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

    // 5. Drawer de associação
    setupAssociateDrawer();

    // 6. Configurar Modais de Cadastro de Lote e Animal
    setupCreateLotModal();
    setupCreateAnimalModal();
    setupAnimalHistoryModal();

    // 7. Configurar Filtros do Inventário Geral de Animais
    setupAnimalInventoryFilters();

    // 8. Renderizar tabela inicial de animais
    renderAllAnimalsTable();
    renderCurrentLotAnimalsTable(AgroState.selectedLotId);
  }

  function setupLotListClicks() {
    document.querySelectorAll('.agro-list-item[data-lot-code]').forEach(item => {
      item.addEventListener('click', () => {
        const lotCode = item.getAttribute('data-lot-code');
        selectLot(lotCode);
      });
    });
  }

  function setupLotFilters() {
    const searchLotInput = document.getElementById('search-lot-input');
    const filterLotFarm = document.getElementById('filter-lot-farm');
    const filterLotStatus = document.getElementById('filter-lot-status');

    function applyLotFilters() {
      const query = searchLotInput ? searchLotInput.value.toLowerCase().trim() : '';
      const farmFilter = filterLotFarm ? filterLotFarm.value : 'all';
      const statusFilter = filterLotStatus ? filterLotStatus.value : 'all';

      let visibleCount = 0;
      document.querySelectorAll('.agro-list-item[data-lot-code]').forEach(card => {
        const lotCode = card.getAttribute('data-lot-code') || '';
        const farmName = card.getAttribute('data-farm-name') || '';
        const lotStatus = card.getAttribute('data-lot-status') || '';
        const text = card.textContent.toLowerCase();

        const matchesQuery = !query || text.includes(query) || lotCode.toLowerCase().includes(query);
        const matchesFarm = farmFilter === 'all' || farmName.includes(farmFilter);
        const matchesStatus = statusFilter === 'all' || lotStatus === statusFilter;

        if (matchesQuery && matchesFarm && matchesStatus) {
          card.style.display = 'flex';
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      const footer = document.getElementById('lots-sidebar-footer-count');
      if (footer) footer.textContent = `Total de lotes: ${visibleCount}`;
    }

    if (searchLotInput) searchLotInput.addEventListener('input', applyLotFilters);
    if (filterLotFarm) filterLotFarm.addEventListener('change', applyLotFilters);
    if (filterLotStatus) filterLotStatus.addEventListener('change', applyLotFilters);
  }

  function selectLot(lotCode) {
    AgroState.selectedLotId = lotCode;
    const lot = AgroState.lots.find(l => l.code === lotCode);
    if (!lot) return;

    // Highlight item
    document.querySelectorAll('.agro-list-item[data-lot-code]').forEach(card => {
      if (card.getAttribute('data-lot-code') === lotCode) {
        card.classList.add('selected');
      } else {
        card.classList.remove('selected');
      }
    });

    // Update lot detail view header
    const headerTitle = document.getElementById('lot-detail-title');
    const headerBadge = document.getElementById('lot-detail-badge');
    const headerFarm = document.getElementById('lot-detail-farm');
    const headerEntry = document.getElementById('lot-detail-entry');
    const headerDays = document.getElementById('lot-detail-days');
    const subtitle = document.getElementById('lot-active-animals-subtitle');

    if (headerTitle) headerTitle.textContent = `Lote: ${lot.code}`;
    if (headerBadge) {
      headerBadge.textContent = lot.status;
      headerBadge.className = `agro-badge ${lot.statusType}`;
    }
    if (headerFarm) headerFarm.textContent = lot.farmShort;
    if (headerEntry) headerEntry.textContent = `Entrada: ${lot.entryDate}`;
    if (headerDays) headerDays.textContent = `Dias em manejo: ${lot.daysInManagement}`;
    if (subtitle) subtitle.textContent = `${lot.animalsCount} animais ativos associados a este lote.`;

    renderCurrentLotAnimalsTable(lotCode);
  }

  function renderCurrentLotAnimalsTable(lotCode) {
    const tbody = document.getElementById('current-animals-tbody');
    const countLabel = document.getElementById('current-lot-animals-count');
    if (!tbody) return;

    const lotAnimals = AgroState.animals.filter(a => a.lotCode === lotCode);

    if (lotAnimals.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center; padding:32px 16px;">
            <div class="agro-empty-state" style="padding:10px;">
              <p class="agro-empty-title" style="font-size:14px;">Nenhum animal associado a este lote</p>
              <p class="agro-empty-text" style="font-size:12px; margin-bottom:12px;">Utilize o botão acima para associar animais disponíveis.</p>
              <button type="button" class="agro-btn agro-btn-primary agro-btn-sm" onclick="document.getElementById('associate-animals-drawer').classList.add('active')">
                + Associar Animais Agora
              </button>
            </div>
          </td>
        </tr>
      `;
      if (countLabel) countLabel.textContent = 'Mostrando 0 animais';
      return;
    }

    let rowsHtml = '';
    lotAnimals.forEach(a => {
      rowsHtml += `
        <tr>
          <td><strong>${a.identifier}</strong></td>
          <td><span style="font-family:monospace; color:var(--agro-text-secondary);">${a.rfid || '—'}</span></td>
          <td>${a.category}</td>
          <td>${a.birthDate}</td>
          <td>${a.associatedAt || '20/06/2026 10:24'}</td>
          <td>
            <div class="agro-table-actions">
              <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="${a.identifier}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                <span>Ver Histórico</span>
              </button>
              <button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal" data-animal-id="${a.identifier}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                <span>Desassociar</span>
              </button>
            </div>
          </td>
        </tr>
      `;
    });

    tbody.innerHTML = rowsHtml;
    if (countLabel) countLabel.textContent = `Mostrando 1 a ${lotAnimals.length} de ${lotAnimals.length} animais`;

    // Bind action events
    bindAnimalTableActions(tbody);
  }

  function bindAnimalTableActions(container) {
    container.querySelectorAll('.btn-view-animal-history').forEach(btn => {
      btn.addEventListener('click', () => {
        const animalId = btn.getAttribute('data-animal-id');
        openAnimalHistoryModal(animalId);
      });
    });

    container.querySelectorAll('.btn-disassociate-animal').forEach(btn => {
      btn.addEventListener('click', () => {
        const animalId = btn.getAttribute('data-animal-id');
        openConfirmModal(
          'Confirmar Desassociação Temporal',
          `Deseja realmente desassociar o animal ${animalId} do lote ${AgroState.selectedLotId}? A linha histórica será preservada com data de encerramento (RN-06).`,
          () => {
            const animal = AgroState.animals.find(a => a.identifier === animalId);
            if (animal) {
              animal.lotCode = null;
              animal.status = 'Disponível';
              animal.associatedAt = null;
              animal.timeline.unshift({
                date: new Date().toLocaleDateString('pt-BR') + ' ' + new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
                title: `Desassociação do Lote ${AgroState.selectedLotId}`,
                meta: 'Desassociação temporal registrada com integridade. O histórico anterior foi mantido.',
                active: false
              });
            }
            renderCurrentLotAnimalsTable(AgroState.selectedLotId);
            renderAllAnimalsTable();
            showToast(`Animal ${animalId} desassociado do lote ${AgroState.selectedLotId} com sucesso.`);
          }
        );
      });
    });
  }

  // =========================================================================
  // GESTÃO DO INVENTÁRIO DO REBANHO (TELA DE ANIMAIS)
  // =========================================================================
  function renderAllAnimalsTable() {
    const tbody = document.getElementById('all-animals-tbody');
    const footerCount = document.getElementById('animals-inventory-footer-count');
    if (!tbody) return;

    const searchInput = document.getElementById('search-animals-input');
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const catSelect = document.getElementById('filter-animal-category');
    const catFilter = catSelect ? catSelect.value : 'all';
    const statusSelect = document.getElementById('filter-animal-status');
    const statusFilter = statusSelect ? statusSelect.value : 'all';
    const farmSelect = document.getElementById('filter-animal-farm');
    const farmFilter = farmSelect ? farmSelect.value : 'all';

    const filtered = AgroState.animals.filter(a => {
      const matchQuery = !query || a.identifier.toLowerCase().includes(query) || (a.rfid && a.rfid.includes(query));
      const matchCat = catFilter === 'all' || a.category === catFilter;
      const matchStatus = statusFilter === 'all' || a.status === statusFilter;
      const matchFarm = farmFilter === 'all' || a.farm === farmFilter;
      return matchQuery && matchCat && matchStatus && matchFarm;
    });

    if (filtered.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align:center; padding:32px 16px;">
            <div class="agro-empty-state" style="padding:10px;">
              <p class="agro-empty-title" style="font-size:14px;">Nenhum animal encontrado com os filtros aplicados</p>
              <p class="agro-empty-text" style="font-size:12px; margin-bottom:10px;">Altere os parâmetros de pesquisa ou clique em "Limpar Filtros".</p>
              <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm" id="btn-reset-filters-empty">
                Limpar Filtros
              </button>
            </div>
          </td>
        </tr>
      `;
      const btnReset = document.getElementById('btn-reset-filters-empty');
      if (btnReset) {
        btnReset.addEventListener('click', () => {
          if (searchInput) searchInput.value = '';
          if (catSelect) catSelect.value = 'all';
          if (statusSelect) statusSelect.value = 'all';
          if (farmSelect) farmSelect.value = 'all';
          renderAllAnimalsTable();
        });
      }
      if (footerCount) footerCount.textContent = 'Mostrando 0 animais';
      return;
    }

    let html = '';
    filtered.forEach(a => {
      const isAvailable = a.status === 'Disponível';
      const statusBadge = isAvailable
        ? `<span class="agro-badge success" style="font-size:11px;">Disponível</span>`
        : `<span class="agro-badge info" style="font-size:11px;">Em Lote</span>`;

      const lotBadge = a.lotCode
        ? `<strong>${a.lotCode}</strong>`
        : `<span class="agro-badge neutral" style="font-size:10.5px;">Sem Lote</span>`;

      // Ações contextualizadas e visíveis sem hover
      const actionButton = isAvailable
        ? `<button type="button" class="agro-btn agro-btn-primary agro-btn-sm btn-quick-associate" data-animal-id="${a.identifier}">
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
             <span>Alocar em Lote</span>
           </button>`
        : `<button type="button" class="agro-btn agro-btn-danger agro-btn-sm btn-disassociate-animal" data-animal-id="${a.identifier}">
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
             <span>Desassociar</span>
           </button>`;

      html += `
        <tr>
          <td><strong>${a.identifier}</strong></td>
          <td><span style="font-family:monospace; color:var(--agro-text-secondary);">${a.rfid || '—'}</span></td>
          <td>${a.category}</td>
          <td>${statusBadge}</td>
          <td>${lotBadge}</td>
          <td>${a.farm}</td>
          <td>${a.birthDate}</td>
          <td>
            <!-- AÇÕES SEM HOVER -->
            <div class="agro-table-actions">
              <button type="button" class="agro-btn agro-btn-secondary agro-btn-sm btn-view-animal-history" data-animal-id="${a.identifier}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                <span>Ver Histórico</span>
              </button>
              ${actionButton}
            </div>
          </td>
        </tr>
      `;
    });

    tbody.innerHTML = html;
    if (footerCount) footerCount.textContent = `Mostrando 1 a ${filtered.length} de ${AgroState.animals.length} animais`;

    // Eventos nos botões gerados
    bindAnimalTableActions(tbody);

    tbody.querySelectorAll('.btn-quick-associate').forEach(btn => {
      btn.addEventListener('click', () => {
        const animalId = btn.getAttribute('data-animal-id');
        const drawer = document.getElementById('associate-animals-drawer');
        if (drawer) {
          drawer.classList.add('active');
          const searchInput = document.getElementById('drawer-search-input');
          if (searchInput) searchInput.value = animalId;
          showToast(`Animal ${animalId} pronto para associação. Escolha o lote de destino.`);
        }
      });
    });
  }

  function setupAnimalInventoryFilters() {
    const searchInput = document.getElementById('search-animals-input');
    const catSelect = document.getElementById('filter-animal-category');
    const statusSelect = document.getElementById('filter-animal-status');
    const farmSelect = document.getElementById('filter-animal-farm');
    const clearBtn = document.getElementById('btn-clear-animal-filters');

    if (searchInput) searchInput.addEventListener('input', renderAllAnimalsTable);
    if (catSelect) catSelect.addEventListener('change', renderAllAnimalsTable);
    if (statusSelect) statusSelect.addEventListener('change', renderAllAnimalsTable);
    if (farmSelect) farmSelect.addEventListener('change', renderAllAnimalsTable);

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        if (catSelect) catSelect.value = 'all';
        if (statusSelect) statusSelect.value = 'all';
        if (farmSelect) farmSelect.value = 'all';
        renderAllAnimalsTable();
        showToast('Filtros do inventário de animais resetados.');
      });
    }
  }

  // =========================================================================
  // MODAL DE CADASTRO DE NOVO LOTE
  // =========================================================================
  function setupCreateLotModal() {
    const modal = document.getElementById('modal-create-lot');
    const btnOpen = document.getElementById('btn-open-create-lot-modal');
    const btnClose = document.getElementById('btn-close-create-lot-modal');
    const btnCancel = document.getElementById('btn-cancel-create-lot');
    const form = document.getElementById('form-create-lot');
    const inputCode = document.getElementById('new-lot-code');
    const errorCode = document.getElementById('error-lot-code');
    const errorMsg = document.getElementById('error-lot-code-msg');

    if (btnOpen && modal) {
      btnOpen.addEventListener('click', () => {
        if (errorCode) errorCode.style.display = 'none';
        if (form) form.reset();
        modal.classList.add('active');
      });
    }

    function closeModal() {
      if (modal) modal.classList.remove('active');
    }

    if (btnClose) btnClose.addEventListener('click', closeModal);
    if (btnCancel) btnCancel.addEventListener('click', closeModal);

    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const codeVal = inputCode ? inputCode.value.trim().toUpperCase() : '';

        if (!codeVal) return;

        // Validação de Duplicidade (Regra RN-04 / Erro esperado LOTE_CODIGO_DUPLICADO)
        const exists = AgroState.lots.some(l => l.code.toUpperCase() === codeVal);
        if (exists) {
          if (errorCode && errorMsg) {
            errorCode.style.display = 'block';
            errorMsg.textContent = `Código já cadastrado (Erro: LOTE_CODIGO_DUPLICADO - HTTP 409).`;
          }
          return;
        }

        // Estado loading e prevenção de clique duplo
        const submitBtn = document.getElementById('btn-submit-create-lot');
        if (submitBtn) {
          submitBtn.disabled = true;
          const spinner = submitBtn.querySelector('.agro-spinner');
          const btnText = submitBtn.querySelector('.btn-text');
          if (spinner) spinner.style.display = 'inline-block';
          if (btnText) btnText.textContent = 'Salvando...';
        }

        setTimeout(() => {
          // Inserção no estado
          const farmSelect = document.getElementById('new-lot-farm-id');
          const farmText = farmSelect ? farmSelect.options[farmSelect.selectedIndex].text : 'Fazenda Modelo';
          const newLot = {
            code: codeVal,
            status: 'Rascunho',
            statusType: 'neutral',
            farm: farmText,
            farmShort: farmText.split('(')[0].trim(),
            animalsCount: 0,
            entryDate: new Date().toLocaleDateString('pt-BR'),
            daysInManagement: 0,
            readiness: 0,
            lastManagement: '—'
          };

          AgroState.lots.unshift(newLot);

          // Atualiza lista lateral
          const listContainer = document.getElementById('lots-list-items-container');
          if (listContainer) {
            const newItemHtml = `
              <div class="agro-list-item" data-lot-code="${newLot.code}" data-farm-name="${newLot.farmShort}" data-lot-status="${newLot.status}">
                <div class="agro-list-item-left">
                  <div class="agro-list-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                      <circle cx="12" cy="11" r="5"></circle>
                    </svg>
                  </div>
                  <div class="agro-list-item-info">
                    <div style="display:flex; align-items:center; gap:6px;">
                      <span class="agro-list-item-title">${newLot.code}</span>
                      <span class="agro-badge neutral" style="font-size:10px; padding:2px 6px;">Rascunho</span>
                    </div>
                    <div class="agro-list-item-sub">${newLot.farm}</div>
                    <div style="font-size:11px; color:var(--agro-text-muted); margin-top:2px;">0 animais ativos</div>
                  </div>
                </div>
                <div class="agro-list-item-chevron">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </div>
              </div>
            `;
            listContainer.insertAdjacentHTML('afterbegin', newItemHtml);
            setupLotListClicks();
          }

          // Atualiza contador do tab
          const tabCounter = document.getElementById('tab-counter-lots');
          if (tabCounter) tabCounter.textContent = AgroState.lots.length;

          // Restaura botão e fecha modal
          if (submitBtn) {
            submitBtn.disabled = false;
            const spinner = submitBtn.querySelector('.agro-spinner');
            const btnText = submitBtn.querySelector('.btn-text');
            if (spinner) spinner.style.display = 'none';
            if (btnText) btnText.textContent = 'Salvar Lote';
          }

          closeModal();
          selectLot(codeVal);
          showToast(`Lote ${codeVal} criado com sucesso no estado Rascunho.`);
        }, 350);
      });
    }
  }

  // =========================================================================
  // MODAL DE CADASTRO DE NOVO ANIMAL
  // =========================================================================
  function setupCreateAnimalModal() {
    const modal = document.getElementById('modal-create-animal');
    const btnOpen = document.getElementById('btn-open-create-animal-modal');
    const btnClose = document.getElementById('btn-close-create-animal-modal');
    const btnCancel = document.getElementById('btn-cancel-create-animal');
    const form = document.getElementById('form-create-animal');
    const inputIdentifier = document.getElementById('new-animal-identifier');
    const errorIdentifier = document.getElementById('error-animal-identifier');
    const errorIdentifierMsg = document.getElementById('error-animal-identifier-msg');

    if (btnOpen && modal) {
      btnOpen.addEventListener('click', () => {
        if (errorIdentifier) errorIdentifier.style.display = 'none';
        if (form) form.reset();
        modal.classList.add('active');
      });
    }

    function closeModal() {
      if (modal) modal.classList.remove('active');
    }

    if (btnClose) btnClose.addEventListener('click', closeModal);
    if (btnCancel) btnCancel.addEventListener('click', closeModal);

    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const identVal = inputIdentifier ? inputIdentifier.value.trim().toUpperCase() : '';

        if (!identVal) return;

        // Validação de Duplicidade (Regra RN-05 / Erro esperado ANIMAL_IDENTIFICADOR_DUPLICADO)
        const exists = AgroState.animals.some(a => a.identifier.toUpperCase() === identVal);
        if (exists) {
          if (errorIdentifier && errorIdentifierMsg) {
            errorIdentifier.style.display = 'block';
            errorIdentifierMsg.textContent = `Identificador já cadastrado (Erro: ANIMAL_IDENTIFICADOR_DUPLICADO - HTTP 409).`;
          }
          return;
        }

        // Estado loading e prevenção de duplo clique
        const submitBtn = document.getElementById('btn-submit-create-animal');
        if (submitBtn) {
          submitBtn.disabled = true;
          const spinner = submitBtn.querySelector('.agro-spinner');
          const btnText = submitBtn.querySelector('.btn-text');
          if (spinner) spinner.style.display = 'inline-block';
          if (btnText) btnText.textContent = 'Cadastrando...';
        }

        setTimeout(() => {
          const rfidVal = document.getElementById('new-animal-rfid') ? document.getElementById('new-animal-rfid').value.trim() : '';
          const catVal = document.getElementById('new-animal-category') ? document.getElementById('new-animal-category').value : 'Bovino Macho';
          const farmVal = document.getElementById('new-animal-farm') ? document.getElementById('new-animal-farm').value : 'Fazenda Modelo';
          const birthVal = document.getElementById('new-animal-birthdate') ? document.getElementById('new-animal-birthdate').value : '2023-04-15';

          const newAnimal = {
            identifier: identVal,
            rfid: rfidVal || null,
            category: catVal,
            birthDate: birthVal ? birthVal.split('-').reverse().join('/') : '15/04/2023',
            farm: farmVal.split('(')[0].trim(),
            lotCode: null,
            associatedAt: null,
            status: 'Disponível',
            timeline: [
              {
                date: new Date().toLocaleDateString('pt-BR'),
                title: 'Nascimento e Cadastro SISBOV',
                meta: `${farmVal} · Categoria ${catVal} · Animal disponível para associação`,
                active: false
              }
            ]
          };

          AgroState.animals.unshift(newAnimal);

          // Atualiza drawer animals se necessário
          AgroState.drawerAnimals.unshift({
            id: identVal,
            category: catVal,
            available: true,
            status: 'Disponível'
          });

          // Atualiza tabela geral de animais
          renderAllAnimalsTable();
          populateDrawerAnimals();

          // Atualiza contador do tab
          const tabCounter = document.getElementById('tab-counter-animals');
          if (tabCounter) tabCounter.textContent = AgroState.animals.length;

          if (submitBtn) {
            submitBtn.disabled = false;
            const spinner = submitBtn.querySelector('.agro-spinner');
            const btnText = submitBtn.querySelector('.btn-text');
            if (spinner) spinner.style.display = 'none';
            if (btnText) btnText.textContent = 'Salvar Animal';
          }

          closeModal();
          showToast(`Animal ${identVal} cadastrado com sucesso com identificação oficial.`);
        }, 350);
      });
    }
  }

  // =========================================================================
  // MODAL DE HISTÓRICO TEMPORAL DO ANIMAL
  // =========================================================================
  function setupAnimalHistoryModal() {
    const modal = document.getElementById('modal-animal-history');
    const btnClose = document.getElementById('btn-close-animal-history-modal');
    const btnFooter = document.getElementById('btn-close-history-footer');

    function closeModal() {
      if (modal) modal.classList.remove('active');
    }

    if (btnClose) btnClose.addEventListener('click', closeModal);
    if (btnFooter) btnFooter.addEventListener('click', closeModal);
  }

  function openAnimalHistoryModal(animalIdentifier) {
    const modal = document.getElementById('modal-animal-history');
    if (!modal) return;

    const animal = AgroState.animals.find(a => a.identifier === animalIdentifier) || {
      identifier: animalIdentifier,
      rfid: '982000365892100',
      category: 'Bovino Macho',
      status: 'Desassociado (Histórico)',
      timeline: [
        { date: '10/01/2026 a 20/03/2026', title: 'Associação Encerrada - Lote LT-2025-090', meta: '69 dias de permanência regular · Preservação histórica RN-06', active: false },
        { date: '15/09/2021', title: 'Cadastro Inicial e Brincagem', meta: 'Fazenda Modelo', active: false }
      ]
    };

    const titleElem = document.getElementById('history-modal-title');
    const subElem = document.getElementById('history-modal-subtitle');
    const badgeContainer = document.getElementById('history-current-status-badge');
    const rfidElem = document.getElementById('history-current-rfid');
    const timelineContainer = document.getElementById('animal-history-timeline-container');

    if (titleElem) titleElem.textContent = `Histórico Temporal: ${animal.identifier}`;
    if (subElem) subElem.textContent = `${animal.identifier} · ${animal.category} · ${animal.farm || 'Fazenda Modelo'}`;
    if (rfidElem) rfidElem.textContent = animal.rfid || 'Sem chip RFID';

    if (badgeContainer) {
      if (animal.lotCode) {
        badgeContainer.innerHTML = `<span class="agro-badge info" style="font-size:11.5px;">Ativo no Lote ${animal.lotCode}</span>`;
      } else {
        badgeContainer.innerHTML = `<span class="agro-badge success" style="font-size:11.5px;">Disponível (Sem Lote)</span>`;
      }
    }

    if (timelineContainer && animal.timeline) {
      let timelineHtml = '';
      animal.timeline.forEach(event => {
        const dotClass = event.active ? 'active' : 'closed';
        timelineHtml += `
          <div class="agro-timeline-item">
            <div class="agro-timeline-dot ${dotClass}"></div>
            <div class="agro-timeline-content">
              <div class="agro-timeline-header">
                <span class="agro-timeline-title">${event.title}</span>
                <span class="agro-timeline-date">${event.date}</span>
              </div>
              <div class="agro-timeline-meta">${event.meta}</div>
            </div>
          </div>
        `;
      });
      timelineContainer.innerHTML = timelineHtml;
    }

    modal.classList.add('active');
  }

  // =========================================================================
  // GAVETA DE ASSOCIAÇÃO (DRAWER LATERAL)
  // =========================================================================
  function setupAssociateDrawer() {
    const btnOpenDrawer = document.getElementById('btn-open-associate-drawer');
    const drawerOverlay = document.getElementById('associate-animals-drawer');
    const btnCloseDrawer = document.getElementById('btn-close-associate-drawer');
    const searchInput = document.getElementById('drawer-search-input');
    const filterCat = document.getElementById('drawer-filter-cat');
    const selectAll = document.getElementById('select-all-drawer');
    const btnAddToList = document.getElementById('btn-add-animals-to-list');

    if (btnOpenDrawer && drawerOverlay) {
      btnOpenDrawer.addEventListener('click', () => {
        populateDrawerAnimals();
        drawerOverlay.classList.add('active');
      });
    }

    if (btnCloseDrawer && drawerOverlay) {
      btnCloseDrawer.addEventListener('click', () => {
        drawerOverlay.classList.remove('active');
      });
    }

    if (drawerOverlay) {
      drawerOverlay.addEventListener('click', (e) => {
        if (e.target === drawerOverlay) drawerOverlay.classList.remove('active');
      });
    }

    if (searchInput) {
      searchInput.addEventListener('input', filterDrawerList);
    }
    if (filterCat) {
      filterCat.addEventListener('change', filterDrawerList);
    }

    if (selectAll) {
      selectAll.addEventListener('change', () => {
        const checkboxes = document.querySelectorAll('.drawer-animal-checkbox:not(:disabled)');
        checkboxes.forEach(cb => cb.checked = selectAll.checked);
        updateDrawerSelectedCount();
      });
    }

    if (btnAddToList) {
      btnAddToList.addEventListener('click', () => {
        const selectedCheckboxes = Array.from(document.querySelectorAll('.drawer-animal-checkbox:checked'));
        if (selectedCheckboxes.length === 0) {
          alert('Selecione ao menos um animal disponível na lista.');
          return;
        }

        const conflictItem = selectedCheckboxes.find(cb => cb.getAttribute('data-conflict') === 'true');
        if (conflictItem) {
          const animalId = conflictItem.getAttribute('data-animal-id') || 'BR-123456790-1';
          openValidationErrorModal(
            'Erro de Validação: Conflito de Associação Ativa',
            `Animal ${animalId} já possui associação ativa em outro lote. A regra de negócio (RN-06) impede a duplicidade de vínculo simultâneo.`,
            'ANIMAL_JA_ASSOCIADO_CONFLITO (HTTP 409)',
            `Animal ${animalId} está ativo no lote LT-2026-003.`
          );
          return;
        }

        // Sucesso na associação
        selectedCheckboxes.forEach(cb => {
          const animalId = cb.getAttribute('data-animal-id');
          const animal = AgroState.animals.find(a => a.identifier === animalId);
          if (animal) {
            animal.lotCode = AgroState.selectedLotId;
            animal.status = 'Em Lote';
            animal.associatedAt = new Date().toLocaleDateString('pt-BR') + ' ' + new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            animal.timeline.unshift({
              date: animal.associatedAt,
              title: `Associação Ativa ao Lote ${AgroState.selectedLotId}`,
              meta: `Associação realizada no sistema com integridade e auditoria transacional.`,
              active: true
            });
          }
        });

        drawerOverlay.classList.remove('active');
        renderCurrentLotAnimalsTable(AgroState.selectedLotId);
        renderAllAnimalsTable();
        showToast(`${selectedCheckboxes.length} animais associados com sucesso ao lote ${AgroState.selectedLotId}!`);
      });
    }
  }

  function populateDrawerAnimals() {
    const tbody = document.getElementById('drawer-animals-tbody');
    if (!tbody) return;

    let rowsHtml = '';
    AgroState.drawerAnimals.forEach(item => {
      const isConflict = !item.available;
      const statusBadge = isConflict
        ? `<span class="agro-badge danger" style="font-size:11px;">Já em outro lote</span>`
        : `<span class="agro-badge success" style="font-size:11px;">Disponível</span>`;

      const idStyle = isConflict ? 'color:#991b1b;' : '';
      const rowBg = isConflict ? 'background-color:#fff9fa;' : '';

      rowsHtml += `
        <tr style="${rowBg}">
          <td>
            <input type="checkbox" class="agro-checkbox drawer-animal-checkbox" data-animal-id="${item.id}" data-conflict="${isConflict}">
          </td>
          <td><strong style="${idStyle}">${item.id}</strong></td>
          <td>${item.category}</td>
          <td>${statusBadge}</td>
        </tr>
      `;
    });

    tbody.innerHTML = rowsHtml;

    tbody.querySelectorAll('.drawer-animal-checkbox').forEach(cb => {
      cb.addEventListener('change', updateDrawerSelectedCount);
    });

    updateDrawerSelectedCount();
  }

  function filterDrawerList() {
    const searchInput = document.getElementById('drawer-search-input');
    const catSelect = document.getElementById('drawer-filter-cat');
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const cat = catSelect ? catSelect.value : 'all';

    document.querySelectorAll('#drawer-animals-tbody tr').forEach(row => {
      const text = row.textContent.toLowerCase();
      const matchQuery = !query || text.includes(query);
      const matchCat = cat === 'all' || text.includes(cat.toLowerCase());
      row.style.display = (matchQuery && matchCat) ? '' : 'none';
    });
  }

  function updateDrawerSelectedCount() {
    const count = document.querySelectorAll('.drawer-animal-checkbox:checked').length;
    const countLabel = document.getElementById('drawer-selected-count');
    if (countLabel) countLabel.textContent = `Selecionados: ${count}`;
  }

  // =========================================================================
  // SETUP FARMS MODULE (LEGADO S1 PRESERVADO)
  // =========================================================================
  function setupFarmsModule() {
    document.querySelectorAll('.agro-list-item[data-farm-id]').forEach(card => {
      card.addEventListener('click', () => {
        const farmId = parseInt(card.getAttribute('data-farm-id'), 10);
        selectFarm(farmId);
      });
    });

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
  }

  function selectFarm(farmId) {
    AgroState.selectedFarmId = farmId;
    const farm = AgroState.farms.find(f => f.id === farmId);
    if (!farm) return;

    document.querySelectorAll('.agro-list-item[data-farm-id]').forEach(card => {
      if (parseInt(card.getAttribute('data-farm-id'), 10) === farmId) {
        card.classList.add('selected');
      } else {
        card.classList.remove('selected');
      }
    });

    const detailTitle = document.getElementById('farm-detail-name');
    const detailLocation = document.getElementById('farm-detail-location');
    if (detailTitle) detailTitle.textContent = farm.name;
    if (detailLocation) detailLocation.textContent = `${farm.city} - ${farm.uf}`;

    const inputName = document.getElementById('farm-input-name');
    const inputCar = document.getElementById('farm-input-car');
    const selectCity = document.getElementById('farm-select-city');
    const selectUf = document.getElementById('farm-select-uf');
    const inputCoord = document.getElementById('farm-input-coord');

    if (inputName) inputName.value = farm.name;
    if (inputCar) inputCar.value = farm.car;
    if (selectCity) selectCity.value = farm.city;
    if (selectUf) selectUf.value = farm.uf;
    if (inputCoord) inputCoord.value = farm.coordinates;
  }

  // =========================================================================
  // MODALS GLOBAIS DE VALIDAÇÃO E CONFIRMAÇÃO
  // =========================================================================
  function setupModals() {
    const valModal = document.getElementById('modal-validation-error');
    const btnCloseVal = document.getElementById('btn-close-validation-modal');
    const btnUnderVal = document.getElementById('btn-understand-validation');

    if (btnCloseVal && valModal) {
      btnCloseVal.addEventListener('click', () => valModal.classList.remove('active'));
    }
    if (btnUnderVal && valModal) {
      btnUnderVal.addEventListener('click', () => {
        valModal.classList.remove('active');
        document.querySelectorAll('.drawer-animal-checkbox[data-conflict="true"]').forEach(cb => cb.checked = false);
        updateDrawerSelectedCount();
      });
    }

    const confModal = document.getElementById('modal-confirm-action');
    const btnCloseConf = document.getElementById('btn-close-confirm-modal');
    const btnCancelConf = document.getElementById('btn-cancel-confirm');

    if (btnCloseConf && confModal) {
      btnCloseConf.addEventListener('click', () => confModal.classList.remove('active'));
    }
    if (btnCancelConf && confModal) {
      btnCancelConf.addEventListener('click', () => confModal.classList.remove('active'));
    }
  }

  function openValidationErrorModal(title, description, errorCode, detail) {
    const modal = document.getElementById('modal-validation-error');
    if (!modal) return;

    const headlineElem = document.getElementById('val-modal-headline');
    const descElem = document.getElementById('val-modal-description');
    const codeElem = document.getElementById('val-modal-conflict-code');
    const detailElem = document.getElementById('val-modal-conflict-detail');

    if (headlineElem && title) headlineElem.textContent = title;
    if (descElem && description) descElem.textContent = description;
    if (codeElem && errorCode) codeElem.textContent = `Código de Erro: ${errorCode}`;
    if (detailElem && detail) detailElem.innerHTML = detail;

    modal.classList.add('active');
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

    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

    newConfirmBtn.addEventListener('click', () => {
      modal.classList.remove('active');
      if (typeof onConfirmCallback === 'function') {
        onConfirmCallback();
      }
    });
  }

  // Initialization
  function init() {
    document.querySelectorAll('.agro-nav-item[data-screen]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const screen = btn.getAttribute('data-screen');
        switchScreen(screen);
      });
    });

    if (window.location.hash) {
      const hashScreen = window.location.hash.replace('#', '');
      if (['dashboard', 'fazendas', 'lotes'].includes(hashScreen)) {
        switchScreen(hashScreen);
      }
    }

    setupFarmsModule();
    setupLotsModule();
    setupModals();
  }

  // Public API
  window.AgroTracer = {
    switchScreen,
    switchSubTab,
    showToast,
    openValidationErrorModal,
    openConfirmModal,
    openAnimalHistoryModal,
    state: AgroState
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
