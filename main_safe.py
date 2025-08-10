from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import uvicorn
import os
from datetime import datetime
from pathlib import Path
import re
import asyncio
import concurrent.futures
import time
import signal
import threading

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Audio Stream API (Safe)",
    description="API for extracting audio streams from YouTube videos with safe error handling",
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

# Create a thread pool for YouTube operations
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    print("🚀 YouTube Audio Stream API (Safe) starting up...")
    print(f"📦 Python version: {os.sys.version}")
    print(f"🌐 Server will run on port: {os.getenv('PORT', '8000')}")
    print("✅ Startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down YouTube Audio Stream API...")
    executor.shutdown(wait=True)
    print("✅ Shutdown complete!")

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

def extract_youtube_stream_with_timeout(video_id: str, timeout: int = 20):
    """Extract YouTube stream information with strict timeout"""
    try:
        # Import pytubefix inside the function to avoid import issues
        import pytubefix
        
        # Construct YouTube URL
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Create YouTube object
        yt = pytubefix.YouTube(youtube_url)
        
        # Get audio streams with timeout check
        start_time = time.time()
        streams = yt.streams.filter(only_audio=True)
        
        if time.time() - start_time > timeout:
            raise Exception("YouTube stream extraction timed out")
        
        if not streams:
            raise Exception("No audio streams found")
        
        # Select the best quality stream
        stream = None
        streams = sorted(streams, key=lambda x: x.filesize)
        for s in streams:
            if s.bitrate >= 128000:  # Minimum 128kbps
                stream = s
                break
        
        if not stream:
            stream = streams[0]
        
        return {
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
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {
        "name": "YouTube Audio Stream API (Safe)",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/api/health",
            "stream_info": "/api/stream/{video_id}",
            "stream_audio": "/api/stream/{video_id}/proxy",
            "test": "/api/test"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "FastAPI",
        "version": "1.0.0"
    }

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint to verify server is working"""
    return {
        "status": "success",
        "message": "Server is working",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stream/{video_id}")
async def get_stream(request: Request, video_id: str, format: Optional[str] = None):
    """
    Get audio stream information for a YouTube video ID with safe timeout
    """
    try:
        # Extract video ID if URL is provided
        video_id = extract_video_id(video_id)
        
        print(f"🔍 Extracting stream for video: {video_id}")
        
        # Run YouTube extraction in thread pool with strict timeout
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(executor, extract_youtube_stream_with_timeout, video_id, 20),
            timeout=25.0  # 5 seconds extra for overhead
        )
        
        print(f"📊 Extraction result: {result['status']}")
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result

    except asyncio.TimeoutError:
        print(f"⏰ Timeout for video: {video_id}")
        raise HTTPException(status_code=408, detail="Request timeout - YouTube extraction took too long")
    except Exception as e:
        print(f"❌ Error for video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream/{video_id}/proxy")
async def proxy_stream(request: Request, video_id: str):
    """
    Proxy the audio stream through this server with safe timeout
    """
    try:
        print(f"🎵 Proxying stream for video: {video_id}")
        
        # Get stream info first with timeout
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
        
        # Make request to YouTube with timeout
        import requests
        
        def fetch_stream():
            return requests.get(
                stream_url,
                headers=headers,
                stream=True,
                timeout=15  # Shorter timeout for streaming
            )
        
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(executor, fetch_stream),
            timeout=20.0
        )
        
        if response.status_code not in [200, 206]:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch stream")
        
        print(f"✅ Successfully proxying stream for video: {video_id}")
        
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
        
    except asyncio.TimeoutError:
        print(f"⏰ Proxy timeout for video: {video_id}")
        raise HTTPException(status_code=408, detail="Request timeout - Stream fetch took too long")
    except Exception as e:
        print(f"❌ Proxy error for video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run("main_safe:app", host="0.0.0.0", port=port, reload=False) 