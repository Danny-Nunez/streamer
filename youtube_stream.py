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
        pass

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
            # Create a YouTube object
            yt = pytubefix.YouTube(youtube_url)
            
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
