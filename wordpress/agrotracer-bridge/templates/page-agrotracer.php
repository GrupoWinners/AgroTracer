<?php
/**
 * Template Name: AgroTracer Desktop Rural Application
 * Description: Template WordPress Full-Width para a interface desktop rural do AgroTracer (Sprint 1 - S1-T03)
 */

if (!defined('ABSPATH')) {
    // Direct access fallback
}
?>
<div class="agrotracer-app" id="agrotracer-app-root">
  <?php 
    $plugin_dir = dirname(__DIR__);
    include $plugin_dir . '/templates/header.php'; 
  ?>

  <main class="agro-main">
    <nav id="agro-breadcrumb" class="agro-breadcrumb" aria-label="Breadcrumb">
      <ol class="agro-breadcrumb-list">
        <li class="agro-breadcrumb-item">
          <button type="button" class="agro-breadcrumb-link" onclick="AgroTracer.switchScreen('dashboard')">AgroTracer</button>
        </li>
        <li class="agro-breadcrumb-sep" aria-hidden="true">/</li>
        <li class="agro-breadcrumb-item agro-breadcrumb-current" aria-current="page">Dashboard</li>
      </ol>
    </nav>

    <?php 
      include $plugin_dir . '/templates/dashboard.php';
      include $plugin_dir . '/templates/farms.php';
      include $plugin_dir . '/templates/lots.php';
      include $plugin_dir . '/templates/manejo.php';
      include $plugin_dir . '/templates/fechamento.php';
      include $plugin_dir . '/templates/certificados.php';
    ?>
  </main>

  <?php 
    include $plugin_dir . '/templates/modals.php';
    include $plugin_dir . '/templates/footer.php'; 
  ?>

  <!-- Toast Notification Container Persistente -->
  <div id="agro-toast-container" class="agro-toast-container" aria-live="polite"></div>
</div>
