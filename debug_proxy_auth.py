#!/usr/bin/env python3

"""
Debug SmartProxy authentication issues
"""

import requests
import os
from dotenv import load_dotenv
import urllib.parse
import base64

# Load environment variables
load_dotenv()

def test_proxy_auth_methods():
    """Test different proxy authentication methods"""
    
    proxy_host = os.getenv('PROXY_HOST', 'gate.smartproxy.com')
    proxy_username = os.getenv('PROXY_USERNAME', 'spj8zjg34x')
    proxy_password = os.getenv('PROXY_PASSWORD', 'pyYgPna58y+B80yjHk')
    
    print(f"Debugging SmartProxy authentication:")
    print(f"Host: {proxy_host}")
    print(f"Username: {proxy_username}")
    print(f"Password: {proxy_password}")
    print(f"Password length: {len(proxy_password)}")
    print(f"Password contains special chars: {any(c in proxy_password for c in '+/=')}")
    print()
    
    # Test different authentication methods
    methods = [
        {
            'name': 'URL-encoded password',
            'url': f"http://{proxy_username}:{urllib.parse.quote(proxy_password)}@{proxy_host}:10001"
        },
        {
            'name': 'Raw password',
            'url': f"http://{proxy_username}:{proxy_password}@{proxy_host}:10001"
        },
        {
            'name': 'Base64 encoded auth',
            'url': f"http://{proxy_host}:10001",
            'headers': {
                'Proxy-Authorization': f"Basic {base64.b64encode(f'{proxy_username}:{proxy_password}'.encode()).decode()}"
            }
        }
    ]
    
    for method in methods:
        print(f"Testing: {method['name']}")
        print(f"URL: {method['url']}")
        
        try:
            session = requests.Session()
            
            if 'headers' in method:
                # Use headers for authentication
                session.proxies = {
                    'http': method['url'],
                    'https': method['url']
                }
                session.headers.update(method['headers'])
            else:
                # Use URL for authentication
                session.proxies = {
                    'http': method['url'],
                    'https': method['url']
                }
            
            response = session.get(
                'http://httpbin.org/ip',
                timeout=10,
                verify=False
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Success! IP: {data.get('origin', 'Unknown')}")
                return True
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.ProxyError as e:
            print(f"✗ Proxy Error: {str(e)}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        print()

def test_credentials_format():
    """Test if credentials format is correct"""
    
    proxy_host = os.getenv('PROXY_HOST', 'gate.smartproxy.com')
    proxy_username = os.getenv('PROXY_USERNAME', 'spj8zjg34x')
    proxy_password = os.getenv('PROXY_PASSWORD', 'pyYgPna58y+B80yjHk')
    
    print("Testing credentials format...")
    
    # Check if credentials match expected format
    print(f"Username format check:")
    print(f"  Length: {len(proxy_username)}")
    print(f"  Alphanumeric: {proxy_username.isalnum()}")
    print(f"  Contains special chars: {any(c in proxy_username for c in '!@#$%^&*()_+-=[]{}|;:,.<>?')}")
    
    print(f"\nPassword format check:")
    print(f"  Length: {len(proxy_password)}")
    print(f"  Contains +: {'+' in proxy_password}")
    print(f"  Contains /: {'/' in proxy_password}")
    print(f"  Contains =: {'=' in proxy_password}")
    
    # URL encode the password to handle special characters
    encoded_password = urllib.parse.quote(proxy_password)
    print(f"\nURL encoded password: {encoded_password}")
    
    # Test with encoded password
    proxy_url = f"http://{proxy_username}:{encoded_password}@{proxy_host}:10001"
    print(f"Encoded proxy URL: {proxy_url}")
    
    try:
        session = requests.Session()
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        response = session.get('http://httpbin.org/ip', timeout=10, verify=False)
        print(f"Encoded URL test status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Encoded URL works! IP: {data.get('origin', 'Unknown')}")
            return True
        else:
            print(f"✗ Encoded URL failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Encoded URL error: {str(e)}")
        return False

if __name__ == "__main__":
    print("SmartProxy Authentication Debug")
    print("=" * 50)
    
    # Test credentials format
    format_success = test_credentials_format()
    
    print("\n" + "=" * 50)
    
    # Test different auth methods
    auth_success = test_proxy_auth_methods()
    
    print("\n" + "=" * 50)
    if format_success or auth_success:
        print("✓ Found working authentication method!")
    else:
        print("✗ All authentication methods failed.")
        print("\nPossible issues:")
        print("1. Credentials might be incorrect")
        print("2. Account might be suspended or expired")
        print("3. IP might be blocked")
        print("4. Proxy service might be down")
        print("\nPlease check your SmartProxy account status.") 