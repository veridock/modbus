<?php

// Loguj wszystko do php.log
ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/php.log');
/**
 * Router dla obsługi plików SVG+PHP
 * Umożliwia wykonywanie PHP wewnątrz plików .svg
 */


// Konfiguracja CORS dla API calls
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Obsługa OPTIONS dla CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Parsowanie URI
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
if ($uri === false) {
    $uri = '/';
}
$path = __DIR__ . $uri;

// Logowanie żądań
error_log("[Router] --- START router.php ---");
error_log("[Router] Request: $uri");

// Obsługa plików .svg jako PHP
if (strtolower(pathinfo($uri, PATHINFO_EXTENSION)) === 'svg' && file_exists($path)) {
    error_log("[Router] Rozpoznano żądanie SVG: $uri");
    // Ustaw poprawny Content-Type dla SVG
    //header('Content-Type: image/svg+xml; charset=UTF-8');
    // Jeśli ?validate, uruchom validator.php i pokaż wynik walidacji zamiast SVG
    if (isset($_GET['validate'])) {
        error_log("[Router] Tryb walidacji SVG: $uri");
        // Załaduj tylko klasę SVGValidator bez globalnego kodu HTTP API
        require_once __DIR__ . '/validator.php';
        if (!class_exists('SVGValidator')) {
            echo "Validator class not found!";
            exit(1);
        }
        $validator = new SVGValidator();
        $results = $validator->testSVGFile($path);
        header('Content-Type: text/plain; charset=UTF-8');
        error_log("[Router] Wynik walidacji SVG: $uri - tests: " . count($results['tests']) . ", errors: " . count($results['errors']));
        echo "SVG VALIDATION RESULT for $uri\n";
        echo str_repeat('=', 60) . "\n";
        foreach ($results['tests'] as $test) {
            echo ($test['passed'] ? '✅' : '❌') . " {$test['id']}: {$test['description']}\n";
        }
        if (!empty($results['errors'])) {
            echo "\n🔧 Detailed Error Analysis:\n";
            foreach ($results['errors'] as $error) {
                echo "   📍 Test: {$error['test_id']}\n";
                echo "   📝 Issue: {$error['description']}\n";
                if (!empty($error['suggestions'])) {
                    echo "   💡 Suggestions to fix:\n";
                    foreach ($error['suggestions'] as $suggestion) {
                        echo "      • $suggestion\n";
                    }
                }
                if (!empty($error['line_info'])) {
                    echo "   📄 Line-specific issues:\n";
                    foreach ($error['line_info'] as $lineInfo) {
                        echo "      • Line {$lineInfo['line']}: {$lineInfo['issue']}\n";
                        echo "        Code: " . substr($lineInfo['content'], 0, 80) . (strlen($lineInfo['content']) > 80 ? '...' : '') . "\n";
                        echo "        Fix: {$lineInfo['fix']}\n";
                    }
                }
                echo "\n";
            }
        }
        exit();
    }

    // Ustawienie zmiennych środowiskowych dostępnych w SVG
    $_ENV['API_BASE_URL'] = getenv('API_BASE_URL') ?: 'http://localhost:8090';
    $_ENV['MQTT_BROKER'] = getenv('MQTT_BROKER') ?: 'mosquitto';
    $_ENV['MQTT_PORT'] = getenv('MQTT_PORT') ?: '1883';

    // Włączenie pliku SVG (wykonanie PHP wewnątrz)
    include $path;
    return true;
}

// Obsługa plików statycznych
if (file_exists($path) && is_file($path)) {
    error_log("[Router] Serwowanie pliku statycznego: $uri");
    // Określenie MIME type
    $mime_types = [
        'css' => 'text/css',
        'js' => 'application/javascript',
        'json' => 'application/json',
        'xml' => 'application/xml',
        'png' => 'image/png',
        'jpg' => 'image/jpeg',
        'jpeg' => 'image/jpeg',
        'gif' => 'image/gif',
        'ico' => 'image/x-icon'
    ];

    $ext = pathinfo($path, PATHINFO_EXTENSION);
    $mime_type = $mime_types[$ext] ?? 'application/octet-stream';

    header("Content-Type: $mime_type");
    readfile($path);
    return true;
}

// Strona główna - lista dostępnych plików SVG
if ($uri === '/' || $uri === '') {
    header('Content-Type: text/html; charset=UTF-8');
    ?>
    <!DOCTYPE html>
    <html>
    <head>
        <title>PHP+SVG Client Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .app-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .app-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                text-decoration: none;
                color: #333;
                transition: transform 0.2s;
            }
            .app-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .app-card h3 {
                margin: 0 0 10px 0;
                color: #007bff;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                background: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 5px;
                color: #155724;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 PHP+SVG Client Dashboard</h1>
            <div class="status">
                <strong>Status:</strong> Connected to API at <?= $_ENV['API_BASE_URL'] ?><br>
                <strong>MQTT Broker:</strong> <?= $_ENV['MQTT_BROKER'] ?>:<?= $_ENV['MQTT_PORT'] ?>
            </div>

            <div class="app-list">
                <a href="/rest.php.svg" class="app-card">
                    <h3>📡 REST API Client</h3>
                    <p>Interactive REST API testing interface with real-time responses</p>
                </a>

                <a href="/mqtt.php.svg" class="app-card">
                    <h3>📨 MQTT Client</h3>
                    <p>MQTT publish/subscribe client with topic management</p>
                </a>
            </div>
        </div>
    </body>
    </html>
    <?php
    return true;
}

// 404 dla nieistniejących plików
error_log("[Router] 404 Not Found: $uri");
http_response_code(404);
echo "404 Not Found: $uri";
return false;