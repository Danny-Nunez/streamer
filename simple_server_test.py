#!/usr/bin/env python3

"""
Simple test to check server functionality
"""

import requests
import time

def test_server_endpoints():
    server_url = "https://youtube-stream-api-fst0.onrender.com"
    
    print("Testing server endpoints...")
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{server_url}/", timeout=10)
        end_time = time.time()
        print(f"✓ Root endpoint: {response.status_code} (took {end_time - start_time:.2f}s)")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
    
    # Test 2: Health endpoint
    print("\n2. Testing health endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{server_url}/api/health", timeout=10)
        end_time = time.time()
        print(f"✓ Health endpoint: {response.status_code} (took {end_time - start_time:.2f}s)")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
    
    # Test 3: Stream endpoint with timeout
    print("\n3. Testing stream endpoint (with 30s timeout)...")
    try:
        start_time = time.time()
        response = requests.get(f"{server_url}/api/stream/dQw4w9WgXcQ", timeout=30)
        end_time = time.time()
        print(f"✓ Stream endpoint: {response.status_code} (took {end_time - start_time:.2f}s)")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            if data.get('status') == 'success':
                stream_data = data.get('data', {})
                print(f"Title: {stream_data.get('title')}")
                print(f"Format: {stream_data.get('format')}")
    except requests.exceptions.Timeout:
        print("✗ Stream endpoint timed out after 30 seconds")
    except Exception as e:
        print(f"✗ Stream endpoint failed: {e}")

if __name__ == "__main__":
    test_server_endpoints() 