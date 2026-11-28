<?php
/**
 * AgroTracer Shortcodes
 * Handles [agrotracer_app], [agrotracer_dashboard], [agrotracer_farms], [agrotracer_lots]
 */

if (!defined('ABSPATH')) {
    exit;
}

class AgroTracer_Shortcodes {

    public static function init() {
        add_shortcode('agrotracer_app', [__CLASS__, 'render_full_app']);
        add_shortcode('agrotracer_dashboard', [__CLASS__, 'render_dashboard']);
        add_shortcode('agrotracer_farms', [__CLASS__, 'render_farms']);
        add_shortcode('agrotracer_lots', [__CLASS__, 'render_lots']);
    }

    public static function render_full_app($atts) {
        self::ensure_assets();
        ob_start();
        $plugin_dir = dirname(__DIR__);
        include $plugin_dir . '/templates/page-agrotracer.php';
        return ob_get_clean();
    }

    public static function render_dashboard($atts) {
        self::ensure_assets();
        ob_start();
        $plugin_dir = dirname(__DIR__);
        echo '<div class="agrotracer-app"><main class="agro-main">';
        include $plugin_dir . '/templates/dashboard.php';
        echo '</main></div>';
        return ob_get_clean();
    }

    public static function render_farms($atts) {
        self::ensure_assets();
        ob_start();
        $plugin_dir = dirname(__DIR__);
        echo '<div class="agrotracer-app"><main class="agro-main">';
        include $plugin_dir . '/templates/farms.php';
        echo '</main>';
        include $plugin_dir . '/templates/modals.php';
        echo '</div>';
        return ob_get_clean();
    }

    public static function render_lots($atts) {
        self::ensure_assets();
        ob_start();
        $plugin_dir = dirname(__DIR__);
        echo '<div class="agrotracer-app"><main class="agro-main">';
        include $plugin_dir . '/templates/lots.php';
        echo '</main>';
        include $plugin_dir . '/templates/modals.php';
        echo '</div>';
        return ob_get_clean();
    }

    private static function ensure_assets() {
        wp_enqueue_style('agrotracer-screens-css');
        wp_enqueue_script('agrotracer-screens-js');
    }
}
