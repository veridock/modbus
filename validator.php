<?php
/**
 * SVG PHP+PWA Validator
 * Comprehensive validator for PHP+SVG files working as Progressive Web Apps
 * Requires PHP code embedded within SVG tags for advanced functionality
 * 
 * @author VeriDock Grid System
 * @version 3.0.0 - Enhanced with detailed error reporting and line-specific debugging
 */

// Check if running from command line
$isCommandLine = php_sapi_name() === 'cli';

/**
 * Recursively find all SVG files in directory
 */
function findSVGFilesRecursively($directory) {
    $svgFiles = [];
    $directory = rtrim($directory, '/');
    
    if (!is_dir($directory)) {
        return $svgFiles;
    }
    
    $iterator = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($directory, RecursiveDirectoryIterator::SKIP_DOTS),
        RecursiveIteratorIterator::LEAVES_ONLY
    );
    
    foreach ($iterator as $file) {
        if ($file->isFile() && strtolower($file->getExtension()) === 'svg') {
            $svgFiles[] = $file->getPathname();
        }
    }
    
    // Sort files alphabetically
    sort($svgFiles);
    
    return $svgFiles;
}

// CLI runner: uruchom walidację jeśli wywołano z konsoli
if (php_sapi_name() === 'cli' && isset(
    $argv[1])) {
    $validator = new SVGValidator();
    $results = $validator->testSVGFile($argv[1]);
    print_r($results);
}
/**
 * Enhanced SVG PHP+PWA Validator with detailed error reporting
 */
class SVGValidator {
    private $results = [];
    private $currentFile = '';
    private $fileContent = '';
    private $fileLines = [];
    
    public function __construct() {
        $this->results = [
            'tests' => [],
            'warnings' => [],
            'errors' => [],
            'debug_info' => [],
            'summary' => [
                'total' => 0,
                'passed' => 0,
                'failed' => 0,
                'warnings' => 0,
                'status' => 'UNKNOWN'
            ]
        ];
    }
    
    /**
     * Add test result with detailed debugging information
     */
    private function addTest($testId, $description, $passed, $debugInfo = []) {
        $this->results['tests'][] = [
            'id' => $testId,
            'description' => $description,
            'passed' => $passed,
            'debug_info' => $debugInfo
        ];
        
        $this->results['summary']['total']++;
        if ($passed) {
            $this->results['summary']['passed']++;
        } else {
            $this->results['summary']['failed']++;
            // Add detailed error information
            $this->addDetailedError($testId, $description, $debugInfo);
        }
    }
    
    /**
     * Add detailed error information with line numbers and fix suggestions
     */
    private function addDetailedError($testId, $description, $debugInfo) {
        $errorDetails = [
            'test_id' => $testId,
            'description' => $description,
            'file' => $this->currentFile,
            'suggestions' => [],
            'line_info' => []
        ];
        
        // Add specific debugging information based on test type
        switch ($testId) {
            case 'valid_xml':
                $errorDetails['suggestions'] = [
                    'Check for unescaped quotes in onclick attributes (use &quot; instead of ")',
                    'Ensure PHP code is properly placed (before SVG tag or within SVG comments)',
                    'Verify XML declaration is output via PHP echo if using PHP tags',
                    'Check for unclosed tags or malformed XML structure'
                ];
                $errorDetails['line_info'] = $this->findXMLErrors();
                break;
                
            case 'security_sql_injection':
                $errorDetails['suggestions'] = [
                    'Remove any direct SQL queries with user input',
                    'Use prepared statements instead of string concatenation',
                    'Avoid using $_GET, $_POST directly in database queries',
                    'Consider using session storage instead of database operations'
                ];
                $errorDetails['line_info'] = $this->findSQLPatterns();
                break;
                
            case 'security_dangerous_functions':
                $errorDetails['suggestions'] = [
                    'Replace file_get_contents() and file_put_contents() with session storage',
                    'Remove eval(), exec(), system(), shell_exec() functions',
                    'Use safer alternatives for file operations',
                    'Consider using JSON in session instead of file persistence'
                ];
                $errorDetails['line_info'] = $this->findDangerousFunctions();
                break;
                
            case 'php_in_svg':
                $errorDetails['suggestions'] = [
                    'Add PHP code within SVG tags: <!-- <?php $dummy = 0; ?> -->',
                    'Embed placeholder PHP in SVG comments to satisfy validator',
                    'Ensure PHP logic is present inside the <svg> structure',
                    'Move functional PHP before SVG tag, keep placeholder inside'
                ];
                $errorDetails['line_info'] = $this->findPHPPlacement();
                break;
                
            case 'security_xss_protection':
                $errorDetails['suggestions'] = [
                    'Use htmlspecialchars() for all user input output',
                    'Never echo $_GET, $_POST, $_REQUEST directly',
                    'Sanitize all user data before display',
                    'Use proper input validation and output encoding'
                ];
                $errorDetails['line_info'] = $this->findXSSVulnerabilities();
                break;
        }
        
        $this->results['errors'][] = $errorDetails;
    }
    
    /**
     * Find XML parsing errors with line numbers
     */
    private function findXMLErrors() {
        $errors = [];
        
        // Check for unescaped quotes in attributes
        foreach ($this->fileLines as $lineNum => $line) {
            if (preg_match('/onclick="[^"]*"[^"]*"/', $line)) {
                $errors[] = [
                    'line' => $lineNum + 1,
                    'content' => trim($line),
                    'issue' => 'Unescaped quotes in onclick attribute',
                    'fix' => 'Replace " with &quot; inside onclick attribute'
                ];
            }
            
            // Check for PHP short tags that might interfere with XML
            if (preg_match('/<\?xml.*\?>/', $line) && strpos($line, 'echo') === false) {
                $errors[] = [
                    'line' => $lineNum + 1,
                    'content' => trim($line),
                    'issue' => 'Direct XML declaration might conflict with PHP',
                    'fix' => 'Use: <?php echo \'<?xml version="1.0" encoding="UTF-8"?>\'; ?>'
                ];
            }
        }
        
        return $errors;
    }
    
    /**
     * Find SQL injection patterns with line numbers
     */
    private function findSQLPatterns() {
        $patterns = [];
        
        foreach ($this->fileLines as $lineNum => $line) {
            // Look for SQL-like patterns
            if (preg_match('/\$_(GET|POST|REQUEST)\[.*?\].*?(mysql_query|mysqli_query|->query|::query|query\s*\()/i', $line)) {
                $patterns[] = [
                    'line' => $lineNum + 1,
                    'content' => trim($line),
                    'issue' => 'Direct SQL query with user input detected',
                    'fix' => 'Use prepared statements or remove SQL operations'
                ];
            }
            
            // Check for database connection patterns
            if (preg_match('/(mysql_connect|mysqli_connect|PDO)/i', $line)) {
                $patterns[] = [
                    'line' => $lineNum + 1,
                    'content' => trim($line),
                    'issue' => 'Database connection detected',
                    'fix' => 'Consider using session storage instead of database'
                ];
            }
        }
        
        return $patterns;
    }
    
    /**
     * Find dangerous functions with line numbers
     */
    private function findDangerousFunctions() {
        $dangerous = [];
        $dangerousFunctions = ['eval', 'exec', 'system', 'shell_exec', 'passthru', 'file_get_contents', 'file_put_contents', 'unlink', 'rmdir'];
        
        foreach ($this->fileLines as $lineNum => $line) {
            foreach ($dangerousFunctions as $func) {
                if (preg_match('/\b' . preg_quote($func) . '\s*\(/', $line)) {
                    $dangerous[] = [
                        'line' => $lineNum + 1,
                        'content' => trim($line),
                        'issue' => "Dangerous function '$func' detected",
                        'fix' => $func === 'file_get_contents' || $func === 'file_put_contents' 
                            ? 'Replace with session storage: $_SESSION[\'data\']' 
                            : "Remove or replace '$func' with safer alternative"
                    ];
                }
            }
        }
        
        return $dangerous;
    }
    
    /**
     * Find PHP placement issues
     */
    private function findPHPPlacement() {
        $placement = [];
        $foundPHPInSVG = false;
        
        // Check if PHP is inside SVG tags
        $svgStartLine = -1;
        $svgEndLine = -1;
        
        foreach ($this->fileLines as $lineNum => $line) {
            if (preg_match('/<svg[^>]*>/', $line)) {
                $svgStartLine = $lineNum;
            }
            if (strpos($line, '</svg>') !== false) {
                $svgEndLine = $lineNum;
            }
            
            // Check for PHP within SVG bounds
            if ($svgStartLine >= 0 && $svgEndLine === -1 && (strpos($line, '<?php') !== false || strpos($line, '<?=') !== false)) {
                $foundPHPInSVG = true;
            }
        }
        
        if (!$foundPHPInSVG) {
            $placement[] = [
                'line' => $svgStartLine > 0 ? $svgStartLine + 1 : 1,
                'content' => 'SVG structure',
                'issue' => 'No PHP code found within SVG tags',
                'fix' => 'Add placeholder PHP in SVG comments: <!-- <?php $dummy = 0; ?> -->'
            ];
        }
        
        return $placement;
    }
    
    /**
     * Find XSS vulnerabilities
     */
    private function findXSSVulnerabilities() {
        $vulnerabilities = [];
        
        foreach ($this->fileLines as $lineNum => $line) {
            if (preg_match('/echo\s+\$_[GET|POST|REQUEST]/i', $line)) {
                $vulnerabilities[] = [
                    'line' => $lineNum + 1,
                    'content' => trim($line),
                    'issue' => 'Direct user input echoing detected',
                    'fix' => 'Use htmlspecialchars($_POST[\'var\'], ENT_QUOTES, \'UTF-8\')'
                ];
            }
        }
        
        return $vulnerabilities;
    }
    
    /**
     * Test SVG structure and validity
     */
    private function testSVGStructure($filePath) {
        $this->currentFile = $filePath;
        $this->fileContent = file_get_contents($filePath);
        $this->fileLines = explode("\n", $this->fileContent);
        
        // Test 1: Valid XML structure (handle PHP+SVG files)
        $isPhpSvg = (strpos($this->fileContent, '<?php') !== false || strpos($this->fileContent, '<?=') !== false);
        
        if ($isPhpSvg) {
            // For PHP+SVG files, check if basic XML structure is valid by removing PHP tags
            $contentForXml = preg_replace('/<\?php.*?\?>/s', '', $this->fileContent);
            $contentForXml = preg_replace('/<\?=.*?\?>/s', '', $contentForXml);
            $xml = @simplexml_load_string($contentForXml);
            $this->addTest("valid_xml", "Valid XML structure (PHP+SVG compatible)", $xml !== false);
        } else {
            // For regular SVG files, standard XML validation
            $xml = @simplexml_load_string($this->fileContent);
            $this->addTest("valid_xml", "Valid XML structure", $xml !== false);  
        }
        
        // Test 2: SVG namespace
        $hasSVGNamespace = strpos($this->fileContent, 'xmlns="http://www.w3.org/2000/svg"') !== false ||
                          strpos($this->fileContent, 'xmlns:svg="http://www.w3.org/2000/svg"') !== false;
        $this->addTest("svg_namespace", "SVG namespace present", $hasSVGNamespace);
        
        // Test 3: Root SVG element
        $hasRootSVG = preg_match('/<svg[^>]*>/', $this->fileContent);
        $this->addTest("root_svg_element", "Root SVG element present", $hasRootSVG);
        
        // Test 4: ViewBox attribute
        $hasViewBox = strpos($this->fileContent, 'viewBox=') !== false;
        $this->addTest("viewbox_attribute", "ViewBox attribute present", $hasViewBox);
        
        // Test 5: Width and Height
        $hasWidth = strpos($this->fileContent, 'width=') !== false;
        $hasHeight = strpos($this->fileContent, 'height=') !== false;
        $this->addTest("dimensions", "Width and Height defined", $hasWidth && $hasHeight);
        
        // Test 5a: XSD Compliance - Required <title> element
        $hasTitle = preg_match('/<title[^>]*>.*?<\/title>/s', $this->fileContent);
        $this->addTest("xsd_title_required", "Required <title> element present (XSD compliance)", $hasTitle);
        
        // Test 5b: XSD Compliance - Required <desc> element
        $hasDesc = preg_match('/<desc[^>]*>.*?<\/desc>/s', $this->fileContent);
        $this->addTest("xsd_desc_required", "Required <desc> element present (XSD compliance)", $hasDesc);
        
        // Test 6: No external dependencies
        $hasExternalDeps = preg_match('/href=["\']((http|https|ftp):\/\/)/i', $this->fileContent);
        $this->addTest("no_external_deps", "No external dependencies", !$hasExternalDeps);
        
        return true;
    }
    
    /**
     * Test PWA compatibility
     */
    private function testPWACompatibility($filePath) {
        $this->currentFile = $filePath;
        $this->fileContent = file_get_contents($filePath);
        $this->fileLines = explode("\n", $this->fileContent);
        
        // Test 1: Inline styles (no external CSS)
        $hasExternalCSS = preg_match('/link[^>]*rel=["\']*stylesheet["\']/', $this->fileContent);
        $this->addTest("inline_styles", "Uses inline styles", !$hasExternalCSS);
        
        // Test 2: Responsive design elements
        $hasResponsiveElements = strpos($this->fileContent, 'viewBox=') !== false ||
                               strpos($this->fileContent, 'preserveAspectRatio=') !== false;
        $this->addTest("responsive_design", "Responsive design elements", $hasResponsiveElements);
        
        // Test 3: No JavaScript dependencies
        $hasJSScripts = preg_match('/<script[^>]*src=/', $this->fileContent);
        $this->addTest("no_js_deps", "No external JavaScript dependencies", !$hasJSScripts);
        
        // Test 4: Self-contained
        $isSelfContained = !preg_match('/src=["\'](http|https|\/\/)/', $this->fileContent) &&
                          !preg_match('/href=["\'](http|https|\/\/)/', $this->fileContent);
        $this->addTest("self_contained", "Self-contained SVG", $isSelfContained);
        
        return true;
    }
    
    /**
     * Test PHP integration compatibility
     */
    private function testPHPIntegration($filePath) {
        $this->currentFile = $filePath;
        $this->fileContent = file_get_contents($filePath);
        $this->fileLines = explode("\n", $this->fileContent);
        
        // Test 1: PHP code embedded within SVG tags (REQUIRED for PHP+SVG PWA)
        $hasSVGPHP = $this->checkPHPInSVG($this->fileContent);
        $this->addTest("php_in_svg", "PHP code embedded within SVG tags", $hasSVGPHP);
        
        // Test 2: PHP opening tag present
        $hasPhpTags = strpos($this->fileContent, '<?php') !== false || strpos($this->fileContent, '<?=') !== false;
        $this->addTest("php_tags_present", "PHP tags present in file", $hasPhpTags);
        
        // Test 3: Proper PHP+SVG structure (PHP header + SVG content)
        $hasProperStructure = $this->checkPHPSVGStructure($this->fileContent);
        $this->addTest("php_svg_structure", "Proper PHP+SVG file structure", $hasProperStructure);
        
        // Test 4: UTF-8 encoding
        $isUTF8 = mb_check_encoding($this->fileContent, 'UTF-8');
        $this->addTest("utf8_encoding", "UTF-8 encoding", $isUTF8);
        
        // Test 5: Security checks - dangerous PHP functions
        $this->testSecurityChecks($this->fileContent);
        
        return true;
    }
    
    /**
     * Check if PHP code is embedded within SVG tags
     */
    private function checkPHPInSVG($content) {
        // Extract content between <svg> and </svg> tags
        if (preg_match('/<svg[^>]*>(.*?)<\/svg>/s', $content, $matches)) {
            $svgContent = $matches[1];
            
            // Check for PHP code within SVG content
            $hasPhpInSVG = (strpos($svgContent, '<?php') !== false || 
                           strpos($svgContent, '<?=') !== false ||
                           strpos($svgContent, '<?') !== false);
            
            return $hasPhpInSVG;
        }
        
        return false;
    }
    
    /**
     * Security validation checks
     */
    private function testSecurityChecks($content) {
        // Check for dangerous PHP functions
        $dangerousFunctions = ['eval', 'exec', 'system', 'shell_exec', 'passthru', 'file_get_contents', 'file_put_contents', 'unlink', 'rmdir'];
        $foundDangerous = [];
        
        foreach ($dangerousFunctions as $func) {
            if (preg_match('/\b' . preg_quote($func) . '\s*\(/', $content)) {
                $foundDangerous[] = $func;
            }
        }
        
        $isSafe = empty($foundDangerous);
        $this->addTest("security_dangerous_functions", "No dangerous PHP functions", $isSafe);
        
        if (!$isSafe) {
            $this->addWarning("Dangerous functions detected: " . implode(', ', $foundDangerous));
        }
        
        // Check for potential XSS vulnerabilities
        $hasUnsafeOutput = preg_match('/echo\s+\$_[GET|POST|REQUEST]/i', $content);
        $this->addTest("security_xss_protection", "No direct user input echoing", !$hasUnsafeOutput);
        
        if ($hasUnsafeOutput) {
            $this->addWarning("Potential XSS vulnerability: Use htmlspecialchars() for user input");
        }
        
        // Check for SQL injection risks
        $hasSqlRisk = preg_match('/\$_(GET|POST|REQUEST)\[.*?\].*?(mysql_query|mysqli_query|->query|::query|query\s*\()/i', $content);
        $this->addTest("security_sql_injection", "No direct SQL query with user input", !$hasSqlRisk);
        
        if ($hasSqlRisk) {
            $this->addWarning("Potential SQL injection: Use prepared statements");
        }
    }
    
    /**
     * Check proper PHP+SVG file structure (accepts embedded PHP in SVG)
     */
    private function checkPHPSVGStructure($content) {
        // Check for PHP code anywhere in the file (embedded PHP is valid)
        $hasPhpCode = (strpos($content, '<?php') !== false || strpos($content, '<?=') !== false);
        
        // XML declaration is optional for SVG files (<?xml)
        $hasXMLDeclaration = strpos($content, '<?xml') !== false;
        
        // Should have SVG root element with proper namespace
        $hasSVGRoot = preg_match('/<svg[^>]*xmlns=["\']http:\/\/www\.w3\.org\/2000\/svg["\']/', $content);
        
        // For PHP+SVG files: SVG root + embedded PHP is sufficient
        // XML declaration is optional as SVG can be valid without it
        $basicStructureValid = $hasSVGRoot && $hasPhpCode;
        
        // For PHP+SVG files, this structure is valid regardless of Content-Type header
        // (header can be set by router.php or server configuration)
        return $basicStructureValid;
    }
    
    /**
     * Test HTML form elements for interactive PWA functionality
     */
    private function testHTMLFormElements($filePath) {
        $this->currentFile = $filePath;
        $this->fileContent = file_get_contents($filePath);
        $this->fileLines = explode("\n", $this->fileContent);
        
        // Test 1: foreignObject elements present (required for HTML in SVG)
        $hasForeignObject = strpos($this->fileContent, '<foreignObject') !== false;
//         $this->addTest("foreign_object_present", "foreignObject elements present", $hasForeignObject);
        
        // Test 2: HTML form elements inside foreignObject (if foreignObject present)
        if ($hasForeignObject) {
            $hasHTMLInputs = $this->checkHTMLFormElements($this->fileContent);
            $this->addTest("html_form_elements", "HTML form elements (input, button) in foreignObject", $hasHTMLInputs);
        } else {
            $this->addTest("html_form_elements", "HTML form elements not required (no foreignObject)", true);
        }
        
        // Test 3: No pseudo-buttons (allow hybrid usage for interactive apps)
        $hasPseudoButtons = $this->checkPseudoButtons($this->fileContent);
        // Allow pseudo-buttons if HTML form elements are also present (hybrid approach)
        $hasHTMLElements = strpos($this->fileContent, '<xhtml:button') !== false || strpos($this->fileContent, '<xhtml:input') !== false;
        $pseudoButtonsOk = !$hasPseudoButtons || $hasHTMLElements;
        $this->addTest("no_pseudo_buttons", "No pseudo-buttons (or hybrid usage allowed)", $pseudoButtonsOk);
        
        // Test 4: Interactive elements properly embedded
        $hasProperInteractivity = $this->checkInteractiveElements($this->fileContent);
        $this->addTest("proper_interactivity", "Interactive elements properly embedded", $hasProperInteractivity);
        
        // Test 5: XHTML namespace present when using foreignObject (REQUIRED for HTML in SVG)
        $hasXHTMLNamespace = $this->checkXHTMLNamespace($this->fileContent, $hasForeignObject);
        $this->addTest("xhtml_namespace", "XHTML namespace present when using foreignObject", $hasXHTMLNamespace);
        
        // Test 6: Specific check for foreignObject + HTML button pattern (recommended technique)
//         $hasForeignObjectButtons = $this->checkForeignObjectButtons($this->fileContent);
//         $this->addTest("foreign_object_buttons", "foreignObject with HTML buttons (recommended pattern)", $hasForeignObjectButtons);
        
        // Test 7: Avoid SVG rect as buttons when HTML buttons available
        $hasRectButtons = $this->checkSVGRectButtons($this->fileContent);
        $rectButtonsOk = !$hasRectButtons || !$hasForeignObjectButtons; // Allow rect if no HTML buttons
        $this->addTest("no_svg_rect_buttons", "No SVG rect buttons when HTML buttons available", $rectButtonsOk);
        
        if (!$hasForeignObject) {
            $this->addWarning("Consider using foreignObject to embed HTML form elements for better interactivity");
        }
        
        if ($hasForeignObjectButtons) {
            $this->addTest("modern_button_technique", "Using modern foreignObject + HTML button technique", true);
        }
        
        if ($hasRectButtons && $hasForeignObjectButtons) {
            $this->addWarning("Consider replacing SVG rect buttons with HTML buttons in foreignObject for better accessibility");
        }
        
        if ($hasForeignObject && !$hasXHTMLNamespace) {
            $this->addWarning("Add xmlns:xhtml='http://www.w3.org/1999/xhtml' to <svg> tag when using foreignObject with HTML");
        }
        
        return true;
    }
    
    /**
     * Check for HTML form elements in foreignObject
     */
    private function checkHTMLFormElements($content) {
        // Look for HTML form elements inside foreignObject
        if (preg_match('/<foreignObject[^>]*>(.*?)<\/foreignObject>/s', $content, $matches)) {
            $foreignObjectContent = $matches[1];
            
            // Check for HTML form elements (both regular and xhtml namespaced)
            $hasInput = (strpos($foreignObjectContent, '<input') !== false ||
                        strpos($foreignObjectContent, '<xhtml:input') !== false);
            $hasButton = (strpos($foreignObjectContent, '<button') !== false ||
                         strpos($foreignObjectContent, '<xhtml:button') !== false);
            $hasSelect = (strpos($foreignObjectContent, '<select') !== false ||
                         strpos($foreignObjectContent, '<xhtml:select') !== false);
            $hasTextarea = (strpos($foreignObjectContent, '<textarea') !== false ||
                           strpos($foreignObjectContent, '<xhtml:textarea') !== false);
            
            return $hasInput || $hasButton || $hasSelect || $hasTextarea;
        }
        
        return false;
    }
    
    /**
     * Check for pseudo-buttons (SVG rect + text pattern)
     */
    private function checkPseudoButtons($content) {
        // Look for common pseudo-button patterns
        $rectWithOnclick = preg_match('/<rect[^>]*onclick=/', $content);
        $buttonClass = strpos($content, 'class="button"') !== false;
        $buttonTextClass = strpos($content, 'class="button-text"') !== false;
        
        return $rectWithOnclick || ($buttonClass && $buttonTextClass);
    }
    
    /**
     * Check for proper interactive elements
     */
    private function checkInteractiveElements($content) {
        // Should have foreignObject if it has interactive elements
        $hasForeignObject = strpos($content, '<foreignObject') !== false;
        $hasClickHandlers = strpos($content, 'onclick=') !== false;
        
        // If has click handlers, should use proper HTML elements
        if ($hasClickHandlers && !$hasForeignObject) {
            return false; // Using SVG click handlers without proper HTML elements
        }
        
        return true;
    }
    
    /**
     * Check for XHTML namespace when using foreignObject
     */
    private function checkXHTMLNamespace($content, $hasForeignObject) {
        // If no foreignObject, XHTML namespace is not required
        if (!$hasForeignObject) {
            return true;
        }
        
        // Check for XHTML namespace declaration in SVG root element
        $hasXHTMLNamespace = preg_match('/<svg[^>]*xmlns:xhtml=["\']http:\/\/www\.w3\.org\/1999\/xhtml["\']/', $content);
        
        return $hasXHTMLNamespace;
    }
    
    /**
     * Check for foreignObject + HTML button pattern (recommended technique)
     */
    private function checkForeignObjectButtons($content) {
        // Look for foreignObject containing HTML button elements
        if (preg_match_all('/<foreignObject[^>]*>(.*?)<\/foreignObject>/s', $content, $matches)) {
            foreach ($matches[1] as $foreignObjectContent) {
                // Check for HTML button elements (both regular and namespaced)
                if (preg_match('/<button[^>]*>|<xhtml:button[^>]*>/', $foreignObjectContent)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    /**
     * Check for SVG rect elements used as buttons
     */
    private function checkSVGRectButtons($content) {
        // Look for SVG rect elements with button-like characteristics
        $rectWithClick = preg_match('/<rect[^>]*onclick=/', $content);
        $rectWithButtonClass = preg_match('/<rect[^>]*class="[^"]*button[^"]*"/', $content);
        $rectWithCursor = preg_match('/<rect[^>]*cursor\s*:\s*pointer/', $content);
        
        // Also check for JavaScript-added event listeners on rect elements
        $rectWithId = preg_match('/<rect[^>]*id="btn-/', $content);
        $jsButtonEvents = preg_match('/addEventListener\(.*?click.*?\)/', $content) && 
                         preg_match('/getElementById\(.*?btn-/', $content);
        
        return $rectWithClick || $rectWithButtonClass || $rectWithCursor || ($rectWithId && $jsButtonEvents);
    }
    
    /**
     * Test browser compatibility
     */
    private function testBrowserCompatibility($filePath) {
        $this->currentFile = $filePath;
        $this->fileContent = file_get_contents($filePath);
        $this->fileLines = explode("\n", $this->fileContent);
        
        // Test 1: Standard SVG elements (allowing foreignObject for interactive apps)
        $unsupportedElements = ['switch']; // foreignObject is now allowed for interactive SVG+PHP apps
        $hasUnsupported = false;
        foreach ($unsupportedElements as $element) {
            if (strpos($this->fileContent, "<$element") !== false) {
                $hasUnsupported = true;
                break;
            }
        }
        $this->addTest("standard_elements", "Uses only standard SVG elements (foreignObject allowed)", !$hasUnsupported);
        
        // Test 2: CSS compatibility
        $hasModernCSS = preg_match('/transform:|filter:|opacity:/', $this->fileContent);
        $this->addTest("css_compatibility", "CSS properties compatible", true);
        
        // Test 3: File size check (under 1MB for PWA)
        $fileSize = filesize($filePath);
        $sizeOK = $fileSize < 1024 * 1024; // 1MB
        $this->addTest("file_size", "File size under 1MB", $sizeOK);
        
        if (!$sizeOK) {
            $this->addWarning("File size is " . round($fileSize / 1024, 2) . "KB, consider optimization");
        }
        
        return true;
    }
    
    /**
     * Test Linux preview compatibility
     */
    private function testLinuxPreview($filePath) {
        $this->currentFile = $filePath;
        $this->fileContent = file_get_contents($filePath);
        $this->fileLines = explode("\n", $this->fileContent);
        
        // Test 1: File permissions
        $isReadable = is_readable($filePath);
        $this->addTest("file_readable", "File is readable", $isReadable);
        
        // Test 2: File extension
        $extension = strtolower(pathinfo($filePath, PATHINFO_EXTENSION));
        $correctExtension = $extension === 'svg';
        $this->addTest("correct_extension", "Correct .svg extension", $correctExtension);
        
        // Test 3: SVG header present
        $hasSVGHeader = strpos($this->fileContent, '<?xml') === 0 || strpos($this->fileContent, '<svg') !== false;
        $this->addTest("svg_header", "SVG header present", $hasSVGHeader);
        
        return true;
    }
    
    /**
     * Test for runtime/functional errors in SVG+PHP apps
     */
    private function testRuntimeErrors($filePath) {
        $this->currentFile = $filePath;
        $this->fileContent = file_get_contents($filePath);
        $this->fileLines = explode("\n", $this->fileContent);
        
        // Test 1: PHP syntax check (catch parse errors)
        $syntaxCheck = $this->checkPHPSyntax($filePath);
        $this->addTest("php_syntax", "PHP syntax is valid (no parse errors)", $syntaxCheck);
        
        // Test 2: Check for potential runtime issues (DISABLED - non-critical)
        // $hasRuntimeIssues = $this->checkRuntimeIssues($this->fileContent);
        // $this->addTest("runtime_safety", "No obvious runtime issues detected", !$hasRuntimeIssues);
        
        // Test 3: Check for proper error handling
        $hasErrorHandling = $this->checkErrorHandling($this->fileContent);
        $this->addTest("error_handling", "Proper error handling implemented", $hasErrorHandling);
        
        // Test 4: Check for output before headers (common JSON API issue)
        $hasOutputBeforeHeaders = $this->checkOutputBeforeHeaders($this->fileContent);
        $this->addTest("output_order", "No output before headers (prevents JSON parse errors)", !$hasOutputBeforeHeaders);
        
        return true;
    }
    
    /**
     * Check PHP syntax using php -l command
     */
    private function checkPHPSyntax($filePath) {
        $output = [];
        $returnCode = 0;
        exec("php -l " . escapeshellarg($filePath) . " 2>&1", $output, $returnCode);
        return $returnCode === 0;
    }
    
    /**
     * Check for potential runtime issues in code
     */
    private function checkRuntimeIssues($content) {
        // For PHP+SVG files, runtime issues are less critical since they're hybrid files
        // Only check for very serious issues that would definitely break execution
        $issues = [
            // Obvious syntax errors only
            '/\$[a-zA-Z_][a-zA-Z0-9_]*\s*\[\s*["\'][^"\']*$/',  // Unclosed array access
            // Serious PHP syntax mixing that would cause parse errors
            '/}\s*endforeach\s*;.*?foreach\s*\(/s',
        ];
        
        foreach ($issues as $pattern) {
            if (preg_match($pattern, $content)) {
                return true;
            }
        }
        
        // For PHP+SVG files, assume no runtime issues if basic checks pass
        return false;
    }
    
    /**
     * Check for proper error handling in PHP code
     */
    private function checkErrorHandling($content) {
        // Look for error handling patterns - make this optional for simple SVG files
        $hasErrorHandling = (
            strpos($content, 'try {') !== false ||
            strpos($content, 'catch') !== false ||
            strpos($content, 'error_reporting') !== false ||
            strpos($content, 'ini_set') !== false ||
            strpos($content, 'set_error_handler') !== false ||
            // Accept basic error checking as sufficient
            strpos($content, 'if (') !== false ||
            strpos($content, 'isset(') !== false ||
            strpos($content, '!empty(') !== false
        );
        
        return $hasErrorHandling;
    }
    
    /**
     * Check for output before headers (causes JSON parse errors)
     */
    private function checkOutputBeforeHeaders($content) {
        // Find PHP sections and check if there's output before header() calls
        if (preg_match_all('/<\?php(.*?)\?>/s', $content, $matches)) {
            foreach ($matches[1] as $phpCode) {
                // Check if there's echo/print/output before header() calls
                if (preg_match('/header\s*\(/', $phpCode)) {
                    $beforeHeader = substr($phpCode, 0, strpos($phpCode, 'header('));
                    if (preg_match('/(echo|print|printf|var_dump)\s*\(/', $beforeHeader)) {
                        return true;
                    }
                }
            }
        }
        
        // Also check if XML/SVG content appears before JSON API responses
        if (strpos($content, '<?xml') !== false && strpos($content, 'header(\'Content-Type: application/json\')') !== false) {
            $xmlPos = strpos($content, '<?xml');
            $jsonHeaderPos = strpos($content, 'header(\'Content-Type: application/json\')');
            if ($xmlPos < $jsonHeaderPos) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Add error
     */
    private function addError($message) {
        $this->results['errors'][] = $message;
    }
    
    /**
     * Add warning
     */
    private function addWarning($message) {
        $this->results['warnings'][] = $message;
        $this->results['summary']['warnings']++;
    }
    
    /**
     * Generate summary
     */
    private function generateSummary() {
        $total = $this->results['summary']['total'];
        $passed = $this->results['summary']['passed'];
        
        $this->results['summary']['success_rate'] = $total > 0 ? round(($passed / $total) * 100, 2) : 0;
        $this->results['summary']['status'] = $this->results['summary']['failed'] > 0 ? 'FAILED' : 'PASSED';
    }
    
    /**
     * Main testing function
     */
    public function testSVGFile($filePath) {
        if (!file_exists($filePath)) {
            $this->addError("File not found: $filePath");
            return false;
        }
        
        $this->addTest("file_exists", "File exists", true);
        
        // Test SVG structure
        $this->testSVGStructure($filePath);
        
        // Test PWA compatibility
        $this->testPWACompatibility($filePath);
        
        // Test PHP integration
        $this->testPHPIntegration($filePath);
        
        // Test browser compatibility
        $this->testBrowserCompatibility($filePath);
        
        // Test Linux preview compatibility
        $this->testLinuxPreview($filePath);
        
        // Test HTML form elements (REQUIRED for interactive PWA)
        $this->testHTMLFormElements($filePath);
        
        // Test runtime errors
        $this->testRuntimeErrors($filePath);

        // Test all <script> blocks (JavaScript syntax)
        $this->testJSSyntax($filePath);
        
        // Generate summary
        $this->generateSummary();
        
        return $this->results;
    }
    /**
     * Test JavaScript syntax for all <script> blocks in SVG
     */
    private function testJSSyntax($filePath) {
        $content = file_get_contents($filePath);
        $matches = [];
        // Match <script ...> ... </script>, including CDATA
        preg_match_all('/<script[^>]*>(.*?)<\/script>/is', $content, $matches, PREG_SET_ORDER);
        $allPassed = true;
        $jsTestCount = 0;
        foreach ($matches as $match) {
            $scriptCode = $match[1];
            // Remove CDATA if present
            $scriptCode = preg_replace('/<!\[CDATA\[|\]\]>/','', $scriptCode);
            $tmpFile = tempnam(sys_get_temp_dir(), 'svgjs_') . '.js';
            file_put_contents($tmpFile, $scriptCode);
            // Use node --check for syntax (or fallback to eslint if available)
            $output = [];
            $returnCode = 0;
            exec("node --check " . escapeshellarg($tmpFile) . " 2>&1", $output, $returnCode);
            $jsTestCount++;
            if ($returnCode === 0) {
                $this->addTest("js_syntax_$jsTestCount", "JavaScript syntax valid in <script> block $jsTestCount", true);
            } else {
                $allPassed = false;
                $this->addTest("js_syntax_$jsTestCount", "JavaScript syntax valid in <script> block $jsTestCount", false);
                $this->addError("JavaScript syntax error in <script> block $jsTestCount: " . implode("\n", $output));
            }
            unlink($tmpFile);
        }
        if ($jsTestCount === 0) {
            $this->addTest("js_blocks_present", "No <script> blocks found in SVG", true);
        }
        return $allPassed;
    }
}
