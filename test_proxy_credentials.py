#!/usr/bin/env python3

"""
Test SmartProxy credentials
"""

import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def test_proxy_credentials():
    """Test SmartProxy credentials with various endpoints"""
    
    # Get proxy settings
    proxy_host = os.getenv('PROXY_HOST', 'gate.smartproxy.com')
    proxy_username = os.getenv('PROXY_USERNAME', 'spj8zjg34x')
    proxy_password = os.getenv('PROXY_PASSWORD', 'pyYgPna58y+B80yjHk')
    
    print(f"Testing SmartProxy credentials:")
    print(f"Host: {proxy_host}")
    print(f"Username: {proxy_username}")
    print(f"Password: {'*' * len(proxy_password)}")
    print()
    
    # Configure proxy URL
    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:10001"
    
    # Test different ports
    ports = [10001, 10002, 10003, 10004, 10005]
    
    for port in ports:
        print(f"Testing port {port}...")
        proxy_url_port = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{port}"
        
        try:
            # Configure session with proxy
            session = requests.Session()
            session.proxies = {
                'http': proxy_url_port,
                'https': proxy_url_port
            }
            
            # Test with a simple HTTP request
            start_time = time.time()
            response = session.get(
                'http://httpbin.org/ip',
                timeout=10,
                verify=False
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Port {port} - Success! Response time: {end_time - start_time:.2f}s")
                print(f"  IP: {data.get('origin', 'Unknown')}")
                
                # Test HTTPS
                try:
                    start_time = time.time()
                    response = session.get(
                        'https://httpbin.org/ip',
                        timeout=10,
                        verify=False
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  HTTPS: ✓ Working (Response time: {end_time - start_time:.2f}s)")
                        print(f"  HTTPS IP: {data.get('origin', 'Unknown')}")
                    else:
                        print(f"  HTTPS: ✗ Failed (Status: {response.status_code})")
                        
                except Exception as e:
                    print(f"  HTTPS: ✗ Failed - {str(e)}")
                    
            else:
                print(f"✗ Port {port} - Failed (Status: {response.status_code})")
                
        except requests.exceptions.ProxyError as e:
            print(f"✗ Port {port} - Proxy Error: {str(e)}")
        except requests.exceptions.ConnectTimeout:
            print(f"✗ Port {port} - Connection Timeout")
        except requests.exceptions.ReadTimeout:
            print(f"✗ Port {port} - Read Timeout")
        except Exception as e:
            print(f"✗ Port {port} - Error: {str(e)}")
        
        print()
    
    # Test YouTube access
    print("Testing YouTube access...")
    try:
        session = requests.Session()
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        # Test with YouTube homepage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        start_time = time.time()
        response = session.get(
            'https://www.youtube.com',
            headers=headers,
            timeout=15,
            verify=False
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✓ YouTube access - Success! Response time: {end_time - start_time:.2f}s")
            print(f"  Content length: {len(response.text)} characters")
        else:
            print(f"✗ YouTube access - Failed (Status: {response.status_code})")
            
    except Exception as e:
        print(f"✗ YouTube access - Error: {str(e)}")

def test_specific_proxy_url():
    """Test the specific proxy URL format used in the server"""
    
    proxy_host = os.getenv('PROXY_HOST', 'gate.smartproxy.com')
    proxy_username = os.getenv('PROXY_USERNAME', 'spj8zjg34x')
    proxy_password = os.getenv('PROXY_PASSWORD', 'pyYgPna58y+B80yjHk')
    
    print(f"\nTesting specific proxy URL format...")
    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:10001"
    print(f"Proxy URL: {proxy_url}")
    
    try:
        session = requests.Session()
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        # Test with a simple request
        response = session.get('http://httpbin.org/ip', timeout=10, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Proxy URL test - Success!")
            print(f"  IP: {data.get('origin', 'Unknown')}")
            return True
        else:
            print(f"✗ Proxy URL test - Failed (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"✗ Proxy URL test - Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("SmartProxy Credentials Test")
    print("=" * 40)
    
    # Test basic proxy functionality
    test_proxy_credentials()
    
    # Test specific URL format
    success = test_specific_proxy_url()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ Proxy credentials appear to be working!")
        print("You can proceed with deploying the proxy server.")
    else:
        print("✗ Proxy credentials test failed.")
        print("Please check your credentials and try again.") 