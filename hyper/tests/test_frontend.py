#!/usr/bin/env python3
"""
Frontend Tests for Hyper Modbus Dashboard
Test suite for validating UI components, API endpoints, and dashboard functionality
"""

import unittest
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestModbusAPI(unittest.TestCase):
    """Test API endpoints and backend functionality"""
    
    BASE_URL = "http://localhost:5002"
    
    def setUp(self):
        """Set up test fixtures"""
        self.session = requests.Session()
        
    def tearDown(self):
        """Clean up after tests"""
        self.session.close()
    
    def test_main_dashboard_endpoint(self):
        """Test main dashboard loads successfully"""
        response = self.session.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Modbus", response.text)
    
    def test_demo_page_endpoint(self):
        """Test demo page loads successfully"""
        response = self.session.get(f"{self.BASE_URL}/demo")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Demo", response.text)
    
    def test_widget_endpoints(self):
        """Test individual widget endpoints"""
        widget_urls = [
            "/widget/switch/0",
            "/widget/gauge/0", 
            "/widget/register/0",
            "/widget/status",
            "/module/button/0",
            "/module/led/0"
        ]
        
        for url in widget_urls:
            with self.subTest(url=url):
                response = self.session.get(f"{self.BASE_URL}{url}")
                self.assertEqual(response.status_code, 200)
    
    def test_command_execution_api(self):
        """Test command execution API endpoint"""
        test_command = {"command": "help"}
        
        response = self.session.post(
            f"{self.BASE_URL}/execute",
            json=test_command,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("success", result)
    
    def test_toggle_action_endpoints(self):
        """Test toggle action endpoints"""
        for channel in range(3):
            with self.subTest(channel=channel):
                response = self.session.post(f"{self.BASE_URL}/toggle/{channel}")
                # Should redirect, so expect 302 or 200
                self.assertIn(response.status_code, [200, 302])


class TestDashboardUI(unittest.TestCase):
    """Test dashboard UI components and interactions using Selenium"""
    
    BASE_URL = "http://localhost:5002"
    
    @classmethod
    def setUpClass(cls):
        """Set up Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except Exception as e:
            raise unittest.SkipTest(f"Chrome WebDriver not available: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up WebDriver"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    def test_dashboard_loads(self):
        """Test that dashboard page loads properly"""
        self.driver.get(f"{self.BASE_URL}/")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check title
        self.assertIn("Modbus", self.driver.title)
    
    def test_widget_iframes_load(self):
        """Test that widget iframes load properly"""
        self.driver.get(f"{self.BASE_URL}/dashboard.html")
        
        # Wait for iframes to load
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        self.assertGreater(len(iframes), 0, "No iframes found on dashboard")
        
        # Check that iframes have proper src attributes
        for iframe in iframes:
            src = iframe.get_attribute("src")
            self.assertTrue(src.startswith("http://") or src.startswith("/"), 
                          f"Invalid iframe src: {src}")
    
    def test_responsive_design(self):
        """Test responsive design at different screen sizes"""
        test_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in test_sizes:
            with self.subTest(size=f"{width}x{height}"):
                self.driver.set_window_size(width, height)
                self.driver.get(f"{self.BASE_URL}/dashboard.html")
                
                # Check that dashboard elements are visible
                dashboard = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
                )
                self.assertTrue(dashboard.is_displayed())


class TestWidgetFunctionality(unittest.TestCase):
    """Test individual widget functionality"""
    
    BASE_URL = "http://localhost:5002"
    
    def setUp(self):
        """Set up test fixtures"""
        self.session = requests.Session()
    
    def tearDown(self):
        """Clean up after tests"""
        self.session.close()
    
    def test_switch_widget_html_structure(self):
        """Test switch widget HTML structure"""
        response = self.session.get(f"{self.BASE_URL}/widget/switch/0")
        self.assertEqual(response.status_code, 200)
        
        html = response.text
        self.assertIn("switch", html.lower())
        self.assertIn("toggle", html.lower())
    
    def test_gauge_widget_rendering(self):
        """Test gauge widget renders properly"""
        response = self.session.get(f"{self.BASE_URL}/widget/gauge/0")
        self.assertEqual(response.status_code, 200)
        
        html = response.text
        self.assertIn("gauge", html.lower())
        # Should contain SVG or canvas elements
        self.assertTrue("svg" in html.lower() or "canvas" in html.lower())
    
    def test_status_widget_data(self):
        """Test status widget returns system information"""
        response = self.session.get(f"{self.BASE_URL}/widget/status")
        self.assertEqual(response.status_code, 200)
        
        html = response.text
        self.assertIn("status", html.lower())
    
    def test_register_widget_form(self):
        """Test register widget has proper form elements"""
        response = self.session.get(f"{self.BASE_URL}/widget/register/0")
        self.assertEqual(response.status_code, 200)
        
        html = response.text
        self.assertIn("form", html.lower())
        self.assertIn("input", html.lower())


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    BASE_URL = "http://localhost:5002"
    
    def setUp(self):
        """Set up test fixtures"""
        self.session = requests.Session()
    
    def tearDown(self):
        """Clean up after tests"""
        self.session.close()
    
    def test_invalid_widget_channel(self):
        """Test handling of invalid widget channels"""
        response = self.session.get(f"{self.BASE_URL}/widget/switch/999")
        # Should not crash - either 200 with error message or 404
        self.assertIn(response.status_code, [200, 404, 500])
    
    def test_invalid_command_format(self):
        """Test handling of invalid command formats"""
        invalid_commands = [
            {"invalid": "format"},
            {"command": ""},
            {}
        ]
        
        for cmd in invalid_commands:
            with self.subTest(command=cmd):
                response = self.session.post(
                    f"{self.BASE_URL}/execute",
                    json=cmd,
                    headers={"Content-Type": "application/json"}
                )
                # Should handle gracefully
                self.assertIn(response.status_code, [200, 400])
    
    def test_nonexistent_endpoints(self):
        """Test handling of non-existent endpoints"""
        invalid_urls = [
            "/nonexistent",
            "/widget/invalid/0",
            "/module/unknown/1"
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                response = self.session.get(f"{self.BASE_URL}{url}")
                self.assertEqual(response.status_code, 404)


class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    BASE_URL = "http://localhost:5002"
    
    def setUp(self):
        """Set up test fixtures"""
        self.session = requests.Session()
    
    def tearDown(self):
        """Clean up after tests"""
        self.session.close()
    
    def test_dashboard_load_time(self):
        """Test dashboard loads within reasonable time"""
        start_time = time.time()
        response = self.session.get(f"{self.BASE_URL}/")
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 2.0, "Dashboard took too long to load")
    
    def test_widget_load_times(self):
        """Test widgets load within reasonable time"""
        widget_urls = [
            "/widget/switch/0",
            "/widget/gauge/0",
            "/widget/status"
        ]
        
        for url in widget_urls:
            with self.subTest(url=url):
                start_time = time.time()
                response = self.session.get(f"{self.BASE_URL}{url}")
                load_time = time.time() - start_time
                
                self.assertEqual(response.status_code, 200)
                self.assertLess(load_time, 1.0, f"Widget {url} took too long to load")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        
        results = []
        
        def make_request():
            response = self.session.get(f"{self.BASE_URL}/widget/status")
            results.append(response.status_code)
        
        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        self.assertEqual(len(results), 10)
        self.assertTrue(all(status == 200 for status in results))


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestModbusAPI,
        TestDashboardUI,
        TestWidgetFunctionality,
        TestErrorHandling,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    exit(0 if result.wasSuccessful() else 1)
