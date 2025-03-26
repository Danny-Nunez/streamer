#!/usr/bin/env python3

"""
YouTube Audio Extractor
This script downloads audio from a YouTube video and saves it as a WAV file.
Usage: python youtube_audio.py <youtube_url>
"""

import sys
import os
import pytubefix
import ffmpeg
import time
from datetime import datetime

def main():
    # Check if URL is provided as command line argument
    if len(sys.argv) != 2:
        print("Error: Please provide a YouTube URL as argument")
        print("Usage: python youtube_audio.py <youtube_url>")
        sys.exit(1)

    # Get the YouTube video URL from command-line arguments
    youtube_url = sys.argv[1]

    # Ensure the audios directory exists
    os.makedirs("audios", exist_ok=True)

    # Specify the output file name for the audio
    filename = f"audios/"
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename += f"audio_{timestamp}.wav"

    try:
        # Create a YouTube object and fetch the stream URL
        print('Downloading audio from youtube...')
        yt = pytubefix.YouTube(youtube_url)

        print('Fetching audio stream...')
        # Get the audio-only stream with highest quality
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            raise Exception("No audio stream found")
        stream = audio_stream.url

        print('Use ffmpeg to convert the audio stream to a .wav file...')
        # Use ffmpeg to convert the audio stream to a .wav file
        ffmpeg.input(stream).output(filename, format='wav', loglevel="error").run()

        # Save the filename
        with open("filename_audio.txt", "w") as text_file:
            text_file.write(filename)

        print(f"Audio downloaded and saved as {filename}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
