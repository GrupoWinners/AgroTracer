<?php
/**
 * AgroTracer Header Template
 * Scoped Desktop Rural Navigation Bar
 */
if (!defined('ABSPATH')) {
    // If loaded standalone, avoid direct execution issues
}

$agro_user_display = 'João Silva';
if (function_exists('wp_get_current_user')) {
    $wp_user = wp_get_current_user();
    if ($wp_user && !empty($wp_user->display_name)) {
        $agro_user_display = (string) $wp_user->display_name;
    }
}

$agro_public_cert_url = function_exists('home_url')
    ? home_url('/certificado/')
    : '/certificado/';
$agro_logout_url = function_exists('wp_logout_url')
    ? wp_logout_url(function_exists('home_url') ? home_url('/agrotracer/') : '/')
    : '';
?>
<header class="agro-header">
  <div class="agro-brand" role="button" tabindex="0" aria-label="Ir para Dashboard AgroTracer" onclick="AgroTracer.switchScreen('dashboard')">
    <?php 
      $logo_url = defined('AGROTRACER_PLUGIN_URL') 
        ? AGROTRACER_PLUGIN_URL . 'assets/images/logo-agrotracer-emblem.png' 
        : plugin_dir_url(dirname(__DIR__)) . 'assets/images/logo-agrotracer-emblem.png';
    ?>
    <img src="<?php echo esc_url($logo_url); ?>" alt="AgroTracer" class="agro-brand-logo-img" width="42" height="42">
    <span>AGROTRACER</span>
  </div>

  <nav class="agro-nav" aria-label="Navegação Principal">
    <button type="button" class="agro-nav-item active" data-screen="dashboard">
      <svg viewBox="0 0 24 24">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        <polyline points="9 22 9 12 15 12 15 22"></polyline>
      </svg>
      <span>Dashboard</span>
    </button>

    <button type="button" class="agro-nav-item" data-screen="fazendas">
      <svg viewBox="0 0 24 24">
        <path d="M3 21h18"></path>
        <path d="M5 21V7l8-4v18"></path>
        <path d="M19 21V11l-6-3"></path>
        <path d="M9 9h1"></path>
        <path d="M9 13h1"></path>
        <path d="M9 17h1"></path>
      </svg>
      <span>Fazendas</span>
    </button>

    <button type="button" class="agro-nav-item" data-screen="lotes">
      <svg viewBox="0 0 24 24">
        <path d="M17 10h.01"></path>
        <path d="M7 10h.01"></path>
        <path d="M4 14c0 3 3 5 8 5s8-2 8-5"></path>
        <path d="M6 8c-2 0-3-2-3-4 2 0 4 1 5 3"></path>
        <path d="M18 8c2 0 3-2 3-4-2 0-4 1-5 3"></path>
        <circle cx="12" cy="11" r="5"></circle>
      </svg>
      <span>Lotes e Animais</span>
    </button>

    <button type="button" class="agro-nav-item" data-screen="manejo">
      <svg viewBox="0 0 24 24">
        <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
        <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
        <path d="M9 12h6"></path>
        <path d="M9 16h6"></path>
      </svg>
      <span>Manejo</span>
    </button>

    <button type="button" class="agro-nav-item" data-screen="fechamento">
      <svg viewBox="0 0 24 24">
        <path d="M9 11l3 3L22 4"></path>
        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
      </svg>
      <span>Fechamento</span>
    </button>

    <button type="button" class="agro-nav-item" data-screen="certificados">
      <svg viewBox="0 0 24 24">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        <polyline points="9 12 11 14 15 10"></polyline>
      </svg>
      <span>Certificados</span>
    </button>
  </nav>

  <div class="agro-header-right">
    <div class="agro-header-menu-wrap">
      <button type="button" id="btn-header-notifications" class="agro-notification-btn" title="Notificações Pendentes" aria-label="Notificações" aria-expanded="false" aria-controls="agro-notifications-popover">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        <span class="agro-badge-count" id="agro-notifications-count">3</span>
      </button>

      <div id="agro-notifications-popover" class="agro-header-popover" role="region" aria-label="Central de Notificações" hidden>
        <div class="agro-header-popover-head">
          <strong>Notificações</strong>
          <button type="button" class="agro-popover-clear" id="btn-mark-notifications-read">Marcar como lidas</button>
        </div>
        <div class="agro-header-popover-list">
          <button type="button" class="agro-popover-item" data-nav-screen="fechamento" data-lot-id="1">
            <span class="agro-badge warning" style="font-size:10px;">Atenção</span>
            <span>Lote <strong>LT-2026-001</strong> próximo do fechamento.</span>
          </button>
          <button type="button" class="agro-popover-item" data-nav-screen="manejo" data-lot-id="1">
            <span class="agro-badge info" style="font-size:10px;">Método</span>
            <span>Parâmetros didáticos <strong>v1.0-2026 [SYNTHETIC]</strong> ativos.</span>
          </button>
          <button type="button" class="agro-popover-item" data-nav-screen="certificados">
            <span class="agro-badge success" style="font-size:10px;">Certificado</span>
            <span>Certificado do lote <strong>LT-2025-090</strong> disponível para consulta.</span>
          </button>
        </div>
      </div>
    </div>

    <div class="agro-header-menu-wrap">
      <button type="button" id="btn-header-user-menu" class="agro-user-menu" title="Perfil de Acesso Rural" aria-expanded="false" aria-controls="agro-user-dropdown">
        <div class="agro-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
        <span class="agro-user-name"><?php echo esc_html($agro_user_display); ?></span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#94a3b8;">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      <div id="agro-user-dropdown" class="agro-header-popover agro-user-dropdown" role="menu" aria-label="Menu do Produtor" hidden>
        <div class="agro-header-popover-head">
          <strong><?php echo esc_html($agro_user_display); ?></strong>
          <span class="agro-badge neutral" style="font-size:10px;">Produtor Rural</span>
        </div>
        <div class="agro-header-popover-list">
          <button type="button" class="agro-popover-item" role="menuitem" data-nav-screen="dashboard">
            <span>Ir para Dashboard</span>
          </button>
          <button type="button" class="agro-popover-item" role="menuitem" data-nav-screen="certificados">
            <span>Meus Certificados</span>
          </button>
          <a class="agro-popover-item" role="menuitem" href="<?php echo esc_url($agro_public_cert_url); ?>" target="_blank" rel="noopener noreferrer">
            <span>Consulta Pública de Certificado</span>
          </a>
          <?php if ($agro_logout_url !== ''): ?>
            <a class="agro-popover-item" role="menuitem" href="<?php echo esc_url($agro_logout_url); ?>">
              <span>Sair da Sessão</span>
            </a>
          <?php endif; ?>
        </div>
      </div>
    </div>
  </div>
</header>
