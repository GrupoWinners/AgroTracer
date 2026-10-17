<?php
/**
 * Canvas Autônomo Full-Width para AgroTracer Desktop Rural
 * Isola a interface do sistema da interferência visual de temas terceiros (Twenty Twenty-Four, Astra, etc.)
 * Versão: 3.2.0 (Full-Width Canvas & Isolated Shell)
 */

if (!defined('ABSPATH')) {
    exit;
}

// Enfileira os assets oficiais do AgroTracer
wp_enqueue_style('agrotracer-screens-css');
wp_enqueue_script('agrotracer-screens-js');
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php wp_title('|', true, 'right'); bloginfo('name'); ?></title>
    <?php wp_head(); ?>
    <style>
        /* Reset estrito para Full-Width absoluto no canvas */
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #f8f9fa !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            overflow-x: hidden;
            width: 100% !important;
            min-height: 100vh !important;
        }
        #wpadminbar {
            opacity: 0.95;
        }
    </style>
</head>
<body <?php body_class('agrotracer-fullscreen'); ?>>
<?php 
    $plugin_dir = dirname(__DIR__);
    include $plugin_dir . '/templates/page-agrotracer.php'; 
?>
<?php wp_footer(); ?>
</body>
</html>
