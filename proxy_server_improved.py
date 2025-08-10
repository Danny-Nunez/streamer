from flask import Flask, Response, request
import requests
import sys
import urllib.parse
import re
import os
from dotenv import load_dotenv
import logging
import urllib3
import base64
import time

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

def extract_ip_from_url(url):
    """Extract IP address from URL parameters."""
    try:
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)
        if 'ip' in query_params:
            return query_params['ip'][0].strip()
    except Exception as e:
        logger.error(f"Error extracting IP: {e}")
    return None

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>YouTube Audio Stream Proxy</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }
                .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 4px; }
                button:hover { background: #0056b3; }
                #status { margin-top: 20px; padding: 10px; border-radius: 4px; }
                .error { background: #ffebee; color: #c62828; }
                .success { background: #e8f5e9; color: #2e7d32; }
                .loading { background: #e3f2fd; color: #1565c0; }
                .info { background: #f3e5f5; color: #6a1b9a; margin-bottom: 20px; padding: 15px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>YouTube Audio Stream Proxy</h1>
                <div class="info">
                    <strong>How to use:</strong><br>
                    1. Run <code>python3 youtube_stream_local_test.py "YOUTUBE_URL"</code> to get a stream URL<br>
                    2. Copy the stream URL and paste it below<br>
                    3. Click Play to start streaming through the proxy
                </div>
                <input type="text" id="url" placeholder="Paste stream URL here">
                <button onclick="playStream()">Play</button>
                <div id="status"></div>
                <audio id="audio" controls style="width: 100%; margin-top: 20px;"></audio>
            </div>
            <script>
                function playStream() {
                    const url = document.getElementById('url').value;
                    const status = document.getElementById('status');
                    const audio = document.getElementById('audio');
                    
                    if (!url) {
                        status.textContent = 'Please enter a URL';
                        status.className = 'error';
                        return;
                    }
                    
                    status.textContent = 'Loading...';
                    status.className = 'loading';
                    
                    const proxyUrl = '/proxy?url=' + encodeURIComponent(url);
                    audio.src = proxyUrl;
                    audio.play().catch(e => {
                        status.textContent = 'Error: ' + e.message;
                        status.className = 'error';
                    });
                    
                    audio.onloadstart = () => {
                        status.textContent = 'Loading audio...';
                        status.className = 'loading';
                    };
                    
                    audio.oncanplay = () => {
                        status.textContent = 'Audio loaded successfully!';
                        status.className = 'success';
                    };
                    
                    audio.onerror = () => {
                        status.textContent = 'Error loading audio. Check the URL and try again.';
                        status.className = 'error';
                    };
                }
            </script>
        </body>
    </html>
    '''

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return 'No URL provided', 400

    try:
        # Extract IP from URL
        ip = extract_ip_from_url(url)
        if not ip:
            logger.error("No IP found in URL")
            return 'No IP found in URL', 400

        # Get proxy settings from environment
        proxy_host = os.getenv('PROXY_HOST')
        proxy_username = os.getenv('PROXY_USERNAME')
        proxy_password = os.getenv('PROXY_PASSWORD')
        
        if not all([proxy_host, proxy_username, proxy_password]):
            logger.error("Missing proxy configuration")
            return 'Missing proxy configuration', 500

        # Configure proxy URL with authentication
        proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:10001"
        
        # Log proxy configuration (without sensitive data)
        logger.info(f"Using proxy host: {proxy_host}")
        
        # Get range header from request
        range_header = request.headers.get('Range')
        
        # Parse the URL to get the host
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc
        
        # Set up headers with realistic browser values
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/',
            'Connection': 'keep-alive',
            'X-Forwarded-For': ip,
            'X-Real-IP': ip,
            'Sec-Fetch-Dest': 'audio',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-GPC': '1',
            'Host': host,
            'X-YouTube-Client-Name': '1',
            'X-YouTube-Client-Version': '2.20250202.01.00',
            'X-YouTube-Device': 'cbr=Chrome&cbrver=122.0.0.0&c=WEB&cver=2.20250202.01.00&cplayer=UNIPLAYER&cos=Windows&cosver=10.0.0'
        }

        # Add range header if present
        if range_header:
            headers['Range'] = range_header

        logger.info(f"Making request to {url} with IP {ip}")
        
        # Create a session to handle cookies and connection pooling
        session = requests.Session()
        
        # Configure proxy authentication
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        # Make request through proxy with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} of {max_retries}")
                
                # Make the GET request directly (skip HEAD request to avoid issues)
                response = session.get(
                    url,
                    headers=headers,
                    stream=True,
                    verify=False,
                    timeout=30,
                    allow_redirects=True
                )

                # Check if request was successful
                if response.status_code in [200, 206]:
                    logger.info(f"Request successful: {response.status_code}")
                    
                    # Stream the response
                    return Response(
                        response.iter_content(chunk_size=8192),
                        content_type=response.headers.get('content-type', 'audio/mp4'),
                        status=response.status_code,
                        headers={
                            'Accept-Ranges': 'bytes',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, OPTIONS',
                            'Access-Control-Allow-Headers': 'Range, Origin, Accept, Content-Type',
                            'Access-Control-Expose-Headers': 'Content-Length, Content-Range',
                            'Content-Type': response.headers.get('content-type', 'audio/mp4')
                        }
                    )
                else:
                    logger.error(f"Error: Status code {response.status_code}")
                    logger.error(f"Response headers: {response.headers}")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in 2 seconds...")
                        time.sleep(2)
                        continue
                    else:
                        return f'Error: {response.status_code}', response.status_code
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    return f'Request error: {str(e)}', 500

    except Exception as e:
        logger.error(f"Error in proxy: {str(e)}")
        return str(e), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'timestamp': time.time()}

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    print(f"Starting proxy server on port {port}")
    print("1. Run youtube_stream_local_test.py to get a stream URL")
    print("2. Copy the URL and paste it in the web interface")
    print("3. Click Play to start streaming")
    app.run(host='0.0.0.0', port=port) 