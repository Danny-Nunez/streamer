"""
Configuration settings for the YouTube stream extractor
"""

import os
from dotenv import load_dotenv
from pathlib import Path
import random
import time

# Load environment variables from .env file if it exists
env_path = Path('.env')
if env_path.exists():
    load_dotenv()

# Proxy settings
PROXY_USERNAME = os.getenv('PROXY_USERNAME', 'spj8zjg34x')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD', 'pyYgPna58y+B80yjHk')
PROXY_HOST = os.getenv('PROXY_HOST', 'gate.smartproxy.com')

# List of available proxy ports
PROXY_PORTS = [10001, 10002, 10003, 10004, 10005, 10006, 10007]

# Track failed ports to avoid reusing them immediately
failed_ports = set()
last_proxy_reset = time.time()
PROXY_RESET_INTERVAL = 300  # Reset failed ports every 5 minutes

def get_proxy_url():
    """Get a working proxy URL with rotation and error handling"""
    global failed_ports, last_proxy_reset
    
    # Reset failed ports after interval
    if time.time() - last_proxy_reset > PROXY_RESET_INTERVAL:
        failed_ports.clear()
        last_proxy_reset = time.time()
    
    # Get available ports
    available_ports = [port for port in PROXY_PORTS if port not in failed_ports]
    
    # If all ports failed, reset and try again
    if not available_ports:
        failed_ports.clear()
        available_ports = PROXY_PORTS
    
    # Select random port from available ones
    port = random.choice(available_ports)
    
    return f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{port}"

def mark_proxy_failed(proxy_url):
    """Mark a proxy as failed to avoid reusing it immediately"""
    try:
        port = int(proxy_url.split(':')[-1])
        if port in PROXY_PORTS:
            failed_ports.add(port)
    except:
        pass

# Get initial proxy URL
PROXY_URL = get_proxy_url()

# Environment settings
SERVER_ENV = os.getenv('SERVER_ENV', 'true').lower() == 'true'

# YouTube settings
YOUTUBE_CLIENT = 'ANDROID'  # Use ANDROID client for better compatibility
YOUTUBE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
    'Upgrade-Insecure-Requests': '1',
    'X-YouTube-Client-Name': '1',
    'X-YouTube-Client-Version': '2.20240229.01.00',
    'X-YouTube-Device': 'android',
    'X-YouTube-Device-Make': 'Samsung',
    'X-YouTube-Device-Model': 'SM-S908B',
    'X-YouTube-Device-OS': 'Android',
    'X-YouTube-Device-OS-Version': '13'
} 