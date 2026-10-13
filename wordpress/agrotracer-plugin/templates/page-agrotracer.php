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
    <?php 
      include $plugin_dir . '/templates/dashboard.php';
      include $plugin_dir . '/templates/farms.php';
      include $plugin_dir . '/templates/lots.php';
    ?>
  </main>

  <?php 
    include $plugin_dir . '/templates/modals.php';
    include $plugin_dir . '/templates/footer.php'; 
  ?>

  <!-- Toast Notification Container Persistente -->
  <div id="agro-toast-container" class="agro-toast-container">
    <!-- Toast Inicial demonstrativo conforme tela B de Fazendas -->
    <div class="agro-toast" id="initial-demo-toast">
      <div class="agro-toast-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:15px;height:15px;">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </div>
      <div class="agro-toast-content">
        <p class="agro-toast-title">Fazenda atualizada com sucesso!</p>
        <div class="agro-toast-correlation">ID da requisi&ccedil;&atilde;o: 8d7c3f2a-9e4b</div>
      </div>
      <button type="button" class="agro-toast-close" onclick="document.getElementById('initial-demo-toast').remove()" aria-label="Fechar">&times;</button>
    </div>
  </div>
</div>
