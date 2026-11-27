<?php
/**
 * Página Pública de Verificação de Certificado (Sprint 5 - Task S5-T05 / RN-13)
 *
 * Exibe exclusivamente o DTO minimizado do certificado consultado via token opaco,
 * sem dados pessoais do produtor, sem identificadores de animais, sem source_uri
 * e com badges semânticos ("success" para Válido, "danger" para Revogado/Invalidado).
 *
 * @package AgroTracerBridge
 */

if (!defined('ABSPATH')) {
    // Allow isolated rendering in PHPUnit / standalone preview
}

$agro_esc = static function ($value): string {
    $text = (string) $value;
    return function_exists('esc_html')
        ? esc_html($text)
        : htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
};

$agro_esc_attr = static function ($value): string {
    $text = (string) $value;
    return function_exists('esc_attr')
        ? esc_attr($text)
        : htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
};

$agro_fmt_metric = static function ($value, int $max_decimals = 6): string {
    if ($value === null || $value === '') {
        return '—';
    }
    $raw = trim((string) $value);
    if (!preg_match('/^-?\d+(?:\.(\d+))?$/', $raw, $m)) {
        return $raw;
    }
    $decimals = $m[1] ?? '';
    if (strlen($decimals) <= $max_decimals) {
        return $raw;
    }
    $trimmed = rtrim($decimals, '0');
    if (strlen($trimmed) < 2) {
        $trimmed = str_pad($trimmed, 2, '0');
    }
    if (strlen($trimmed) <= $max_decimals) {
        $int_part = explode('.', $raw, 2)[0];
        return $int_part . '.' . $trimmed;
    }
    return number_format((float) $raw, $max_decimals, '.', '');
};

$agro_fmt_date = static function ($value): string {
    $raw = trim((string) ($value ?? ''));
    if (preg_match('/^(\d{4})-(\d{2})-(\d{2})$/', $raw, $m)) {
        return $m[3] . '/' . $m[2] . '/' . $m[1];
    }
    return $raw !== '' ? $raw : '—';
};

$agro_fmt_datetime = static function ($value): string {
    $raw = trim((string) ($value ?? ''));
    if (preg_match('/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/', $raw, $m)) {
        return $m[3] . '/' . $m[2] . '/' . $m[1] . ' ' . $m[4] . ':' . $m[5] . ' UTC';
    }
    return $raw !== '' ? $raw : '—';
};

if (!isset($agrotracer_public_lookup) || !is_array($agrotracer_public_lookup)) {
    $has_token = isset($_GET['token']);
    $raw_token = '';
    if ($has_token) {
        $raw_token = function_exists('wp_unslash')
            ? (string) wp_unslash($_GET['token'])
            : (string) $_GET['token'];
    }
    $agrotracer_public_lookup = [
        'has_token' => $has_token,
        'result'    => ($has_token && class_exists('AgroTracer_Bridge'))
            ? AgroTracer_Bridge::consultar_certificado_publico($raw_token)
            : null,
    ];
}

$has_token = !empty($agrotracer_public_lookup['has_token']);
$result    = $agrotracer_public_lookup['result'] ?? null;
$dto       = (is_array($result) && !empty($result['success']) && is_array($result['data'] ?? null))
    ? $result['data']
    : null;
$error     = (is_array($result) && empty($result['success']) && is_array($result['error'] ?? null))
    ? $result['error']
    : null;
$status_code = is_array($result) ? (int) ($result['status'] ?? 0) : 0;

$logo_url = defined('AGROTRACER_PLUGIN_URL')
    ? AGROTRACER_PLUGIN_URL . 'assets/images/logo-agrotracer-emblem.png'
    : (function_exists('plugin_dir_url')
        ? plugin_dir_url(dirname(__FILE__)) . 'assets/images/logo-agrotracer-emblem.png'
        : '');
$agro_portal_url = function_exists('home_url')
    ? home_url('/agrotracer/')
    : '/';
?>
<div class="agrotracer-app agro-public-shell" id="agrotracer-public-cert-page">
  <header class="agro-header agro-public-header">
    <div class="agro-brand" style="cursor: default;">
      <?php if ($logo_url !== ''): ?>
        <img src="<?php echo $agro_esc_attr($logo_url); ?>" alt="AgroTracer" class="agro-brand-logo-img" width="42" height="42">
      <?php endif; ?>
      <span>AGROTRACER</span>
    </div>
    <span class="agro-badge info" style="font-size: 11.5px;">Verificação Pública (RN-13)</span>
  </header>

  <main class="agro-main agro-public-main">
    <section class="agro-public-container" aria-labelledby="public-cert-heading">
      <nav class="agro-breadcrumb agro-public-breadcrumb" aria-label="Breadcrumb">
        <ol class="agro-breadcrumb-list">
          <li class="agro-breadcrumb-item">
            <a class="agro-breadcrumb-link" href="<?php echo $agro_esc_attr($agro_portal_url); ?>">AgroTracer</a>
          </li>
          <li class="agro-breadcrumb-sep" aria-hidden="true">/</li>
          <li class="agro-breadcrumb-item agro-breadcrumb-current" aria-current="page">Consulta Pública de Certificado</li>
        </ol>
      </nav>
      <div class="agro-public-hero">
        <h1 id="public-cert-heading">Consulta Pública de Certificado</h1>
        <p>
          Verifique a autenticidade, o status e os resultados consolidados de pegada de carbono
          a partir do código de verificação ou QR Code impresso no certificado.
        </p>
      </div>

      <?php if (!$has_token): ?>
        <div class="agro-card agro-public-card" id="public-cert-form-card">
          <form method="get" class="agro-public-lookup-form" onsubmit="var b=this.querySelector('button[type=submit]');if(b){b.disabled=true;b.textContent='Verificando certificado...';}">
            <label for="public-cert-token-input" style="display:block; font-size:13px; font-weight:600; color:var(--agro-text-primary); margin-bottom:6px;">
              Código de Verificação (Token Público)
            </label>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              <input
                type="text"
                id="public-cert-token-input"
                name="token"
                class="agro-input"
                placeholder="Cole o token público de verificação"
                autocomplete="off"
                spellcheck="false"
                required
                style="flex:1; min-width:240px;"
              >
              <button type="submit" id="btn-public-verify-submit" class="agro-btn agro-btn-primary">
                Verificar Certificado
              </button>
            </div>
            <span style="display:block; margin-top:8px; font-size:12px; color:var(--agro-text-muted);">
              Consultas públicas são limitadas por IP e não exibem dados pessoais do produtor.
            </span>
          </form>
        </div>
      <?php endif; ?>

      <?php if ($dto !== null): ?>
        <?php
          $is_valido     = ($dto['status'] ?? '') === 'VALIDO';
          $badge_class   = $is_valido ? 'success' : 'danger';
          $badge_label   = $is_valido ? 'Válido' : 'Revogado / Invalidado';
          $resultados    = is_array($dto['resultados'] ?? null) ? $dto['resultados'] : [];
          $source_types  = is_array($dto['source_types'] ?? null) ? $dto['source_types'] : [];
          $is_synthetic  = !empty($dto['synthetic']);
          $aviso_sint    = (string) ($dto['aviso_proveniencia'] ?? 'SYNTHETIC - DEMONSTRAÇÃO DIDÁTICA. Contém fatores sintéticos.');
        ?>
        <article class="agro-card agro-public-card" id="public-cert-result-card" data-cert-status="<?php echo $agro_esc_attr($dto['status']); ?>">
          <div class="agro-public-card-header">
            <div>
              <span style="font-size:12px; color:var(--agro-text-muted); display:block;">
                Registro #<?php echo $agro_esc($dto['certificado_id']); ?> &middot; Lote #<?php echo $agro_esc($dto['lote_id']); ?>
              </span>
              <h2 style="margin:4px 0 0 0; font-size:20px; font-weight:700; color:var(--agro-text-primary);">
                Certificado de Emissões de Carbono
              </h2>
            </div>
            <span id="public-cert-status-badge" class="agro-badge <?php echo $agro_esc_attr($badge_class); ?>" style="font-size:13px; padding:6px 12px;">
              <?php echo $agro_esc($badge_label); ?>
            </span>
          </div>

          <?php if (!$is_valido): ?>
            <div id="public-cert-revoked-alert" class="agro-alert danger" role="alert" style="margin-bottom:18px;">
              <strong>Certificado Invalidado (<?php echo $agro_esc($dto['status']); ?>):</strong>
              Este registro foi revogado e não deve ser aceito como certificado válido.
            </div>
          <?php endif; ?>

          <?php if ($is_synthetic): ?>
            <div id="public-cert-synthetic-banner" class="agro-alert warning" data-source-type="SYNTHETIC" style="margin-bottom:18px;">
              <strong>Proveniência [SYNTHETIC]:</strong>
              <?php echo $agro_esc($aviso_sint); ?>
            </div>
          <?php endif; ?>

          <?php
            $raw_emissao     = (string) ($resultados['emissao_total_kg_co2e'] ?? '');
            $raw_intensidade = (string) ($resultados['intensidade_kg_co2e_kg'] ?? '');
            $fmt_emissao     = $agro_fmt_metric($raw_emissao);
            $fmt_intensidade = $agro_fmt_metric($raw_intensidade);
            $animais_abate   = (int) ($dto['numero_animais_abate'] ?? 0);
            $animais_label   = $animais_abate === 1 ? 'cabeça' : 'cabeças';
            $raw_emitido_em  = (string) ($dto['emitido_em'] ?? '');
          ?>
          <div class="agro-public-metrics-grid">
            <div class="agro-public-metric-box">
              <span class="agro-public-metric-label">Emissão Total Consolidada</span>
              <div class="agro-public-metric-value">
                <strong id="public-cert-emissao-total" title="<?php echo $agro_esc_attr($raw_emissao); ?>"><?php echo $agro_esc($fmt_emissao); ?></strong>
                <span><?php echo $agro_esc($resultados['unidade_emissao'] ?? 'kg CO2e'); ?></span>
              </div>
            </div>

            <div class="agro-public-metric-box highlight">
              <span class="agro-public-metric-label">Intensidade de Carbono</span>
              <div class="agro-public-metric-value">
                <strong id="public-cert-intensidade" title="<?php echo $agro_esc_attr($raw_intensidade); ?>"><?php echo $agro_esc($fmt_intensidade); ?></strong>
                <span><?php echo $agro_esc($resultados['unidade_intensidade'] ?? 'kg CO2e/kg de carcaça'); ?></span>
              </div>
            </div>
          </div>

          <dl class="agro-public-details-list">
            <div>
              <dt>Versão do Método</dt>
              <dd id="public-cert-metodo"><?php echo $agro_esc($dto['versao_metodo'] ?? '—'); ?></dd>
            </div>
            <div>
              <dt>Versão dos Parâmetros</dt>
              <dd id="public-cert-parametros"><?php echo $agro_esc($dto['versao_parametros'] ?? '—'); ?></dd>
            </div>
            <div>
              <dt>Tipo de Origem (source_type)</dt>
              <dd id="public-cert-source-types"><?php echo $agro_esc(!empty($source_types) ? implode(', ', $source_types) : '—'); ?></dd>
            </div>
            <div>
              <dt>Data de Abate</dt>
              <dd id="public-cert-data-abate"><?php echo $agro_esc($agro_fmt_date($dto['data_abate'] ?? '')); ?></dd>
            </div>
            <div>
              <dt>Animais no Abate</dt>
              <dd id="public-cert-animais"><?php echo $agro_esc($animais_abate); ?> <?php echo $agro_esc($animais_label); ?></dd>
            </div>
            <div>
              <dt>Emitido em</dt>
              <dd id="public-cert-emitido-em" title="<?php echo $agro_esc_attr($raw_emitido_em); ?>"><?php echo $agro_esc($agro_fmt_datetime($raw_emitido_em)); ?></dd>
            </div>
          </dl>

          <div class="agro-public-integrity-box">
            <strong style="display:block; font-size:12px; color:var(--agro-text-secondary); margin-bottom:6px;">
              Integridade Criptográfica (DTO Minimizado — Sem Dados Pessoais)
            </strong>
            <div style="font-size:12px; color:var(--agro-text-secondary); word-break:break-all;">
              <strong>Snapshot SHA-256:</strong>
              <code id="public-cert-snapshot-sha256"><?php echo $agro_esc($dto['snapshot_sha256'] ?? '—'); ?></code>
            </div>
            <?php if (!empty($dto['pdf_sha256'])): ?>
              <div style="font-size:12px; color:var(--agro-text-secondary); word-break:break-all; margin-top:4px;">
                <strong>PDF SHA-256:</strong>
                <code id="public-cert-pdf-sha256"><?php echo $agro_esc($dto['pdf_sha256']); ?></code>
              </div>
            <?php endif; ?>
          </div>
        </article>
      <?php elseif ($has_token && $error !== null): ?>
        <?php
          $err_code   = (string) ($error['code'] ?? 'CERTIFICADO_NAO_ENCONTRADO');
          $err_corr   = (string) ($error['correlation_id'] ?? '');
          $alert_kind = ($status_code === 429 || $status_code === 503) ? 'warning' : 'danger';
          $err_title  = 'Certificado não encontrado.';
          $err_desc   = 'Verifique se o link ou QR Code utilizado está completo e tente novamente.';

          if ($err_code === 'LIMITE_CONSULTAS' || $status_code === 429) {
              $err_title = 'Limite de consultas atingido.';
              $err_desc  = 'Muitas consultas foram realizadas recentemente a partir desta conexão. Aguarde um minuto e tente novamente.';
          } elseif ($err_code === 'CONSULTA_INDISPONIVEL' || $err_code === 'SERVICE_UNAVAILABLE' || $status_code === 503) {
              $err_title = 'Consulta temporariamente indisponível.';
              $err_desc  = 'O serviço de verificação pública não pôde processar a solicitação agora. Tente novamente em instantes.';
          } elseif ($err_code === 'SNAPSHOT_INTEGRO_OBRIGATORIO' || $status_code === 409) {
              $err_title = 'Falha na verificação de integridade.';
              $err_desc  = 'Não foi possível validar a integridade criptográfica deste registro.';
          }
        ?>
        <div id="public-cert-error-box" class="agro-card agro-public-card">
          <div class="agro-alert <?php echo $agro_esc_attr($alert_kind); ?>" role="alert">
            <strong id="public-cert-error-title" style="display:block; font-size:15px; margin-bottom:4px;">
              <?php echo $agro_esc($err_title); ?>
            </strong>
            <p id="public-cert-error-message" style="margin:0 0 8px 0; font-size:13px;">
              <?php echo $agro_esc($err_desc); ?>
            </p>
            <div style="font-size:11.5px; opacity:0.85;">
              Código: <code id="public-cert-error-code"><?php echo $agro_esc($err_code); ?></code>
              <?php if ($err_corr !== ''): ?>
                &middot; Correlation ID: <code id="public-cert-error-corr"><?php echo $agro_esc($err_corr); ?></code>
              <?php endif; ?>
            </div>
          </div>
          <div style="margin-top:14px;">
            <a href="?" class="agro-btn agro-btn-secondary">Consultar outro código</a>
          </div>
        </div>
      <?php endif; ?>
    </section>
  </main>

  <footer class="agro-footer agro-public-footer">
    <div class="agro-footer-left">
      <span>&copy; 2026 AgroTracer &middot; Plataforma de Rastreabilidade Acad&ecirc;mica</span>
    </div>
    <div class="agro-footer-right">
      <span>Motor de Estimativa: <strong>CARBONENGINE-MVP-1.0</strong></span>
      <span>&verbar;</span>
      <span>Consulta P&uacute;blica (RN-13)</span>
    </div>
  </footer>
</div>
