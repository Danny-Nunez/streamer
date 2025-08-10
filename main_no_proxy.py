from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import pytubefix
import uvicorn
import os
from datetime import datetime
from pathlib import Path
import re

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Audio Stream API (No Proxy)",
    description="API for extracting audio streams from YouTube videos without proxy",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from URL or return if already an ID"""
    if len(url_or_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    raise HTTPException(status_code=400, detail="Invalid YouTube URL or video ID")

@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {
        "name": "YouTube Audio Stream API (No Proxy)",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stream/{video_id}")
async def get_stream(request: Request, video_id: str, format: Optional[str] = None):
    """
    Get audio stream information for a YouTube video ID (no proxy)
    """
    try:
        # Extract video ID if URL is provided
        video_id = extract_video_id(video_id)
        
        # Construct YouTube URL
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Create YouTube object without proxy
        yt = pytubefix.YouTube(youtube_url)
        
        # Get audio streams
        streams = yt.streams.filter(only_audio=True)
        if not streams:
            raise HTTPException(status_code=400, detail="No audio streams found")
        
        # Select the best quality stream
        stream = None
        streams = sorted(streams, key=lambda x: x.filesize)
        for s in streams:
            if s.bitrate >= 128000:  # Minimum 128kbps
                stream = s
                break
        
        if not stream:
            stream = streams[0]
        
        response = {
            "status": "success",
            "data": {
                "video_id": video_id,
                "url": stream.url,
                "format": stream.mime_type.split('/')[-1],
                "bitrate": stream.bitrate,
                "mime_type": stream.mime_type,
                "filesize": stream.filesize,
                "title": yt.title,
                "author": yt.author,
                "length": yt.length
            }
        }
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream/{video_id}/proxy")
async def proxy_stream(request: Request, video_id: str):
    """
    Proxy the audio stream through this server
    """
    try:
        # Get stream info first
        stream_response = await get_stream(request, video_id)
        stream_data = stream_response["data"]
        stream_url = stream_data["url"]
        
        # Get range header from request
        range_header = request.headers.get('Range')
        
        # Set up headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/',
            'Connection': 'keep-alive',
        }
        
        if range_header:
            headers['Range'] = range_header
        
        # Make request to YouTube
        import requests
        response = requests.get(
            stream_url,
            headers=headers,
            stream=True,
            timeout=30
        )
        
        if response.status_code not in [200, 206]:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch stream")
        
        # Return streaming response
        return StreamingResponse(
            response.iter_content(chunk_size=8192),
            media_type=response.headers.get('content-type', 'audio/mp4'),
            headers={
                'Accept-Ranges': 'bytes',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Range, Origin, Accept, Content-Type',
                'Access-Control-Expose-Headers': 'Content-Length, Content-Range',
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main_no_proxy:app", host="0.0.0.0", port=port, reload=True) 