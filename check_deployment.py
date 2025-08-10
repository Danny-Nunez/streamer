#!/usr/bin/env python3

"""
Check what's currently deployed on the server
"""

import requests
import time

def check_deployment():
    server_url = "https://youtube-stream-api-fst0.onrender.com"
    
    print("Checking Current Deployment")
    print("=" * 40)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{server_url}/", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Health endpoint
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{server_url}/api/health", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Test endpoint (only in safe version)
    print("\n3. Testing /api/test endpoint...")
    try:
        response = requests.get(f"{server_url}/api/test", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            print("✅ This indicates the safe version is deployed!")
        else:
            print(f"Error: {response.text}")
            print("❌ This indicates an older version is deployed")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Stream info endpoint
    print("\n4. Testing stream info endpoint...")
    try:
        response = requests.get(f"{server_url}/api/stream/dQw4w9WgXcQ", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            if data.get('status') == 'success':
                stream_data = data.get('data', {})
                print(f"Title: {stream_data.get('title')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Proxy endpoint
    print("\n5. Testing proxy endpoint...")
    try:
        response = requests.get(f"{server_url}/api/stream/dQw4w9WgXcQ/proxy", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 206]:
            print("✅ Proxy endpoint is working!")
            print(f"Content-Type: {response.headers.get('content-type')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Checking what version is currently deployed...")
    print("This will help identify if the deployment updated properly.")
    print()
    
    check_deployment()
    
    print("\n" + "=" * 40)
    print("If /api/test returns 200, the safe version is deployed.")
    print("If /api/test returns 404, an older version is still running.")
    print("The deployment may still be in progress - wait a few minutes and try again.") 