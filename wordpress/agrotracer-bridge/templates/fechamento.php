<?php
/**
 * AgroTracer Lot Closing & Abate Screen Template (Sprint 4 - Task S4-T04)
 * Épico: [EP-S4] Sprint 4 — Fechamento e CarbonEngine
 * Escopo: Tela de fechamento/abate com resumo, unidades e confirmação; prevenção de clique duplo; erro acionável.
 * Critérios de aceite:
 * 1. Campos e unidades claros (data AAAA-MM-DD, cabeças, kg peso vivo, % rendimento carcaça)
 * 2. Erro acionável com orientação de correção (422 associações parciais, abate superior, datas, 409 lote fechado)
 * 3. Sem submissão duplicada (botão desabilitado durante submit e trava de estado)
 * Cuidado de Engenharia: Prevenção estrita de duplo clique e conformidade com RN-09, RN-10, RN-11, RN-19 e RN-21.
 */
if (!defined('ABSPATH')) {
    // Direct access security fallback
}
?>
<section id="screen-fechamento" class="agro-screen" aria-labelledby="fechamento-screen-title">

  <!-- Cabeçalho do Módulo de Fechamento -->
  <div class="agro-screen-header">
    <div class="agro-screen-header-left">
      <div class="agro-screen-badge-container">
        <span class="agro-badge info" style="font-size: 11px; padding: 2px 8px;">Sprint 4 — Fechamento &amp; CarbonEngine</span>
        <span class="agro-badge neutral" style="font-size: 11px; padding: 2px 8px;">RN-09 / RN-10 / RN-11 / RN-21</span>
      </div>
      <h1 id="fechamento-screen-title" class="agro-screen-title" style="margin-top: 4px;">
        Fechamento de Lote &amp; Cálculo de Emissões
      </h1>
      <p class="agro-screen-subtitle">
        Encerramento oficial do lote para abate com cálculo determinístico de emissões (CarbonEngine) e geração de snapshot imutável.
      </p>
    </div>

    <div class="agro-screen-header-actions">
      <button type="button" class="agro-btn agro-btn-secondary" id="btn-back-to-lotes" onclick="AgroTracer.switchScreen('lotes')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;margin-right:6px;">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        <span>Voltar aos Lotes</span>
      </button>
    </div>
  </div>

  <!-- Alerta de Imutabilidade e Transparência Metodológica (RN-11 / RN-21 / ADR S4-T01-T03) -->
  <div class="agro-alert warning" style="margin-bottom: 20px; display: flex; align-items: flex-start; gap: 12px;" role="note">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:22px;height:22px;flex-shrink:0;margin-top:2px;color:#d97706;">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
      <line x1="12" y1="9" x2="12" y2="13"></line>
      <line x1="12" y1="17" x2="12.01" y2="17"></line>
    </svg>
    <div style="font-size: 12.5px; line-height: 1.5; color: #92400e;">
      <strong>Atenção: Ação Irreversível com Snapshot Imutável (RN-11 / RN-21).</strong>
      Ao concluir o fechamento, o status do lote migrará definitivamente para <strong>FECHADO</strong>.
      Todas as entradas, fatores de manejo e métricas calculadas pelo <code>CarbonEngine</code> serão gravadas em snapshot protegido por triggers do PostgreSQL que impedem edição ou exclusão. Novos manejos posteriores serão bloqueados (HTTP 409).
    </div>
  </div>

  <!-- Banner de Erro Acionável com Orientação de Correção (Critério de Aceite 2) -->
  <div id="fechamento-actionable-error-banner" class="agro-alert danger" style="display: none; margin-bottom: 24px; padding: 16px 18px; border-radius: var(--agro-radius-md);" role="alert">
    <div style="display: flex; align-items: flex-start; gap: 14px;">
      <div style="background-color: #fee2e2; color: #dc2626; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width: 18px; height: 18px;">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <div style="flex: 1;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <strong id="fechamento-error-code-badge" class="agro-badge danger" style="font-size: 11px;">ERRO_FECHAMENTO</strong>
          <span style="font-size: 13.5px; font-weight: 700; color: #991b1b;" id="fechamento-error-title">Falha no Fechamento do Lote</span>
        </div>
        <p id="fechamento-error-message" style="margin: 0 0 8px 0; font-size: 13px; color: #7f1d1d; line-height: 1.45;">
          A operação não pôde ser concluída devido a pré-condições não atendidas.
        </p>
        <div id="fechamento-error-action-box" style="background: #ffffff; border: 1px solid #fecaca; border-radius: 6px; padding: 10px 12px; margin-top: 6px;">
          <strong style="display: block; font-size: 12px; color: #991b1b; margin-bottom: 3px;">Como corrigir esta situação:</strong>
          <span id="fechamento-error-action-guide" style="font-size: 12.5px; color: #374151; line-height: 1.4;">
            Instrução acionável de correção.
          </span>
          <div id="fechamento-error-action-button-container" style="margin-top: 8px;">
            <button type="button" id="btn-fechamento-error-action" class="agro-btn agro-btn-secondary" style="font-size: 12px; padding: 4px 10px;">
              Ir para Tela de Manejo
            </button>
          </div>
        </div>
        <div style="margin-top: 8px; font-size: 11px; color: #9ca3af;">
          ID de Correlação: <code id="fechamento-error-correlation-id">corr-preview-id</code>
        </div>
      </div>
      <button type="button" id="btn-dismiss-fechamento-error" class="agro-toast-close" style="color: #991b1b; font-size: 18px;" aria-label="Fechar alerta">&times;</button>
    </div>
  </div>

  <!-- Barra de Filtros e Seleção do Lote -->
  <div class="agro-filter-bar" style="margin-bottom: 24px; background: #fff; padding: 16px 20px; border: 1px solid var(--agro-border); border-radius: var(--agro-radius-md);">
    <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px;">
      <div style="display: flex; align-items: center; gap: 12px; flex: 1; min-width: 300px;">
        <label for="select-fechamento-lote" style="font-size: 13px; font-weight: 600; color: var(--agro-text-primary); white-space: nowrap;">
          Selecionar Lote para Fechamento:
        </label>
        <select id="select-fechamento-lote" class="agro-select" style="min-width: 260px;">
          <option value="1" data-code="LT-2026-001" data-farm="Fazenda Modelo" data-animals="50" data-status="EM_MANEJO" data-days="90">
            LT-2026-001 (Fazenda Modelo — 50 animais · Em manejo)
          </option>
          <option value="2" data-code="LT-2026-003" data-farm="Fazenda São Bento" data-animals="45" data-status="FECHADO" data-days="150">
            LT-2026-003 (Fazenda São Bento — 45 animais · Fechado)
          </option>
          <option value="3" data-code="LT-2025-090" data-farm="Fazenda Esperança" data-animals="12" data-status="EM_MANEJO" data-days="45">
            LT-2025-090 (Fazenda Esperança — 12 animais · Em manejo)
          </option>
          <option value="4" data-code="LT-2024-087" data-farm="Fazenda Alvorada" data-animals="0" data-status="RASCUNHO" data-days="0">
            LT-2024-087 (Fazenda Alvorada — Vazio · Rascunho)
          </option>
        </select>
      </div>

      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 12.5px; color: var(--agro-text-muted);">Status do Lote:</span>
        <span id="fechamento-lote-status-badge" class="agro-badge warning" style="font-size: 11.5px;">Em manejo</span>
      </div>
    </div>
  </div>

  <!-- Layout em 2 Colunas: Resumo do Lote vs Formulário de Fechamento -->
  <div class="agro-master-detail-grid" style="grid-template-columns: 1fr 1.25fr; gap: 24px; align-items: start;">

    <!-- Coluna Esquerda: Resumo Pré-Fechamento e Verificação de Pré-condições -->
    <div class="agro-sidebar-card" style="background:#fff; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:20px;">
      <div style="border-bottom: 1px solid var(--agro-border); padding-bottom: 14px; margin-bottom: 16px;">
        <span class="agro-badge neutral" style="font-size: 11px; margin-bottom: 6px;">Pré-condições RN-09 &amp; RN-10</span>
        <h2 style="font-size: 16px; font-weight: 700; color: var(--agro-text-primary); margin: 0;">
          Resumo do Lote e Manejos
        </h2>
      </div>

      <!-- Dados de Identificação -->
      <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
        <div style="display:flex; justify-content:space-between; font-size:13px;">
          <span style="color:var(--agro-text-muted);">Código do Lote:</span>
          <strong id="resumo-lote-codigo" style="color:var(--agro-text-primary);">LT-2026-001</strong>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px;">
          <span style="color:var(--agro-text-muted);">Fazenda:</span>
          <span id="resumo-lote-fazenda" style="color:var(--agro-text-primary); font-weight:500;">Fazenda Modelo (Aquidauana/MS)</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px;">
          <span style="color:var(--agro-text-muted);">Animais no Último Manejo:</span>
          <strong id="resumo-lote-animais" style="color:var(--agro-primary);">50 cabeças</strong>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px;">
          <span style="color:var(--agro-text-muted);">Período de Manejo Registrado:</span>
          <span id="resumo-lote-periodo" style="color:var(--agro-text-primary); font-weight:500;">01/01/2026 a 30/05/2026 (150 dias)</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px;">
          <span style="color:var(--agro-text-muted);">Conjunto de Parâmetros:</span>
          <span id="resumo-lote-param-set" class="agro-badge info" style="font-size:11px;">v1.0-2026 [SYNTHETIC]</span>
        </div>
      </div>

      <!-- Checklist de Pré-Condições Obrigatórias -->
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 20px;">
        <strong style="display:block; font-size:12.5px; color:#334155; margin-bottom:8px;">
          Verificação Automática de Pré-condições:
        </strong>
        <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #475569; display: flex; flex-direction: column; gap: 6px;">
          <li id="check-status-lote">✓ Status do lote é <strong>EM_MANEJO</strong> (RN-04)</li>
          <li id="check-manejo-existente">✓ Manejo nutricional presente e contínuo (RN-08)</li>
          <li id="check-associacoes-completas">✓ Associações de animais completas sem lacunas (RN-09/10)</li>
          <li id="check-param-publicado">✓ Parâmetros publicados e dentro da vigência (RN-16)</li>
          <li id="check-data-abate-coerente">✓ Data de abate compatível com o fim do manejo</li>
        </ul>
      </div>

      <!-- Estado Quando Lote Já Está Fechado -->
      <div id="box-lote-ja-fechado" style="display: none; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 14px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
          <svg viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" style="width:18px;height:18px;">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          <strong style="font-size: 13px; color: #1e40af;">Lote Já Fechado e Certificável</strong>
        </div>
        <p style="margin: 0; font-size: 12px; color: #1e3a8a; line-height: 1.4;">
          Este lote já concluiu o fechamento e possui snapshot imutável registrado. Veja os resultados na seção abaixo.
        </p>
      </div>
    </div>

    <!-- Coluna Direita: Formulário de Fechamento com Campos e Unidades Claras -->
    <div class="agro-card" style="background:#fff; border:1px solid var(--agro-border); border-radius:var(--agro-radius-md); padding:24px;">
      <div style="border-bottom: 1px solid var(--agro-border); padding-bottom: 14px; margin-bottom: 20px;">
        <h2 style="font-size: 18px; font-weight: 700; color: var(--agro-text-primary); margin: 0 0 4px 0;">
          Parâmetros de Abate e Confirmação
        </h2>
        <p style="margin: 0; font-size: 12.5px; color: var(--agro-text-muted);">
          Informe os dados zootécnicos reais de abate para consolidação das emissões totais e intensidade de carbono.
        </p>
      </div>

      <form id="form-fechar-lote" novalidate>

        <!-- Campo 1: Data de Abate -->
        <div class="agro-form-group" style="margin-bottom: 18px;">
          <label for="fechamento-data-abate" style="display:block; font-size:13px; font-weight:600; color:var(--agro-text-primary); margin-bottom:6px;">
            Data do Abate <span style="color:#ef4444;">*</span>
          </label>
          <input type="date" id="fechamento-data-abate" class="agro-input" style="width:100%;" required value="2026-06-01">
          <span style="font-size:11.5px; color:var(--agro-text-muted); display:block; margin-top:4px;">
            Unidade: <strong>Data (AAAA-MM-DD)</strong>. Deve ser igual ou posterior à última data de manejo (<span id="data-minima-abate-hint">30/05/2026</span>).
          </span>
          <span id="fechamento-data-abate-error" class="agro-field-error" style="display:none; color:#dc2626; font-size:11.5px; margin-top:2px;"></span>
        </div>

        <!-- Campo 2: Quantidade de Animais Abatidos -->
        <div class="agro-form-group" style="margin-bottom: 18px;">
          <label for="fechamento-animais-abate" style="display:block; font-size:13px; font-weight:600; color:var(--agro-text-primary); margin-bottom:6px;">
            Quantidade de Animais Abatidos <span style="color:#ef4444;">*</span>
          </label>
          <div style="display:flex; align-items:center; gap:10px;">
            <input type="number" id="fechamento-animais-abate" class="agro-input" min="1" max="10000" step="1" value="50" style="width:160px;" required>
            <span style="font-size:13px; font-weight:600; color:var(--agro-text-secondary);">cabeças (cab)</span>
          </div>
          <span style="font-size:11.5px; color:var(--agro-text-muted); display:block; margin-top:4px;">
            Unidade: <strong>Inteiro positivo</strong>. Não pode exceder os <strong id="max-animais-permitidos-hint">50 animais</strong> comprovados no último manejo.
          </span>
          <span id="fechamento-animais-abate-error" class="agro-field-error" style="display:none; color:#dc2626; font-size:11.5px; margin-top:2px;"></span>
        </div>

        <!-- Campo 3: Peso Médio de Abate (kg) -->
        <div class="agro-form-group" style="margin-bottom: 18px;">
          <label for="fechamento-peso-medio" style="display:block; font-size:13px; font-weight:600; color:var(--agro-text-primary); margin-bottom:6px;">
            Peso Médio de Abate (Peso Vivo) <span style="color:#ef4444;">*</span>
          </label>
          <div style="display:flex; align-items:center; gap:10px;">
            <input type="number" id="fechamento-peso-medio" class="agro-input" min="100.0" max="1200.0" step="0.01" value="540.00" style="width:160px;" required>
            <span style="font-size:13px; font-weight:600; color:var(--agro-text-secondary);">kg / cabeça (kg vivo)</span>
          </div>
          <span style="font-size:11.5px; color:var(--agro-text-muted); display:block; margin-top:4px;">
            Unidade: <strong>Quilogramas (kg)</strong>. Utilizado como base para a massa total de carcaça.
          </span>
          <span id="fechamento-peso-medio-error" class="agro-field-error" style="display:none; color:#dc2626; font-size:11.5px; margin-top:2px;"></span>
        </div>

        <!-- Campo 4: Rendimento de Carcaça (%) -->
        <div class="agro-form-group" style="margin-bottom: 22px;">
          <label for="fechamento-rendimento" style="display:block; font-size:13px; font-weight:600; color:var(--agro-text-primary); margin-bottom:6px;">
            Rendimento de Carcaça (RC) <span style="color:#ef4444;">*</span>
          </label>
          <div style="display:flex; align-items:center; gap:10px;">
            <input type="number" id="fechamento-rendimento" class="agro-input" min="1.0" max="100.0" step="0.01" value="53.00" style="width:160px;" required>
            <span style="font-size:13px; font-weight:600; color:var(--agro-text-secondary);">% (fração decimal: <span id="rendimento-fração-preview">0.53</span>)</span>
          </div>
          <span style="font-size:11.5px; color:var(--agro-text-muted); display:block; margin-top:4px;">
            Unidade: <strong>Percentual entre 1% e 100%</strong> (convertido em decimal de 0 a 1 para o CarbonEngine).
          </span>
          <span id="fechamento-rendimento-error" class="agro-field-error" style="display:none; color:#dc2626; font-size:11.5px; margin-top:2px;"></span>
        </div>

        <!-- Card de Pré-visualização Zootécnica Dinâmica -->
        <div style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; margin-bottom: 24px;">
          <span style="display:block; font-size:11px; text-transform:uppercase; font-weight:700; color:#475569; letter-spacing:0.5px; margin-bottom:8px;">
            Pré-visualização Zootécnica de Carcaça:
          </span>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div>
              <span style="font-size: 11.5px; color: #64748b; display: block;">Peso Total Vivo:</span>
              <strong id="preview-peso-vivo-total" style="font-size: 14px; color: #1e293b;">27.000,00 kg</strong>
            </div>
            <div>
              <span style="font-size: 11.5px; color: #64748b; display: block;">Massa Total de Carcaça:</span>
              <strong id="preview-carcaca-total" style="font-size: 14px; color: var(--agro-primary);">14.310,00 kg carcaça</strong>
            </div>
          </div>
        </div>

        <!-- Botões de Ação com Prevenção de Duplo Clique (Cuidado de Engenharia) -->
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 12px;">
          <button type="button" id="btn-cancel-fechamento" class="agro-btn agro-btn-secondary" onclick="AgroTracer.switchScreen('lotes')">
            Cancelar
          </button>
          <button type="submit" id="btn-submit-fechamento" class="agro-btn agro-btn-primary" style="min-width: 200px;">
            <svg id="spinner-fechamento" class="agro-spinner" viewBox="0 0 24 24" style="display:none; width:16px;height:16px;margin-right:8px;" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" stroke-width="4" style="opacity:0.25;"></circle>
              <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" style="opacity:0.75;"></path>
            </svg>
            <span id="btn-submit-fechamento-text">Fechar Lote e Calcular</span>
          </button>
        </div>

      </form>
    </div>

  </div>

  <!-- Painel de Resultados do Fechamento e Snapshot Consolidado (Exibido após Fechamento) -->
  <div id="fechamento-resultado-card" style="display: none; margin-top: 30px; background: #ffffff; border: 2px solid #22c55e; border-radius: var(--agro-radius-md); padding: 24px;">
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 20px;">
      <div style="display: flex; align-items: center; gap: 12px;">
        <div style="background: #dcfce7; color: #15803d; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width: 22px; height: 22px;">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
        <div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #166534;">
              Fechamento Concluído com Sucesso!
            </h3>
            <span class="agro-badge success" style="font-size: 11px;">Status: FECHADO</span>
          </div>
          <p style="margin: 3px 0 0 0; font-size: 12.5px; color: #64748b;">
            Snapshot imutável registrado e transação confirmada no PostgreSQL.
          </p>
        </div>
      </div>
      <span class="agro-badge info" style="font-size: 12px;" id="res-versao-metodo">Método: CARBONENGINE-MVP-1.0</span>
    </div>

    <!-- Grid de Métricas Oficiais do CarbonEngine -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px;">
      
      <!-- Card Emissão Total -->
      <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px;">
        <span style="font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">
          Emissão Total Acumulada
        </span>
        <div style="display: flex; align-items: baseline; gap: 6px; margin-top: 6px;">
          <strong id="res-emissao-total" style="font-size: 26px; font-weight: 800; color: #0f172a;">13.650,00</strong>
          <span style="font-size: 14px; font-weight: 600; color: #475569;">kg CO₂e</span>
        </div>
        <span style="font-size: 11.5px; color: #94a3b8; display: block; margin-top: 4px;">
          Soma de períodos zootécnicos inclusivos
        </span>
      </div>

      <!-- Card Intensidade de Carbono -->
      <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 18px;">
        <span style="font-size: 12px; font-weight: 600; color: #166534; text-transform: uppercase; letter-spacing: 0.5px;">
          Intensidade de Emissões
        </span>
        <div style="display: flex; align-items: baseline; gap: 6px; margin-top: 6px;">
          <strong id="res-intensidade" style="font-size: 26px; font-weight: 800; color: #15803d;">0,954</strong>
          <span style="font-size: 14px; font-weight: 600; color: #166534;">kg CO₂e / kg carcaça</span>
        </div>
        <span style="font-size: 11.5px; color: #16a34a; display: block; margin-top: 4px;">
          Divisão exata por massa de carcaça (sem divisão por zero)
        </span>
      </div>

      <!-- Card Snapshot & Versão -->
      <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px;">
        <span style="font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">
          Identificadores de Auditoria
        </span>
        <div style="margin-top: 8px; font-size: 12.5px; color: #334155; display: flex; flex-direction: column; gap: 4px;">
          <div>Fechamento ID: <strong id="res-fechamento-id">#101</strong></div>
          <div>Parâmetro Set ID: <strong id="res-param-id">#1 (v1.0-2026)</strong></div>
          <div>Correlation ID: <code id="res-correlation-id" style="font-size:11px;">8d7c3f2a-9e4b</code></div>
        </div>
      </div>

    </div>

    <!-- Ações Finais Pós-Fechamento -->
    <div style="display: flex; justify-content: flex-end; gap: 12px;">
      <button type="button" class="agro-btn agro-btn-secondary" onclick="AgroTracer.switchScreen('manejo')">
        Ver Timeline de Manejo
      </button>
      <button type="button" class="agro-btn agro-btn-primary" onclick="AgroTracer.switchScreen('lotes')">
        Retornar ao Painel de Lotes
      </button>
    </div>
  </div>

</section>
