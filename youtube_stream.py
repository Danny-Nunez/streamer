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
import random
import base64
from config import PROXY_URL, SERVER_ENV, YOUTUBE_CLIENT, YOUTUBE_HEADERS

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
    """Generate YouTube token using Node.js script"""
    print("Generating YouTube token")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, 'scripts', 'test_token.js')
    # Use absolute path for node_modules
    node_modules_path = os.path.join(current_dir, 'node_modules')
    env = os.environ.copy()
    env['NODE_PATH'] = node_modules_path
    env['HOME'] = current_dir  # Set HOME to current directory for npm
    try:
        result = cmd(f"node {script_path}", env=env)
        if result.returncode != 0:
            raise Exception(f"Token generation failed with exit code {result.returncode}")
        
        # Read the token from the saved file
        token_path = os.path.join(current_dir, 'token.json')
        with open(token_path, 'r') as f:
            data = json.load(f)
            print(f"Token generation result: {data}")
            if 'visitorData' not in data or 'poToken' not in data:
                raise Exception("Invalid token data format")
            return data
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
                    print(f"Visitor Data: {token_data['visitorData']}")
                    print(f"PoToken: {token_data['poToken']}")
                    return token_data['visitorData'], token_data['poToken']
        
        # If no valid saved token, generate a new one
        print("Generating new token")
        token_object = generate_youtube_token()
        print(f"Generated new token data:")
        print(f"Visitor Data: {token_object['visitorData']}")
        print(f"PoToken: {token_object['poToken']}")
        return token_object["visitorData"], token_object["poToken"]
    except Exception as e:
        print(f"Error in po_token_verifier: {e}")
        # Return a fallback token if generation fails
        timestamp = int(time.time() * 1000)
        random_value = random.randint(0, 1000000)
        visitor_data = base64.b64encode(f"{timestamp}.{random_value}".encode()).decode()
        return visitor_data, ""

class YouTubeAudioExtractor:
    def __init__(self):
        self.node_installed = self._check_node_installed()

    def _check_node_installed(self):
        """Check if Node.js is installed"""
        try:
            cmd('node --version')
            # Install dependencies if node is installed
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                cmd(f'npm install --prefix {current_dir}')
            except Exception as e:
                print(f"Warning: npm install failed: {e}")
                print("Continuing anyway as node_modules might already be installed")
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
            
            # Clear the token cache first
            cache_dir = os.path.expanduser('~/.cache/pytubefix')
            if os.path.exists(cache_dir):
                print(f"Clearing cache directory: {cache_dir}")
                import shutil
                shutil.rmtree(cache_dir)
            
            audio_streams = None
            yt = None
            
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
            
            # On server, always use ANDROID client
            if SERVER_ENV:
                try:
                    print("Server environment detected, using ANDROID client...")
                    yt = pytubefix.YouTube(
                        youtube_url,
                        use_oauth=False,
                        allow_oauth_cache=True,
                        proxies=proxies,
                        use_po_token=True  # Enable po_token usage
                    )
                    yt.client = YOUTUBE_CLIENT
                    yt.headers = {
                        **YOUTUBE_HEADERS,
                        'X-YouTube-Client-Name': '1',
                        'X-YouTube-Client-Version': '2.20240229.01.00',
                        'X-YouTube-Device': 'android',
                        'X-YouTube-Device-Make': 'Samsung',
                        'X-YouTube-Device-Model': 'SM-S908B',
                        'X-YouTube-Device-OS': 'Android',
                        'X-YouTube-Device-OS-Version': '13',
                        'X-YouTube-Identity-Token': po_token,
                        'X-YouTube-Visitor-Data': visitor_data
                    }
                    
                    print(f"Using client: {yt.client}")
                    print(f"Using headers: {yt.headers}")
                    audio_streams = yt.streams.filter(only_audio=True)
                    if audio_streams:
                        print(f"Found {len(audio_streams)} audio streams with ANDROID client")
                    else:
                        print("No audio streams found with ANDROID client")
                except Exception as e:
                    print(f"Error getting audio streams with ANDROID client: {e}")
                    return {
                        'status': 'error',
                        'message': str(e),
                        'stream': None
                    }
            else:
                # Local environment: try different clients
                client_types = ['ANDROID', 'IOS', 'WEB']
                for client_type in client_types:
                    try:
                        print(f"Attempting to get audio streams with {client_type} client...")
                        yt = pytubefix.YouTube(
                            youtube_url,
                            use_oauth=False,
                            allow_oauth_cache=True,
                            proxies=proxies if proxies else None,
                            use_po_token=True  # Enable po_token usage
                        )
                        yt.client = client_type
                        yt.headers = {
                            **YOUTUBE_HEADERS,
                            'X-YouTube-Client-Name': '1',
                            'X-YouTube-Client-Version': '2.20240229.01.00',
                            'X-YouTube-Device': 'android',
                            'X-YouTube-Device-Make': 'Samsung',
                            'X-YouTube-Device-Model': 'SM-S908B',
                            'X-YouTube-Device-OS': 'Android',
                            'X-YouTube-Device-OS-Version': '13',
                            'X-YouTube-Identity-Token': po_token,
                            'X-YouTube-Visitor-Data': visitor_data
                        }
                        
                        print(f"Using client: {yt.client}")
                        print(f"Using headers: {yt.headers}")
                        audio_streams = yt.streams.filter(only_audio=True)
                        if audio_streams:
                            print(f"Found {len(audio_streams)} audio streams with {client_type} client")
                            break
                        else:
                            print(f"No audio streams found with {client_type} client")
                    except Exception as e:
                        print(f"Error getting audio streams with {client_type} client: {e}")
                        continue
            
            if not audio_streams or not yt:
                return {
                    'status': 'error',
                    'message': 'No audio streams found',
                    'stream': None
                }

            # Select the best quality audio stream
            selected_stream = None
            
            if preferred_format:
                # Try to find stream with preferred format first
                format_streams = [s for s in audio_streams if s.subtype == preferred_format]
                if format_streams:
                    # Try to sort by bitrate if available
                    try:
                        selected_stream = max(format_streams, key=lambda s: int(s.abr[:-4]) if s.abr else 0)
                    except (AttributeError, ValueError):
                        selected_stream = format_streams[0]
            
            if not selected_stream:
                # Get highest quality stream regardless of format
                try:
                    selected_stream = max(audio_streams, key=lambda s: int(s.abr[:-4]) if s.abr else 0)
                except (AttributeError, ValueError):
                    selected_stream = audio_streams[0]
            
            if not selected_stream:
                return {
                    'status': 'error',
                    'message': 'Could not select appropriate audio stream',
                    'stream': None
                }

            # Create AudioStream object with stream information
            stream_info = AudioStream(
                url=selected_stream.url,
                format=selected_stream.subtype,
                bitrate=getattr(selected_stream, 'abr', 'unknown'),
                mime_type=selected_stream.mime_type,
                filesize=selected_stream.filesize,
                title=yt.title,
                author=yt.author,
                length=yt.length
            )

            return {
                'status': 'success',
                'message': 'Audio stream found',
                'stream': stream_info
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
    else:
        print(f"Error: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
