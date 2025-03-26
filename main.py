from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from youtube_stream import YouTubeAudioExtractor, AudioStream
from cachetools import TTLCache
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os
from datetime import datetime

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

@app.get("/api/stream")
@limiter.limit("100/hour")
async def get_stream(request: Request, url: str, format: Optional[str] = None):
    """
    Get audio stream information for a YouTube video
    
    Args:
        url: YouTube video URL
        format: Preferred audio format (optional)
    """
    try:
        # Check cache first
        cache_key = f"{url}:{format}"
        if cache_key in cache:
            return cache[cache_key]

        # Get stream information
        result = extractor.get_audio_stream(url, format)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Convert AudioStream object to dict for JSON response
        stream = result["stream"]
        response = {
            "status": "success",
            "data": {
                "url": stream.url,
                "format": stream.format,
                "bitrate": stream.bitrate,
                "mime_type": stream.mime_type,
                "filesize": stream.filesize,
                "title": stream.title,
                "author": stream.author,
                "length": stream.length
            }
        }
        
        # Cache the response
        cache[cache_key] = response
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
