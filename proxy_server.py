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
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
                #status { margin-top: 20px; padding: 10px; border-radius: 4px; }
                .error { background: #ffebee; color: #c62828; }
                .success { background: #e8f5e9; color: #2e7d32; }
            </style>
        </head>
        <body>
            <h1>YouTube Audio Stream Proxy</h1>
            <p>Enter the stream URL from youtube_stream_local_test.py:</p>
            <input type="text" id="url" placeholder="Paste stream URL here">
            <button onclick="playStream()">Play</button>
            <div id="status"></div>
            <audio id="audio" controls style="width: 100%; margin-top: 20px;"></audio>
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
                    status.className = '';
                    
                    const proxyUrl = '/proxy?url=' + encodeURIComponent(url);
                    audio.src = proxyUrl;
                    audio.play().catch(e => {
                        status.textContent = 'Error: ' + e.message;
                        status.className = 'error';
                    });
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
        
        # Parse the URL to get the host and path
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path + '?' + parsed_url.query if parsed_url.query else parsed_url.path
        
        # Set up headers with more realistic browser values
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

        # Make request through proxy
        try:
            # First make a HEAD request to check if the resource is accessible
            head_response = session.head(
                url,
                headers=headers,
                verify=False,
                timeout=30,
                allow_redirects=True
            )
            
            if head_response.status_code not in [200, 206]:
                logger.error(f"HEAD request failed with status code {head_response.status_code}")
                logger.error(f"Response headers: {head_response.headers}")
                return f'Error: {head_response.status_code}', head_response.status_code

            # If HEAD request succeeds, make the GET request
            response = session.get(
                url,
                headers=headers,
                stream=True,
                verify=False,
                timeout=30,
                allow_redirects=True
            )

            # Check if request was successful
            if response.status_code not in [200, 206]:
                logger.error(f"Error: Status code {response.status_code}")
                logger.error(f"Response headers: {response.headers}")
                return f'Error: {response.status_code}', response.status_code

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
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return f'Request error: {str(e)}', 500

    except Exception as e:
        logger.error(f"Error in proxy: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    print(f"Starting proxy server on port {port}")
    print("1. Run youtube_stream_local_test.py to get a stream URL")
    print("2. Copy the URL and paste it in the web interface")
    print("3. Click Play to start streaming")
    app.run(host='0.0.0.0', port=port) 