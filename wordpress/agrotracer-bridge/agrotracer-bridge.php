<?php
/**
 * Plugin Name: AgroTracer Bridge
 * Plugin URI: https://github.com/GrupoWinners/AgroTracer
 * Description: Plataforma de Rastreabilidade Pecuária e Pegada de Carbono - Interface Desktop Rural WordPress homologada para a Task S1-T03.
 * Version: 3.0.1
 * Author: Grupo Winners / João Vitor (Losel), Nadiny Martins & Samela Maria
 * Author URI: https://www.portifoliolosel.dev
 * License: GPLv2 or later
 * Text Domain: agrotracer-bridge
 * Domain Path: /languages
 * Requires at least: 5.8
 * Requires PHP: 7.4
 */

if (!defined('ABSPATH')) {
    exit;
}

// Plugin Constants
define('AGROTRACER_VERSION', '3.0.1');
define('AGROTRACER_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('AGROTRACER_PLUGIN_URL', plugin_dir_url(__FILE__));

// Require Core Classes
require_once AGROTRACER_PLUGIN_DIR . 'includes/class-agrotracer-shortcodes.php';
require_once AGROTRACER_PLUGIN_DIR . 'includes/class-agrotracer-bridge.php';

// Bootstrap Plugin
function agrotracer_bridge_init() {
    return AgroTracer_Bridge::get_instance();
}

add_action('plugins_loaded', 'agrotracer_bridge_init');

// Activation & Deactivation Hooks (Roles & Capabilities Setup)
register_activation_hook(__FILE__, ['AgroTracer_Bridge', 'activate']);
register_deactivation_hook(__FILE__, ['AgroTracer_Bridge', 'deactivate']);
