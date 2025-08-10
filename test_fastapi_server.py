#!/usr/bin/env python3

"""
Test script for deployed FastAPI YouTube Audio Stream API
This script tests the actual deployed server endpoints.
"""

import sys
import requests
import json

def test_fastapi_server(youtube_url: str, server_url: str = "https://youtube-stream-api-fst0.onrender.com"):
    """
    Test the deployed FastAPI server endpoints.
    """
    try:
        print(f"Testing deployed FastAPI server: {server_url}")
        print(f"YouTube URL: {youtube_url}")
        
        # Extract video ID from URL
        if "youtube.com" in youtube_url:
            if "v=" in youtube_url:
                video_id = youtube_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in youtube_url:
                video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
            else:
                raise ValueError("Could not extract video ID from URL")
        else:
            video_id = youtube_url  # Assume it's already a video ID
        
        print(f"Video ID: {video_id}")
        
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        health_url = f"{server_url}/api/health"
        response = requests.get(health_url, timeout=30)
        print(f"Health status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Get stream information
        print("\n2. Testing stream information endpoint...")
        stream_url = f"{server_url}/api/stream/{video_id}"
        response = requests.get(stream_url, timeout=60)
        print(f"Stream info status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Stream info endpoint working")
            data = response.json()
            print(f"Status: {data.get('status')}")
            if data.get('status') == 'success':
                stream_data = data.get('data', {})
                print(f"Title: {stream_data.get('title')}")
                print(f"Author: {stream_data.get('author')}")
                print(f"Format: {stream_data.get('format')}")
                print(f"Bitrate: {stream_data.get('bitrate')}")
                print(f"Duration: {stream_data.get('length')} seconds")
                print(f"Stream URL: {stream_data.get('url', '')[:100]}...")
                
                # Test 3: Test download endpoint
                print("\n3. Testing download endpoint...")
                download_url = f"{server_url}/api/stream/{video_id}/download"
                response = requests.head(download_url, timeout=30)
                print(f"Download status: {response.status_code}")
                
                if response.status_code in [200, 206]:
                    print("✓ Download endpoint working")
                    print(f"Content-Type: {response.headers.get('content-type')}")
                    print(f"Content-Length: {response.headers.get('content-length')}")
                    print(f"Accept-Ranges: {response.headers.get('accept-ranges')}")
                    return True
                else:
                    print(f"✗ Download endpoint failed: {response.status_code}")
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
                print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_fastapi_server.py <youtube_url>")
        print("Example: python test_fastapi_server.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    server_url = "https://youtube-stream-api-fst0.onrender.com"
    
    success = test_fastapi_server(youtube_url, server_url)
    
    if success:
        print("\n🎉 Test completed successfully!")
        print(f"Your FastAPI server at {server_url} is working correctly.")
        print("\nYou can now use the API endpoints:")
        print(f"1. GET {server_url}/api/stream/VIDEO_ID - Get stream information")
        print(f"2. GET {server_url}/api/stream/VIDEO_ID/download - Download audio")
        print(f"3. GET {server_url}/api/health - Health check")
    else:
        print("\n❌ Test failed. Check the server logs for more details.")

if __name__ == "__main__":
    main() 