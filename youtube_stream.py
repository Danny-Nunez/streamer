#!/usr/bin/env python3

"""
YouTube Audio Stream Extractor
This script extracts audio stream URLs from YouTube videos for web streaming.
Returns audio stream information including URL, format, and quality.
"""

import sys
import pytubefix
from typing import Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime

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

class YouTubeAudioExtractor:
    def __init__(self):
        self.node_installed = self._check_node_installed()

    def _check_node_installed(self):
        """Check if Node.js is installed"""
        try:
            import subprocess
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            # Install dependencies if node is installed
            subprocess.run(['npm', 'install'], capture_output=True, check=True)
            return True
        except:
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

    def _get_po_token(self, video_id):
        """Get PO token using Node.js helper"""
        if not self.node_installed:
            return None
        
        try:
            import subprocess
            import json
            
            result = subprocess.run(
                ['node', 'po_token_helper.js', video_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            try:
                response = json.loads(result.stdout)
                return response.get('token')
            except:
                return None
        except:
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
            # Get video ID and PO token
            video_id = self._get_video_id(youtube_url)
            if not video_id:
                return {
                    'status': 'error',
                    'message': 'Invalid YouTube URL',
                    'stream': None
                }

            # Create a YouTube object with WEB client
            yt = pytubefix.YouTube(youtube_url, use_oauth=False, allow_oauth_cache=True)
            yt.use_oauth = False  # Ensure OAuth is disabled
            
            # Set client to WEB
            yt.client = 'WEB'
            
            # Get all audio streams
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
