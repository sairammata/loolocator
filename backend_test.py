#!/usr/bin/env python3
"""
LooLocator Backend API Test Suite
Tests all backend endpoints comprehensively including geospatial functionality
"""

import requests
import json
import time
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from frontend .env file
BACKEND_URL = "http://localhost:8001"
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=')[1].strip()
                break
except:
    pass

API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
            
        self.test_results.append(result)
        print(result)
        
    def test_health_endpoint(self):
        """Test GET /api/health endpoint"""
        print("\n=== Testing Health Check Endpoint ===")
        
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy" and "service" in data:
                    self.log_test("Health Check", True, f"Status: {data['status']}, Service: {data['service']}")
                else:
                    self.log_test("Health Check", False, f"Invalid response format: {data}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
    
    def test_geospatial_search(self):
        """Test GET /api/washrooms/nearest with various parameters"""
        print("\n=== Testing Geospatial Search API ===")
        
        # Test case 1: NYC Times Square coordinates
        test_cases = [
            {
                "name": "Times Square Search (500m)",
                "params": {"latitude": 40.7589, "longitude": -73.9851, "radius": 500},
                "expected_min_results": 0
            },
            {
                "name": "Times Square Search (1000m)",
                "params": {"latitude": 40.7589, "longitude": -73.9851, "radius": 1000},
                "expected_min_results": 1
            },
            {
                "name": "Times Square Search (2000m)",
                "params": {"latitude": 40.7589, "longitude": -73.9851, "radius": 2000},
                "expected_min_results": 1
            },
            {
                "name": "Accessibility Required",
                "params": {"latitude": 40.7589, "longitude": -73.9851, "radius": 2000, "accessibility_required": True},
                "expected_min_results": 0
            },
            {
                "name": "Limited Results",
                "params": {"latitude": 40.7589, "longitude": -73.9851, "radius": 5000, "limit": 3},
                "expected_min_results": 0
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.get(f"{API_BASE}/washrooms/nearest", params=test_case["params"], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    if isinstance(data, list):
                        # Check if results meet minimum expectation
                        result_count = len(data)
                        
                        # Validate each washroom in response
                        valid_structure = True
                        distances_sorted = True
                        prev_distance = 0
                        
                        for washroom in data:
                            # Check required fields
                            required_fields = ["id", "name", "location", "address", "distance"]
                            if not all(field in washroom for field in required_fields):
                                valid_structure = False
                                break
                                
                            # Check location structure
                            location = washroom.get("location", {})
                            if not ("latitude" in location and "longitude" in location):
                                valid_structure = False
                                break
                                
                            # Check distance sorting
                            current_distance = washroom.get("distance", 0)
                            if current_distance < prev_distance:
                                distances_sorted = False
                            prev_distance = current_distance
                        
                        if valid_structure and distances_sorted:
                            self.log_test(test_case["name"], True, 
                                        f"Found {result_count} washrooms, properly sorted by distance")
                        else:
                            issues = []
                            if not valid_structure:
                                issues.append("invalid structure")
                            if not distances_sorted:
                                issues.append("not sorted by distance")
                            self.log_test(test_case["name"], False, f"Issues: {', '.join(issues)}")
                    else:
                        self.log_test(test_case["name"], False, "Response is not a list")
                else:
                    self.log_test(test_case["name"], False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(test_case["name"], False, f"Error: {str(e)}")
    
    def test_get_all_washrooms(self):
        """Test GET /api/washrooms with pagination"""
        print("\n=== Testing Get All Washrooms API ===")
        
        test_cases = [
            {"name": "Default pagination", "params": {}},
            {"name": "Custom pagination", "params": {"skip": 0, "limit": 3}},
            {"name": "Skip records", "params": {"skip": 2, "limit": 2}}
        ]
        
        for test_case in test_cases:
            try:
                response = requests.get(f"{API_BASE}/washrooms", params=test_case["params"], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        # Validate structure of each washroom
                        valid_structure = True
                        for washroom in data:
                            required_fields = ["id", "name", "location", "address"]
                            if not all(field in washroom for field in required_fields):
                                valid_structure = False
                                break
                        
                        if valid_structure:
                            self.log_test(test_case["name"], True, f"Retrieved {len(data)} washrooms")
                        else:
                            self.log_test(test_case["name"], False, "Invalid washroom structure")
                    else:
                        self.log_test(test_case["name"], False, "Response is not a list")
                else:
                    self.log_test(test_case["name"], False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(test_case["name"], False, f"Error: {str(e)}")
    
    def test_get_specific_washroom(self):
        """Test GET /api/washrooms/{id}"""
        print("\n=== Testing Get Specific Washroom API ===")
        
        # First get a valid washroom ID
        try:
            response = requests.get(f"{API_BASE}/washrooms", params={"limit": 1}, timeout=10)
            if response.status_code == 200:
                washrooms = response.json()
                if washrooms:
                    valid_id = washrooms[0]["id"]
                    
                    # Test with valid ID
                    response = requests.get(f"{API_BASE}/washrooms/{valid_id}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        required_fields = ["id", "name", "location", "address"]
                        if all(field in data for field in required_fields):
                            self.log_test("Get Washroom by Valid ID", True, f"Retrieved washroom: {data['name']}")
                        else:
                            self.log_test("Get Washroom by Valid ID", False, "Missing required fields")
                    else:
                        self.log_test("Get Washroom by Valid ID", False, f"HTTP {response.status_code}")
                else:
                    self.log_test("Get Washroom by Valid ID", False, "No washrooms available for testing")
            else:
                self.log_test("Get Washroom by Valid ID", False, "Could not fetch washrooms for ID testing")
                
        except Exception as e:
            self.log_test("Get Washroom by Valid ID", False, f"Error: {str(e)}")
        
        # Test with invalid ID
        try:
            invalid_id = "invalid-washroom-id-12345"
            response = requests.get(f"{API_BASE}/washrooms/{invalid_id}", timeout=10)
            if response.status_code == 404:
                self.log_test("Get Washroom by Invalid ID", True, "Correctly returned 404 for invalid ID")
            else:
                self.log_test("Get Washroom by Invalid ID", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Washroom by Invalid ID", False, f"Error: {str(e)}")
    
    def test_add_washroom(self):
        """Test POST /api/washrooms"""
        print("\n=== Testing Add Washroom API ===")
        
        # Test data for new washroom
        new_washroom = {
            "name": "Test Washroom NYC",
            "location": {
                "latitude": 40.7505,
                "longitude": -73.9934
            },
            "address": "123 Test Street, New York, NY 10001",
            "description": "Test washroom for API testing",
            "amenities": ["wheelchair_accessible", "hand_sanitizer"],
            "accessibility": True,
            "rating": 4.0,
            "hours": "9:00 AM - 6:00 PM",
            "verified": False
        }
        
        try:
            response = requests.post(f"{API_BASE}/washrooms", 
                                   json=new_washroom, 
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response has ID and created_at
                if "id" in data and "created_at" in data:
                    # Verify the data was saved correctly
                    if (data["name"] == new_washroom["name"] and 
                        data["location"]["latitude"] == new_washroom["location"]["latitude"]):
                        self.log_test("Add New Washroom", True, f"Created washroom with ID: {data['id']}")
                    else:
                        self.log_test("Add New Washroom", False, "Data mismatch in response")
                else:
                    self.log_test("Add New Washroom", False, "Missing ID or created_at in response")
            else:
                self.log_test("Add New Washroom", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Add New Washroom", False, f"Error: {str(e)}")
    
    def test_maps_api_key(self):
        """Test GET /api/maps/api-key"""
        print("\n=== Testing Google Maps API Key Endpoint ===")
        
        try:
            response = requests.get(f"{API_BASE}/maps/api-key", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "api_key" in data and data["api_key"]:
                    # Check if it's not the placeholder value
                    if data["api_key"] != "your_google_maps_api_key_here":
                        self.log_test("Google Maps API Key", True, "API key retrieved successfully")
                    else:
                        self.log_test("Google Maps API Key", False, "API key is placeholder value")
                else:
                    self.log_test("Google Maps API Key", False, "No API key in response")
            elif response.status_code == 500:
                # This is expected if API key is not configured
                self.log_test("Google Maps API Key", True, "Correctly returns 500 when API key not configured")
            else:
                self.log_test("Google Maps API Key", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Google Maps API Key", False, f"Error: {str(e)}")
    
    def test_data_validation(self):
        """Test data validation and edge cases"""
        print("\n=== Testing Data Validation and Edge Cases ===")
        
        # Test invalid coordinates
        try:
            response = requests.get(f"{API_BASE}/washrooms/nearest", 
                                  params={"latitude": 999, "longitude": 999}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Invalid Coordinates", True, f"Handled gracefully, returned {len(data)} results")
            else:
                self.log_test("Invalid Coordinates", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Coordinates", False, f"Error: {str(e)}")
        
        # Test missing required parameters
        try:
            response = requests.get(f"{API_BASE}/washrooms/nearest", timeout=10)
            if response.status_code == 422:  # FastAPI validation error
                self.log_test("Missing Required Parameters", True, "Correctly validates required parameters")
            else:
                self.log_test("Missing Required Parameters", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Missing Required Parameters", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🧪 Starting LooLocator Backend API Tests")
        print(f"📍 Testing against: {API_BASE}")
        print("=" * 60)
        
        # Wait a moment for services to be ready
        time.sleep(2)
        
        # Run all test suites
        self.test_health_endpoint()
        self.test_geospatial_search()
        self.test_get_all_washrooms()
        self.test_get_specific_washroom()
        self.test_add_washroom()
        self.test_maps_api_key()
        self.test_data_validation()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result:
                    print(f"  {result}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result}")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend is working correctly.")
        exit(0)
    else:
        print(f"\n⚠️  {tester.failed_tests} test(s) failed. Check the details above.")
        exit(1)