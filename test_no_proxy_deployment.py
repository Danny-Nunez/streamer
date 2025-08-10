#!/usr/bin/env python3

"""
Test the no-proxy deployment
"""

import requests
import time

def test_no_proxy_deployment():
    server_url = "https://youtube-stream-api-fst0.onrender.com"
    
    print("Testing No-Proxy Deployment")
    print("=" * 40)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{server_url}/", timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint: {response.status_code} (took {end_time - start_time:.2f}s)")
            print(f"Response: {data}")
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Root endpoint error: {e}")
        return False
    
    # Test 2: Health endpoint
    print("\n2. Testing health endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{server_url}/api/health", timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health endpoint: {response.status_code} (took {end_time - start_time:.2f}s)")
            print(f"Response: {data}")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health endpoint error: {e}")
        return False
    
    # Test 3: Stream info endpoint
    print("\n3. Testing stream info endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{server_url}/api/stream/dQw4w9WgXcQ", timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Stream info: {response.status_code} (took {end_time - start_time:.2f}s)")
            print(f"Status: {data.get('status')}")
            if data.get('status') == 'success':
                stream_data = data.get('data', {})
                print(f"Title: {stream_data.get('title')}")
                print(f"Author: {stream_data.get('author')}")
                print(f"Format: {stream_data.get('format')}")
                print(f"Duration: {stream_data.get('length')} seconds")
                return True
            else:
                print(f"✗ Stream info failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"✗ Stream info failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ Stream info error: {e}")
        return False

if __name__ == "__main__":
    print("Waiting for deployment to complete...")
    print("This may take 2-5 minutes after pushing to git.")
    print("If you get timeout errors, wait a few minutes and try again.")
    print()
    
    success = test_no_proxy_deployment()
    
    if success:
        print("\n🎉 No-proxy deployment is working!")
        print("\nYou can now test the audio streaming:")
        print("1. Get stream info: GET /api/stream/VIDEO_ID")
        print("2. Stream audio: GET /api/stream/VIDEO_ID/proxy")
        print("\nExample:")
        print(f"https://youtube-stream-api-fst0.onrender.com/api/stream/dQw4w9WgXcQ/proxy")
    else:
        print("\n❌ Deployment test failed.")
        print("Please check the Render dashboard for deployment status.")
        print("The deployment may still be in progress - wait a few minutes and try again.") 