"""
Configuration settings for the YouTube stream extractor
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file if it exists
env_path = Path('.env')
if env_path.exists():
    load_dotenv()

# Proxy settings (all optional)
PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')
PROXY_HOST = os.getenv('PROXY_HOST')
PROXY_PORT = os.getenv('PROXY_PORT')

# Construct proxy URLs only if all credentials are provided and non-empty
PROXY_URL = None
if all([PROXY_USERNAME, PROXY_PASSWORD, PROXY_HOST, PROXY_PORT]):
    PROXY_URL = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"

# Environment settings
SERVER_ENV = os.getenv('SERVER_ENV', 'false').lower() == 'true'

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
    'Upgrade-Insecure-Requests': '1'
} 