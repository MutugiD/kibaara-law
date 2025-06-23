"""
Test script for FastAPI endpoints.
"""

import asyncio
import json
from datetime import datetime
from src.api.main import app
from fastapi.testclient import TestClient

# Create test client
client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health endpoint test passed\n")


def test_root_endpoint():
    """Test the root endpoint."""
    print("Testing root endpoint...")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Root endpoint test passed\n")


def test_search_endpoint():
    """Test the search endpoint."""
    print("Testing search endpoint...")

    # Test POST search
    search_data = {
        "query": "civil appeal damages award",
        "max_results": 5,
        "court_level": "appellate"
    }

    response = client.post("/api/v1/cases/search", json=search_data)
    print(f"POST Search Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Found {result.get('total_count', 0)} cases")
        print(f"Success: {result.get('success', False)}")
        print("✅ Search endpoint test passed")
    else:
        print(f"Error: {response.text}")
        print("❌ Search endpoint test failed")

    print()


def test_search_get_endpoint():
    """Test the GET search endpoint."""
    print("Testing GET search endpoint...")

    response = client.get("/api/v1/cases/search?query=civil%20appeal&max_results=3")
    print(f"GET Search Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Found {result.get('total_count', 0)} cases")
        print(f"Success: {result.get('success', False)}")
        print("✅ GET search endpoint test passed")
    else:
        print(f"Error: {response.text}")
        print("❌ GET search endpoint test failed")

    print()


def test_raw_cases_endpoint():
    """Test the raw cases endpoint."""
    print("Testing raw cases endpoint...")

    response = client.get("/api/v1/cases/raw?limit=5")
    print(f"Raw Cases Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Found {result.get('total_count', 0)} cases")
        print(f"Success: {result.get('success', False)}")
        print("✅ Raw cases endpoint test passed")
    else:
        print(f"Error: {response.text}")
        print("❌ Raw cases endpoint test failed")

    print()


def test_download_endpoint():
    """Test the download endpoint."""
    print("Testing download endpoint...")

    # Use a known case URL from the cache
    download_data = {
        "case_urls": [
            "https://kenyalaw.org/caselaw/cases/view/194677/"
        ]
    }

    response = client.post("/api/v1/cases/download", json=download_data)
    print(f"Download Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Total cases: {result.get('total_cases', 0)}")
        print(f"Successful downloads: {result.get('successful_downloads', 0)}")
        print(f"Failed downloads: {result.get('failed_downloads', 0)}")
        print("✅ Download endpoint test passed")
    else:
        print(f"Error: {response.text}")
        print("❌ Download endpoint test failed")

    print()


def test_case_metadata_endpoint():
    """Test the case metadata endpoint."""
    print("Testing case metadata endpoint...")

    response = client.get("/api/v1/cases/raw/194677")
    print(f"Case Metadata Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Case ID: {result.get('case_id', 'Unknown')}")
        print(f"Title: {result.get('title', 'Unknown')}")
        print("✅ Case metadata endpoint test passed")
    else:
        print(f"Error: {response.text}")
        print("❌ Case metadata endpoint test failed")

    print()


def main():
    """Run all API tests."""
    print("🚀 Starting FastAPI Endpoint Tests")
    print("=" * 50)

    try:
        test_health_endpoint()
        test_root_endpoint()
        test_search_endpoint()
        test_search_get_endpoint()
        test_raw_cases_endpoint()
        test_download_endpoint()
        test_case_metadata_endpoint()

        print("🎉 All API tests completed!")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()