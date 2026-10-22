<?php
/**
 * Bootstrap for AgroTracer Bridge PHPUnit / Standalone Test Suite
 *
 * Provides deterministic stubs for WordPress Native APIs (`wp_remote_get`,
 * `wp_remote_post`, `wp_verify_nonce`, `current_user_can`, `get_current_user_id`, etc.)
 * and minimal PHPUnit\Framework\TestCase compatibility when executed directly via PHP CLI.
 *
 * @package AgroTracerBridge\Tests
 */

declare(strict_types=1);

namespace {
    if (!defined('ABSPATH')) {
        define('ABSPATH', dirname(__DIR__) . '/');
    }

    if (!defined('AGROTRACER_PLUGIN_DIR')) {
        define('AGROTRACER_PLUGIN_DIR', dirname(__DIR__) . '/');
    }

    if (!defined('AGROTRACER_API_URL')) {
        define('AGROTRACER_API_URL', 'http://127.0.0.1:8000');
    }

    if (!defined('AGROTRACER_API_HMAC_SECRET')) {
        define('AGROTRACER_API_HMAC_SECRET', 'agrotracer_chave_exclusivamente_teste_2026');
    }

    if (!defined('AGROTRACER_API_TIMEOUT')) {
        define('AGROTRACER_API_TIMEOUT', 10);
    }

    /**
     * Global WordPress Test State Mock Store
     */
    class AgroTracer_WP_Test_Mock_State {
        public static int $current_user_id = 42;
        /** @var array<string, bool> */
        public static array $capabilities = ['agrotracer_manage_farms' => true];
        /** @var array<string, string> */
        public static array $valid_nonces = ['valid_wp_nonce_token_123' => 'wp_rest'];
        /** @var array<int, array<string, mixed>> */
        public static array $dispatched_requests = [];
        /** @var callable|null */
        public static $remote_handler = null;

        public static function reset(): void {
            self::$current_user_id = 42;
            self::$capabilities = ['agrotracer_manage_farms' => true];
            self::$valid_nonces = ['valid_wp_nonce_token_123' => 'wp_rest'];
            self::$dispatched_requests = [];
            self::$remote_handler = null;
        }
    }

    if (!class_exists('WP_Error')) {
        class WP_Error {
            private string $code;
            private string $message;

            public function __construct(string $code = 'http_request_failed', string $message = 'Erro de conexão') {
                $this->code = $code;
                $this->message = $message;
            }

            public function get_error_code(): string {
                return $this->code;
            }

            public function get_error_message(): string {
                return $this->message;
            }
        }
    }

    if (!function_exists('is_wp_error')) {
        function is_wp_error($thing): bool {
            return $thing instanceof WP_Error;
        }
    }

    if (!function_exists('get_current_user_id')) {
        function get_current_user_id(): int {
            return AgroTracer_WP_Test_Mock_State::$current_user_id;
        }
    }

    if (!function_exists('current_user_can')) {
        function current_user_can(string $capability): bool {
            return !empty(AgroTracer_WP_Test_Mock_State::$capabilities[$capability]);
        }
    }

    if (!function_exists('wp_verify_nonce')) {
        function wp_verify_nonce(string $nonce, $action = -1) {
            if (
                isset(AgroTracer_WP_Test_Mock_State::$valid_nonces[$nonce]) &&
                AgroTracer_WP_Test_Mock_State::$valid_nonces[$nonce] === (string) $action
            ) {
                return 1;
            }
            return false;
        }
    }

    if (!function_exists('wp_json_encode')) {
        function wp_json_encode($data, int $options = 0, int $depth = 512) {
            return json_encode($data, $options | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE, $depth);
        }
    }

    if (!function_exists('sanitize_text_field')) {
        function sanitize_text_field(string $str): string {
            return trim(strip_tags($str));
        }
    }

    if (!function_exists('wp_remote_get')) {
        function wp_remote_get(string $url, array $args = []) {
            $args['method'] = 'GET';
            AgroTracer_WP_Test_Mock_State::$dispatched_requests[] = [
                'url'  => $url,
                'args' => $args,
            ];
            if (is_callable(AgroTracer_WP_Test_Mock_State::$remote_handler)) {
                return call_user_func(AgroTracer_WP_Test_Mock_State::$remote_handler, $url, $args);
            }
            return [
                'response' => ['code' => 200, 'message' => 'OK'],
                'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID'] ?? ''],
                'body'     => json_encode(['data' => []]),
            ];
        }
    }

    if (!function_exists('wp_remote_post')) {
        function wp_remote_post(string $url, array $args = []) {
            $args['method'] = 'POST';
            AgroTracer_WP_Test_Mock_State::$dispatched_requests[] = [
                'url'  => $url,
                'args' => $args,
            ];
            if (is_callable(AgroTracer_WP_Test_Mock_State::$remote_handler)) {
                return call_user_func(AgroTracer_WP_Test_Mock_State::$remote_handler, $url, $args);
            }
            return [
                'response' => ['code' => 201, 'message' => 'Created'],
                'headers'  => ['x-correlation-id' => $args['headers']['X-Correlation-ID'] ?? ''],
                'body'     => json_encode(['data' => ['id' => 1]]),
            ];
        }
    }

    if (!function_exists('wp_remote_retrieve_response_code')) {
        function wp_remote_retrieve_response_code($response): int {
            if (is_wp_error($response) || !is_array($response)) {
                return 0;
            }
            return (int) ($response['response']['code'] ?? 0);
        }
    }

    if (!function_exists('wp_remote_retrieve_body')) {
        function wp_remote_retrieve_body($response): string {
            if (is_wp_error($response) || !is_array($response)) {
                return '';
            }
            return (string) ($response['body'] ?? '');
        }
    }

    if (!function_exists('wp_remote_retrieve_header')) {
        function wp_remote_retrieve_header($response, string $header): string {
            if (is_wp_error($response) || !is_array($response) || !isset($response['headers'])) {
                return '';
            }
            foreach ($response['headers'] as $k => $v) {
                if (strtolower((string) $k) === strtolower($header)) {
                    return (string) $v;
                }
            }
            return '';
        }
    }
}

namespace PHPUnit\Framework {
    if (!class_exists(AssertionFailedError::class)) {
        class AssertionFailedError extends \RuntimeException {}
    }

    if (!class_exists(TestCase::class)) {
        abstract class TestCase {
            public static int $assertion_count = 0;

            protected function setUp(): void {}
            protected function tearDown(): void {}

            public function assertSame($expected, $actual, string $message = ''): void {
                self::$assertion_count++;
                if ($expected !== $actual) {
                    throw new AssertionFailedError(
                        ($message !== '' ? "$message — " : '') .
                        sprintf('Failed asserting that %s is identical to %s.', var_export($actual, true), var_export($expected, true))
                    );
                }
            }

            public function assertEquals($expected, $actual, string $message = ''): void {
                self::$assertion_count++;
                if ($expected != $actual) {
                    throw new AssertionFailedError(
                        ($message !== '' ? "$message — " : '') .
                        sprintf('Failed asserting that %s matches expected %s.', var_export($actual, true), var_export($expected, true))
                    );
                }
            }

            public function assertTrue($condition, string $message = ''): void {
                self::$assertion_count++;
                if ($condition !== true) {
                    throw new AssertionFailedError($message ?: 'Failed asserting that condition is true.');
                }
            }

            public function assertFalse($condition, string $message = ''): void {
                self::$assertion_count++;
                if ($condition !== false) {
                    throw new AssertionFailedError($message ?: 'Failed asserting that condition is false.');
                }
            }

            public function assertArrayHasKey($key, array $array, string $message = ''): void {
                self::$assertion_count++;
                if (!array_key_exists($key, $array)) {
                    throw new AssertionFailedError($message ?: "Failed asserting that array has key '$key'.");
                }
            }

            public function assertArrayNotHasKey($key, array $array, string $message = ''): void {
                self::$assertion_count++;
                if (array_key_exists($key, $array)) {
                    throw new AssertionFailedError($message ?: "Failed asserting that array does not have key '$key'.");
                }
            }

            public function assertMatchesRegularExpression(string $pattern, string $string, string $message = ''): void {
                self::$assertion_count++;
                if (preg_match($pattern, $string) !== 1) {
                    throw new AssertionFailedError($message ?: "Failed asserting that '$string' matches PCRE pattern '$pattern'.");
                }
            }

            public function assertStringContainsString(string $needle, string $haystack, string $message = ''): void {
                self::$assertion_count++;
                if (strpos($haystack, $needle) === false) {
                    throw new AssertionFailedError($message ?: "Failed asserting that '$haystack' contains '$needle'.");
                }
            }

            public function assertStringNotContainsString(string $needle, string $haystack, string $message = ''): void {
                self::$assertion_count++;
                if (strpos($haystack, $needle) !== false) {
                    throw new AssertionFailedError($message ?: "Failed asserting that '$haystack' does not contain '$needle'.");
                }
            }
        }
    }
}

namespace {
    require_once dirname(__DIR__) . '/includes/class-agrotracer-http-client.php';
}
