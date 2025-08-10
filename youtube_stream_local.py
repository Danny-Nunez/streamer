#!/usr/bin/env python3

"""
YouTube Audio Stream URL Extractor
This script extracts direct streaming URLs from YouTube videos.
"""

import sys
import pytubefix
from typing import Dict, Union
from dataclasses import dataclass
import urllib.request
import urllib.parse
import json

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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/',
            'Range': 'bytes=0-',
            'Connection': 'keep-alive',
        }

    def get_audio_stream(self, youtube_url: str) -> Union[Dict, None]:
        """
        Get audio stream information and streaming URL.
        """
        try:
            # Create YouTube object
            yt = pytubefix.YouTube(
                youtube_url,
                use_oauth=False,
                allow_oauth_cache=True
            )
            
            # Get audio streams
            print("Getting audio streams...")
            streams = yt.streams.filter(only_audio=True)
            if not streams:
                raise Exception("No audio streams found")
            
            # Select the best quality stream
            stream = None
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
            
            # Get the stream URL
            stream_url = stream.url
            
            # Create a request to get the final URL with headers
            request = urllib.request.Request(stream_url, headers=self.headers)
            try:
                response = urllib.request.urlopen(request, timeout=5)
                final_url = response.geturl()
                print("Stream URL verified successfully")
            except Exception as e:
                print(f"Warning: Could not verify stream URL: {e}")
                final_url = stream_url
            
            # Create AudioStream object
            stream_info = AudioStream(
                url=final_url,
                format=stream.mime_type.split('/')[1],
                bitrate=f"{stream.bitrate // 1000}kbps",
                mime_type=stream.mime_type,
                filesize=stream.filesize,
                title=yt.title,
                author=yt.author,
                length=yt.length
            )
            
            return {
                'status': 'success',
                'message': 'Stream URL generated successfully',
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
    if len(sys.argv) != 2:
        print("Error: Please provide a YouTube URL as argument")
        print("Usage: python youtube_stream_local.py <youtube_url>")
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
        
        print("\nStream URL (copy and paste into your browser):")
        print(f"{stream.url}")
        print("\nNote: If the URL doesn't work in your browser, try using VLC media player")
    else:
        print(f"Error: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 