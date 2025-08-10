#!/usr/bin/env python3

"""
YouTube Audio Stream URL Extractor - Local Test Version
This script extracts direct streaming URLs from YouTube videos for local testing.
Uses proxy settings from .env file.
"""

import sys
import pytubefix
from typing import Dict, Union
from dataclasses import dataclass
import urllib.request
import urllib.parse
import json
import traceback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
            'User-Agent': 'com.google.android.youtube/17.31.35 (Linux; U; Android 11)',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/',
            'Range': 'bytes=0-',
            'Connection': 'keep-alive',
        }
        
        # Get proxy settings from environment
        self.proxy_host = os.getenv('PROXY_HOST')
        self.proxy_username = os.getenv('PROXY_USERNAME')
        self.proxy_password = os.getenv('PROXY_PASSWORD')
        
        if not all([self.proxy_host, self.proxy_username, self.proxy_password]):
            raise ValueError("Missing proxy configuration in .env file")

    def get_audio_stream(self, youtube_url: str) -> Union[Dict, None]:
        """
        Get audio stream information and streaming URL.
        """
        try:
            print(f"Initializing YouTube object for URL: {youtube_url}")
            
            # Configure proxy settings
            proxy_url = f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_host}:10001"
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            
            # Create YouTube object with ANDROID client and proxy settings
            yt = pytubefix.YouTube(
                youtube_url,
                use_oauth=False,
                allow_oauth_cache=True,
                client='ANDROID',
                proxies={
                    'http': proxy_url,
                    'https': proxy_url
                }
            )
            
            # Get audio streams
            print("Getting audio streams...")
            streams = yt.streams.filter(only_audio=True)
            if not streams:
                raise Exception("No audio streams found")
            
            print(f"Found {len(streams)} audio streams")
            
            # Select the best quality stream
            stream = None
            # Try to get the smallest file size that's still good quality
            streams = sorted(streams, key=lambda x: x.filesize)
            for s in streams:
                print(f"Checking stream: {s.itag} - {s.mime_type} - {s.bitrate//1000}kbps")
                if s.bitrate >= 128000:  # Minimum 128kbps for acceptable quality
                    stream = s
                    break
            
            if not stream:
                stream = streams[0]
                print("Using first available stream as fallback")
            
            if not stream:
                raise Exception("No suitable audio stream found")
            
            print(f"Selected stream: {stream.itag} - {stream.mime_type}")
            
            # Get the stream URL
            try:
                stream_url = stream.url
                print("Successfully got stream URL")
            except Exception as e:
                print(f"Error getting stream URL: {str(e)}")
                print(f"Full error: {traceback.format_exc()}")
                raise
            
            # Create AudioStream object
            stream_info = AudioStream(
                url=stream_url,
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
            print(f"Full error: {traceback.format_exc()}")
            return {
                'status': 'error',
                'message': str(e),
                'stream': None
            }

def main():
    if len(sys.argv) != 2:
        print("Error: Please provide a YouTube URL as argument")
        print("Usage: python youtube_stream_local_test.py <youtube_url>")
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
        
        print("\nStream URL (use this with the proxy server):")
        print(f"{stream.url}")
    else:
        print(f"Error: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 