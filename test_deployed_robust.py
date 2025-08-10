#!/usr/bin/env python3

"""
Test the deployed robust server
"""

import requests
import time

def test_deployed_robust():
    server_url = "https://youtube-stream-api-fst0.onrender.com"
    
    print("Testing Deployed Robust Server")
    print("=" * 50)
    
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
    
    # Test 3: Stream info endpoint with timeout
    print("\n3. Testing stream info endpoint (with 60s timeout)...")
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
                
                # Test 4: Proxy endpoint with small range
                print("\n4. Testing proxy endpoint (small range request)...")
                try:
                    proxy_start = time.time()
                    proxy_response = requests.get(
                        f"{server_url}/api/stream/dQw4w9WgXcQ/proxy",
                        headers={'Range': 'bytes=0-1023'},
                        timeout=30,
                        stream=True
                    )
                    proxy_end = time.time()
                    
                    if proxy_response.status_code in [200, 206]:
                        print(f"✓ Proxy endpoint: {proxy_response.status_code} (took {proxy_end - proxy_start:.2f}s)")
                        print(f"Content-Type: {proxy_response.headers.get('content-type')}")
                        print(f"Content-Length: {proxy_response.headers.get('content-length')}")
                        print(f"Accept-Ranges: {proxy_response.headers.get('accept-ranges')}")
                        
                        # Read a small chunk to verify it's working
                        chunk = next(proxy_response.iter_content(chunk_size=1024), None)
                        if chunk:
                            print(f"✓ Received {len(chunk)} bytes of audio data")
                            return True
                        else:
                            print("✗ No audio data received")
                            return False
                    else:
                        print(f"✗ Proxy endpoint failed: {proxy_response.status_code}")
                        return False
                        
                except requests.exceptions.Timeout:
                    print("✗ Proxy endpoint timed out after 30 seconds")
                    return False
                except Exception as e:
                    print(f"✗ Proxy endpoint error: {e}")
                    return False
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
    except requests.exceptions.Timeout:
        print("✗ Stream info timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"✗ Stream info error: {e}")
        return False

if __name__ == "__main__":
    print("Testing deployed robust server...")
    print("This will help identify where the server is hanging.")
    print()
    
    success = test_deployed_robust()
    
    if success:
        print("\n🎉 Deployed server is working correctly!")
        print("\nYou can now use:")
        print("1. Stream info: GET /api/stream/VIDEO_ID")
        print("2. Audio stream: GET /api/stream/VIDEO_ID/proxy")
    else:
        print("\n❌ Deployed server has issues.")
        print("Check the Render dashboard for logs and deployment status.") 