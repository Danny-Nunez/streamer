#!/usr/bin/env python3

"""
YouTube Audio Stream Extractor
This script extracts audio stream URLs from YouTube videos for web streaming.
Returns audio stream information including URL, format, and quality.
"""

import sys
import pytubefix
from typing import Dict, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import subprocess
import json
import os
import time
from config import (
    PROXY_URL, 
    SERVER_ENV, 
    mark_proxy_failed, 
    get_proxy_url, 
    VIDEO_STREAM_SETTINGS,
    YOUTUBE_CLIENT,
    PROXY_USERNAME,
    PROXY_PASSWORD,
    PROXY_HOST
)
import urllib.parse
import requests
from pathlib import Path

@dataclass
class AudioStream:
    url: str
    format: str
    bitrate: str
    mime_type: str
    filesize: int
    title: str
    author: str
    length: int

def cmd(command: str, check: bool = True, shell: bool = True, capture_output: bool = True, text: bool = True, env: dict = None):
    """
    Runs a command in a shell, and throws an exception if the return code is non-zero.
    """
    print(f"Running command: {command}")
    try:
        return subprocess.run(command, check=check, shell=shell, capture_output=capture_output, text=text, env=env)
    except subprocess.CalledProcessError as error:
        print(f"Command failed with exit code: {error.returncode}")
        print(f"stdout: {error.stdout}")
        print(f"stderr: {error.stderr}")
        raise

def generate_youtube_token() -> dict:
    """Generate YouTube token using youtube-po-token-generator"""
    print("Generating YouTube token")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, 'scripts', 'test_token.js')
    
    # Ensure we're in the correct directory
    os.chdir(current_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Use absolute path for node_modules
    node_modules_path = os.path.join(current_dir, 'node_modules')
    env = os.environ.copy()
    env['NODE_PATH'] = node_modules_path
    env['HOME'] = current_dir  # Set HOME to current directory for npm
    
    # Set proxy if configured
    if SERVER_ENV and PROXY_URL:
        env['HTTPS_PROXY'] = PROXY_URL
        env['HTTP_PROXY'] = PROXY_URL
        print(f"Using proxy: {PROXY_URL}")
    
    try:
        # Only install if node_modules doesn't exist
        if not os.path.exists(node_modules_path):
            print("Installing youtube-po-token-generator...")
            cmd(f"npm install youtube-po-token-generator --prefix {current_dir}", env=env)
        
        # Run the token generator script
        print("Running token generator script...")
        result = cmd(f"node {script_path}", env=env)
        
        if result.returncode != 0:
            raise Exception(f"Token generation failed with exit code {result.returncode}")
        
        # Parse the token data from stdout
        try:
            output = result.stdout.strip()
            if not output:
                raise Exception("No output received from token generator")
                
            token_data = json.loads(output)
            print(f"Token generation result: {token_data}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse token data: {e}")
            print(f"Raw output: {result.stdout}")
            raise Exception("Invalid token data format")
        
        if 'visitorData' not in token_data or 'poToken' not in token_data:
            raise Exception("Invalid token data format")
            
        # Save token to file for caching
        token_path = os.path.join(current_dir, 'token.json')
        with open(token_path, 'w') as f:
            json.dump({
                **token_data,
                'timestamp': int(time.time() * 1000)
            }, f)
            
        return token_data
    except Exception as e:
        print(f"Error generating token: {e}")
        raise

def po_token_verifier() -> Tuple[str, str]:
    """Get visitor data and PoToken for YouTube"""
    try:
        # Try to load saved token first
        current_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(current_dir, 'token.json')
        if os.path.exists(token_path):
            with open(token_path, 'r') as f:
                token_data = json.load(f)
                # Check if token is less than 1 hour old
                if time.time() * 1000 - token_data['timestamp'] < 3600000:
                    print("Using saved token data")
                    return token_data['visitorData'], token_data['poToken']
        
        # If no valid saved token, generate a new one
        print("Generating new token")
        token_object = generate_youtube_token()
        return token_object['visitorData'], token_object['poToken']
    except Exception as e:
        print(f"Error in po_token_verifier: {e}")
        raise

def cleanup_old_files(audio_dir: Path, max_age_hours: int = 1):
    """Remove audio files older than max_age_hours"""
    try:
        current_time = time.time()
        for file in audio_dir.glob('audio_*.mp3'):
            file_age = current_time - file.stat().st_mtime
            if file_age > (max_age_hours * 3600):
                file.unlink()
                print(f"Cleaned up old file: {file}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def download_audio(url: str, proxy_info: dict = None) -> str:
    """Download audio file and return the local path"""
    try:
        # Create audios directory if it doesn't exist
        audio_dir = Path('audios')
        audio_dir.mkdir(exist_ok=True)
        
        # Clean up old files before downloading new ones
        cleanup_old_files(audio_dir)
        
        # Generate unique filename
        timestamp = int(time.time())
        filename = f"audio_{timestamp}.mp3"
        filepath = audio_dir / filename
        
        # Set up proxy if provided
        proxies = None
        if proxy_info:
            proxy_url = f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
        
        # Create a YouTube object with the URL
        yt = pytubefix.YouTube(
            url,
            proxies=proxies,
            use_oauth=False,
            allow_oauth_cache=True
        )
        
        # Get the audio stream
        stream = yt.streams.filter(only_audio=True).first()
        if not stream:
            raise Exception("No audio stream found")
        
        # Download the file
        print(f"Downloading audio to {filepath}...")
        stream.download(output_path=str(audio_dir), filename=filename)
        
        return str(filepath)
    except Exception as e:
        print(f"Error downloading audio: {e}")
        raise

class YouTubeAudioExtractor:
    def __init__(self):
        self.node_installed = self._check_node_installed()
        self._token_cache = {}
        self._token_cache_time = 0
        self._token_cache_duration = 3600  # 1 hour in seconds
        self._downloaded_files = set()  # Track downloaded files

    def _check_node_installed(self):
        """Check if Node.js is installed"""
        try:
            cmd('node --version')
            return True
        except Exception as e:
            print(f"Node.js check failed: {e}")
            return False

    def _get_video_id(self, url):
        """Extract video ID from URL"""
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:shorts\/)([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_audio_stream(self, youtube_url: str, preferred_format: str = None) -> Union[Dict, None]:
        """
        Get audio stream information from a YouTube URL.
        
        Args:
            youtube_url (str): YouTube video URL
            preferred_format (str, optional): Preferred audio format (e.g., 'mp4', 'webm')
        
        Returns:
            dict: Dictionary containing stream information or None if no stream found
            {
                'status': 'success' or 'error',
                'message': Error message if status is 'error',
                'stream': AudioStream object if status is 'success'
            }
        """
        try:
            # Get video ID
            video_id = self._get_video_id(youtube_url)
            if not video_id:
                return {
                    'status': 'error',
                    'message': 'Invalid YouTube URL',
                    'stream': None
                }

            print(f"Processing video ID: {video_id}")
            
            # Set up proxy configuration
            proxies = None
            if SERVER_ENV and PROXY_URL:
                proxies = {
                    'http': PROXY_URL,
                    'https': PROXY_URL
                }
                print(f"Using proxies: {proxies}")
            else:
                print("No proxy configuration found, proceeding without proxy")
            
            # Get visitor data and poToken
            visitor_data, po_token = po_token_verifier()
            
            # Try up to 3 different proxies if needed
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Create YouTube object with ANDROID client
                    yt = pytubefix.YouTube(
                        youtube_url,
                        client='ANDROID',  # Use ANDROID client which is more reliable
                        use_oauth=False,
                        allow_oauth_cache=True,
                        proxies=proxies if proxies else None,
                        use_po_token=False,  # Disable po_token for ANDROID client
                        on_progress_callback=None  # Disable progress callback for faster processing
                    )
                    
                    # Get audio streams
                    print("Getting audio streams...")
                    streams = yt.streams.filter(only_audio=True)
                    if not streams:
                        raise Exception("No audio streams found")
                    
                    # Select the best quality stream for mobile
                    # Prioritize smaller file sizes and mobile-friendly formats
                    stream = None
                    if preferred_format:
                        stream = streams.filter(mime_type=f"audio/{preferred_format}").first()
                    
                    if not stream:
                        # Try to get the smallest file size that's still good quality
                        streams = sorted(streams, key=lambda x: x.filesize)
                        for s in streams:
                            if s.bitrate >= 128000:  # Minimum 128kbps for acceptable quality
                                stream = s
                                break
                    
                    if not stream:
                        stream = streams.first()
                    
                    if not stream:
                        raise Exception("No suitable audio stream found")
                    
                    # Create AudioStream object
                    stream_info = AudioStream(
                        url=stream.url,
                        format=stream.mime_type.split('/')[1],
                        bitrate=f"{stream.bitrate // 1000}kbps",
                        mime_type=stream.mime_type,
                        filesize=stream.filesize,
                        title=yt.title,
                        author=yt.author,
                        length=yt.length
                    )
                    
                    # Add necessary parameters to the URL
                    if '?' in stream_info.url:
                        stream_info.url += '&'
                    else:
                        stream_info.url += '?'
                    
                    # Add required parameters for video access
                    params = VIDEO_STREAM_SETTINGS.copy()
                    
                    # Add additional required parameters
                    params.update({
                        'ei': 'w6jlZ6GYCcKf4dUPk5X6kAc',  # Example from working URL
                        'met': str(int(time.time())),
                        'bui': 'AccgBcNca_Jhp4k784mlbZh4m1856WjMR8k251ssBES40_1E02ld97SAoQ5kmt3gzk6-OlNXPHt3u26V',
                        'spc': '_S3wKp5K7XuiCZ0Vn9Q4nDrCbQeScVBRxnNqrCYiOgHlyKSPKqzQdJIct2m9WCza',
                        'clen': str(stream.filesize),
                        'dur': str(stream_info.length),
                        'lmt': str(int(time.time() * 1000)),
                        'mt': str(int(time.time())),
                        'fvip': '5',
                        'keepalive': 'yes'
                    })
                    
                    # Remove IP-related parameters that could cause playback issues
                    params.pop('ip', None)
                    params.pop('ipbits', None)
                    
                    # Build URL with parameters
                    stream_info.url += '&'.join(f"{k}={v}" for k, v in params.items())
                    
                    # Create player URL with stream data and proxy information
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    proxy_info = {
                        'username': PROXY_USERNAME,
                        'password': PROXY_PASSWORD,
                        'host': PROXY_HOST,
                        'port': PROXY_URL.split(':')[-1]
                    } if SERVER_ENV and PROXY_URL else None
                    
                    # Download the audio file
                    try:
                        local_path = download_audio(youtube_url, proxy_info)
                        print(f"Audio downloaded to: {local_path}")
                        self._downloaded_files.add(local_path)  # Track the new file
                    except Exception as e:
                        print(f"Failed to download audio: {e}")
                        local_path = None
                    
                    player_data = {
                        'url': stream_info.url,
                        'local_path': local_path,
                        'title': stream_info.title,
                        'author': stream_info.author,
                        'format': stream_info.format,
                        'bitrate': stream_info.bitrate,
                        'mime_type': stream_info.mime_type,
                        'proxy': proxy_info
                    }
                    
                    player_url = f"file://{os.path.join(current_dir, 'player.html')}?data=" + urllib.parse.quote(json.dumps(player_data))
                    
                    return {
                        'status': 'success',
                        'message': 'Audio stream found',
                        'stream': stream_info,
                        'player_url': player_url,
                        'proxy_info': proxy_info,
                        'local_path': local_path
                    }
                    
                except Exception as e:
                    if SERVER_ENV and PROXY_URL:
                        # Mark current proxy as failed
                        mark_proxy_failed(PROXY_URL)
                        
                        # Get new proxy if not last attempt
                        if attempt < max_retries - 1:
                            new_proxy = get_proxy_url()
                            proxies = {
                                'http': new_proxy,
                                'https': new_proxy
                            }
                            print(f"Retrying with new proxy: {new_proxy}")
                            continue
                    
                    # If all retries failed or no proxy, raise the error
                    print(f"Error in get_audio_stream: {str(e)}")
                    return {
                        'status': 'error',
                        'message': str(e),
                        'stream': None
                    }

        except Exception as e:
            print(f"Error in get_audio_stream: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'stream': None
            }

def main():
    # Example usage
    if len(sys.argv) != 2:
        print("Error: Please provide a YouTube URL as argument")
        print("Usage: python youtube_stream.py <youtube_url>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    extractor = YouTubeAudioExtractor()
    
    # Get stream info
    result = extractor.get_audio_stream(youtube_url)
    
    if result['status'] == 'success':
        stream = result['stream']
        print("\nStream Information:")
        print(f"Title: {stream.title}")
        print(f"Author: {stream.author}")
        print(f"Format: {stream.format}")
        print(f"Bitrate: {stream.bitrate}")
        print(f"MIME Type: {stream.mime_type}")
        print(f"File Size: {stream.filesize / 1024 / 1024:.2f} MB")
        print(f"Length: {stream.length} seconds")
        print(f"\nStream URL: {stream.url}")
        print(f"\nPlayer URL: {result['player_url']}")
        if result['proxy_info']:
            print("\nProxy Information:")
            print(f"Username: {result['proxy_info']['username']}")
            print(f"Password: {result['proxy_info']['password']}")
            print(f"Host: {result['proxy_info']['host']}")
            print(f"Port: {result['proxy_info']['port']}")
    else:
        print(f"Error: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
