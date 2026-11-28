<?php
/**
 * AgroTracer Footer Template
 * Standardized Desktop Rural Academic Platform Footer
 */
?>
<footer class="agro-footer">
  <div class="agro-footer-left">
    <span>&copy; 2026 AgroTracer &middot; Plataforma de Rastreabilidade Acad&ecirc;mica</span>
  </div>

  <div class="agro-footer-right">
    <span>Vers&atilde;o do Motor de Estimativa: <strong>MVP-DIDATICO-1.0</strong></span>
    <span>&verbar;</span>
    <span class="agro-health-badge">
      <span class="agro-health-dot"></span>
      Health: OK
    </span>
    <span>&verbar;</span>
    <span>X-Correlation-ID: <code class="agro-correlation-id"><?php echo esc_html(class_exists('AgroTracer_Bridge') ? AgroTracer_Bridge::resolve_correlation_id() : '123e4567-e89b-42d3-a456-426614174000'); ?></code></span>
  </div>
</footer>
