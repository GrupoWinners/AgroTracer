<?php
/**
 * Plugin Name: AgroTracer Plugin
 * Plugin URI: https://github.com/GrupoWinners/AgroTracer
 * Description: Plataforma de Rastreabilidade Pecuária e Pegada de Carbono - Interface Desktop Rural WordPress homologada para a Task S1-T03.
 * Version: 3.0.0
 * Author: Grupo Winners / João Vitor (Losel) & Nadiny Martins
 * Author URI: https://www.portifoliolosel.dev
 * License: GPLv2 or later
 * Text Domain: agrotracer-plugin
 */

if (!defined('ABSPATH')) {
    exit;
}

// Redirect/Alias to agrotracer-bridge implementation
$bridge_file = dirname(__DIR__) . '/agrotracer-bridge/agrotracer-bridge.php';
if (file_exists($bridge_file)) {
    require_once $bridge_file;
} else {
    // Standalone fallback if copied independently
    define('AGROTRACER_VERSION', '3.0.0');
    define('AGROTRACER_PLUGIN_DIR', plugin_dir_path(__FILE__));
    define('AGROTRACER_PLUGIN_URL', plugin_dir_url(__FILE__));
}
