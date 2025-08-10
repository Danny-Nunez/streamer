#!/usr/bin/env python3

"""
Test script for deployed YouTube Audio Stream API
This script tests the deployed server without using local proxy settings.
"""

import sys
import pytubefix
import requests
import json

def test_deployed_server(youtube_url: str, server_url: str = "https://youtube-stream-api-fst0.onrender.com"):
    """
    Test the deployed server by getting a stream URL and testing the proxy endpoint.
    """
    try:
        print(f"Testing deployed server: {server_url}")
        print(f"YouTube URL: {youtube_url}")
        
        # First, get the stream URL locally (without proxy)
        print("\n1. Getting stream URL locally...")
        
        # Temporarily remove proxy environment variables
        original_http_proxy = os.environ.get('HTTP_PROXY')
        original_https_proxy = os.environ.get('HTTPS_PROXY')
        
        if 'HTTP_PROXY' in os.environ:
            del os.environ['HTTP_PROXY']
        if 'HTTPS_PROXY' in os.environ:
            del os.environ['HTTPS_PROXY']
        
        try:
            # Create YouTube object without proxy
            yt = pytubefix.YouTube(youtube_url)
            
            # Get audio streams
            streams = yt.streams.filter(only_audio=True)
            if not streams:
                raise Exception("No audio streams found")
            
            # Select the best quality stream
            stream = None
            streams = sorted(streams, key=lambda x: x.filesize)
            for s in streams:
                if s.bitrate >= 128000:  # Minimum 128kbps
                    stream = s
                    break
            
            if not stream:
                stream = streams[0]
            
            stream_url = stream.url
            print(f"✓ Got stream URL: {stream_url[:100]}...")
            
        finally:
            # Restore proxy environment variables
            if original_http_proxy:
                os.environ['HTTP_PROXY'] = original_http_proxy
            if original_https_proxy:
                os.environ['HTTPS_PROXY'] = original_https_proxy
        
        # Test the deployed server
        print("\n2. Testing deployed server proxy endpoint...")
        
        proxy_url = f"{server_url}/proxy?url={requests.utils.quote(stream_url)}"
        print(f"Proxy URL: {proxy_url[:100]}...")
        
        # Make a HEAD request to test the proxy
        response = requests.head(proxy_url, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code in [200, 206]:
            print("✓ Proxy server is working!")
            
            # Test with a small range request
            headers = {'Range': 'bytes=0-1023'}
            response = requests.get(proxy_url, headers=headers, timeout=30, stream=True)
            print(f"Range request status: {response.status_code}")
            
            if response.status_code in [200, 206]:
                print("✓ Range requests are working!")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print(f"Content-Length: {response.headers.get('content-length')}")
                return True
            else:
                print(f"✗ Range request failed: {response.status_code}")
                return False
        else:
            print(f"✗ Proxy server failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_deployed_server.py <youtube_url>")
        print("Example: python test_deployed_server.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    server_url = "https://youtube-stream-api-fst0.onrender.com"
    
    success = test_deployed_server(youtube_url, server_url)
    
    if success:
        print("\n🎉 Test completed successfully!")
        print(f"Your server at {server_url} is working correctly.")
        print("\nYou can now use the web interface to stream audio:")
        print(f"1. Open {server_url} in your browser")
        print("2. Paste a stream URL from youtube_stream_local_test.py")
        print("3. Click Play to start streaming")
    else:
        print("\n❌ Test failed. Check the server logs for more details.")

if __name__ == "__main__":
    import os
    main() 