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
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'youtube-token-generator.js')
    # Use absolute path for node_modules
    node_modules_path = os.path.join(os.path.dirname(__file__), 'node_modules')
    env = os.environ.copy()
    env['NODE_PATH'] = node_modules_path
    env['HOME'] = '/app'  # Set HOME to /app for npm
    try:
        result = cmd(f"node {script_path}", env=env)
        data = json.loads(result.stdout)
        print(f"Token generation result: {data}")
        if 'error' in data:
            raise Exception(f"Token generation failed: {data['error']}")
        if 'visitorData' not in data or 'poToken' not in data:
            raise Exception("Invalid token data format")
        return data
    except Exception as e:
        print(f"Error generating token: {e}")
        raise

def po_token_verifier() -> Tuple[str, str]:
    """Get visitor data and PoToken for YouTube"""
    try:
        token_object = generate_youtube_token()
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
                cmd('npm install --prefix /app')
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
            
            # Create a YouTube object with WEB client and PoToken
            yt = pytubefix.YouTube(
                youtube_url,
                use_oauth=False,
                allow_oauth_cache=True,
                use_po_token=True,
                po_token_verifier=po_token_verifier
            )
            yt.use_oauth = False  # Ensure OAuth is disabled
            
            # Set client to WEB
            yt.client = 'WEB'
            
            try:
                # Get all audio streams
                audio_streams = yt.streams.filter(only_audio=True)
            except Exception as e:
                print(f"Error getting audio streams: {e}")
                # Try without PoToken if it fails
                yt = pytubefix.YouTube(youtube_url, use_oauth=False, allow_oauth_cache=True)
                yt.client = 'WEB'
                audio_streams = yt.streams.filter(only_audio=True)
            
            if not audio_streams:
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
                    selected_stream = max(format_streams, key=lambda s: int(s.abr[:-4]))
            
            if not selected_stream:
                # Get highest quality stream regardless of format
                selected_stream = max(audio_streams, key=lambda s: int(s.abr[:-4]))
            
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
                bitrate=selected_stream.abr,
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
