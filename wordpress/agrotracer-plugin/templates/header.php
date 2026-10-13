<?php
/**
 * AgroTracer Header Template
 * Scoped Desktop Rural Navigation Bar
 */
if (!defined('ABSPATH')) {
    // If loaded standalone, avoid direct execution issues
}
?>
<header class="agro-header">
  <div class="agro-brand" onclick="AgroTracer.switchScreen('dashboard')">
    <?php 
      $logo_url = defined('AGROTRACER_PLUGIN_URL') 
        ? AGROTRACER_PLUGIN_URL . 'assets/images/logo-agrotracer-emblem.png' 
        : plugin_dir_url(dirname(__DIR__)) . 'assets/images/logo-agrotracer-emblem.png';
    ?>
    <img src="<?php echo esc_url($logo_url); ?>" alt="AgroTracer" class="agro-brand-logo-img">
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

    <button type="button" class="agro-nav-item" data-screen="certificados">
      <svg viewBox="0 0 24 24">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        <polyline points="9 12 11 14 15 10"></polyline>
      </svg>
      <span>Certificados</span>
    </button>
  </nav>

  <div class="agro-header-right">
    <button type="button" class="agro-notification-btn" title="Notificações Pendentes" aria-label="Notificações">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
      </svg>
      <span class="agro-badge-count">3</span>
    </button>

    <div class="agro-user-menu" title="Perfil de Acesso Rural">
      <div class="agro-avatar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
      </div>
      <span class="agro-user-name">João Silva</span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#94a3b8;">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </div>
  </div>
</header>
