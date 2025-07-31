#!/usr/bin/env python3
"""
Simple test runner for Hyper Modbus Dashboard
Runs basic API and functionality tests without requiring Selenium
"""

import requests
import json
import sys
import time
from datetime import datetime


class SimpleTestRunner:
    """Simple test runner for basic functionality validation"""
    
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_passed = 0
        self.tests_failed = 0
        
    def log(self, message, level="INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_endpoint(self, endpoint, expected_status=200, description=""):
        """Test a single endpoint"""
        try:
            self.log(f"Testing {endpoint} - {description}")
            response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
            
            if response.status_code == expected_status:
                self.log(f"✅ PASS: {endpoint} returned {response.status_code}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"❌ FAIL: {endpoint} returned {response.status_code}, expected {expected_status}", "FAIL")
                self.tests_failed += 1
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ FAIL: {endpoint} - Connection error: {e}", "FAIL")
            self.tests_failed += 1
            return False
    
    def test_api_endpoint(self, endpoint, data=None, expected_status=200, description=""):
        """Test an API endpoint with data"""
        try:
            self.log(f"Testing API {endpoint} - {description}")
            
            if data:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
            else:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
            
            if response.status_code == expected_status:
                self.log(f"✅ PASS: {endpoint} API returned {response.status_code}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"❌ FAIL: {endpoint} API returned {response.status_code}, expected {expected_status}", "FAIL")
                self.tests_failed += 1
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ FAIL: {endpoint} API - Connection error: {e}", "FAIL")
            self.tests_failed += 1
            return False
    
    def run_all_tests(self):
        """Run all basic tests"""
        self.log("🚀 Starting Hyper Modbus Dashboard Tests", "START")
        self.log("=" * 60)
        
        # Test main endpoints
        self.test_endpoint("/", description="Main dashboard page")
        self.test_endpoint("/demo", description="Demo page")
        
        # Test widget endpoints
        widget_tests = [
            ("/widget/switch/0", "Switch widget for channel 0"),
            ("/widget/gauge/0", "Gauge widget for register 0"),
            ("/widget/register/0", "Register widget for register 0"),
            ("/widget/status", "System status widget"),
            ("/module/button/0", "Button module for channel 0"),
            ("/module/led/0", "LED module for channel 0")
        ]
        
        for endpoint, description in widget_tests:
            self.test_endpoint(endpoint, description=description)
        
        # Test command API
        self.test_api_endpoint(
            "/execute",
            data={"command": "help"},
            description="Command execution API"
        )
        
        # Test performance (basic load time check)
        self.log("Testing basic performance...")
        start_time = time.time()
        success = self.test_endpoint("/", description="Performance test")
        load_time = time.time() - start_time
        
        if success and load_time < 2.0:
            self.log(f"✅ PASS: Dashboard loaded in {load_time:.2f}s", "PASS")
        elif success:
            self.log(f"⚠️  WARN: Dashboard loaded in {load_time:.2f}s (slow)", "WARN")
        
        # Summary
        self.log("=" * 60)
        self.log(f"🏁 Test Results: {self.tests_passed} passed, {self.tests_failed} failed")
        
        if self.tests_failed == 0:
            self.log("🎉 All tests passed!", "SUCCESS")
            return True
        else:
            self.log(f"💥 {self.tests_failed} tests failed", "ERROR")
            return False
    
    def close(self):
        """Clean up resources"""
        self.session.close()


def main():
    """Main test execution"""
    runner = SimpleTestRunner()
    
    try:
        success = runner.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        runner.log("Tests interrupted by user", "INFO")
        return 1
    finally:
        runner.close()


if __name__ == "__main__":
    sys.exit(main())
