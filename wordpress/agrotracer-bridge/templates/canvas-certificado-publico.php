<?php
/**
 * Canvas Autônomo para Consulta Pública de Certificado (/certificado/?token=...)
 * Sem barras administrativas do WordPress e com cabeçalhos de proteção de token.
 *
 * @package AgroTracerBridge
 */

if (!defined('ABSPATH')) {
    exit;
}

if (!headers_sent()) {
    header('Cache-Control: no-store');
    header('Referrer-Policy: no-referrer');
    header('X-Robots-Tag: noindex, nofollow');
    header('X-Content-Type-Options: nosniff');
}

if (function_exists('wp_enqueue_style')) {
    wp_enqueue_style('agrotracer-screens-css');
}
?>
<!DOCTYPE html>
<html <?php if (function_exists('language_attributes')) { language_attributes(); } else { echo 'lang="pt-BR"'; } ?>>
<head>
    <meta charset="<?php if (function_exists('bloginfo')) { bloginfo('charset'); } else { echo 'UTF-8'; } ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <meta name="robots" content="noindex, nofollow">
    <title>Verificação Pública de Certificado | AgroTracer</title>
    <?php
      if (function_exists('wp_head')) {
          wp_head();
      } else {
          $css_url = plugin_dir_url(dirname(__FILE__)) . 'assets/css/agrotracer-screens.css';
          echo '<link rel="stylesheet" href="' . htmlspecialchars($css_url, ENT_QUOTES, 'UTF-8') . '">';
      }
    ?>
    <style>
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #f8f9fa !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            min-height: 100vh !important;
        }
    </style>
</head>
<body class="agrotracer-public-body">
<?php
    $plugin_dir = dirname(__DIR__);
    include $plugin_dir . '/templates/certificado-publico.php';
    if (function_exists('wp_footer')) {
        wp_footer();
    }
?>
</body>
</html>
