from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
from youtube_stream import YouTubeAudioExtractor, AudioStream
from cachetools import TTLCache
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os
from datetime import datetime
from pathlib import Path
import re

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Audio Stream API",
    description="API for extracting audio streams from YouTube videos",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize cache (TTL = 1 hour)
cache = TTLCache(maxsize=100, ttl=3600)

# Initialize YouTube extractor
extractor = YouTubeAudioExtractor()

# Create audios directory if it doesn't exist
audio_dir = Path('audios')
audio_dir.mkdir(exist_ok=True)

# Mount the audios directory
app.mount("/audios", StaticFiles(directory="audios"), name="audios")

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
        "name": "YouTube Audio Stream API",
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

@app.post("/api/cleanup")
async def cleanup_audio(filename: str):
    """Clean up an audio file"""
    try:
        file_path = audio_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete the file
        file_path.unlink()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream/{video_id}")
@limiter.limit("100/hour")
async def get_stream(request: Request, video_id: str, format: Optional[str] = None):
    """
    Get audio stream information for a YouTube video ID
    
    Args:
        video_id: YouTube video ID
        format: Preferred audio format (optional)
    """
    try:
        # Extract video ID if URL is provided
        video_id = extract_video_id(video_id)
        
        # Check cache first
        cache_key = f"{video_id}:{format}"
        if cache_key in cache:
            return cache[cache_key]

        # Construct YouTube URL
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Get stream information
        result = extractor.get_audio_stream(youtube_url, format)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Convert AudioStream object to dict for JSON response
        stream = result["stream"]
        response = {
            "status": "success",
            "data": {
                "video_id": video_id,
                "url": stream.url,
                "format": stream.format,
                "bitrate": stream.bitrate,
                "mime_type": stream.mime_type,
                "filesize": stream.filesize,
                "title": stream.title,
                "author": stream.author,
                "length": stream.length,
                "local_path": result.get("local_path"),
                "proxy_info": result.get("proxy_info")
            }
        }
        
        # Cache the response
        cache[cache_key] = response
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream/{video_id}/download")
@limiter.limit("50/hour")
async def download_audio(video_id: str):
    """
    Download and stream audio directly for mobile playback
    
    Args:
        video_id: YouTube video ID
    """
    try:
        # Extract video ID if URL is provided
        video_id = extract_video_id(video_id)
        
        # Construct YouTube URL
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Get stream information
        result = extractor.get_audio_stream(youtube_url)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Get the local file path
        local_path = result.get("local_path")
        if not local_path:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Return the file as a streaming response
        return FileResponse(
            local_path,
            media_type=result["stream"].mime_type,
            filename=f"{video_id}.{result['stream'].format}",
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "no-cache",
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
