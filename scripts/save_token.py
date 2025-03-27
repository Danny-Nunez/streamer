#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
import yt_dlp

def save_token():
    try:
        print('Getting video info from YouTube...')
        
        # Configure yt-dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ', download=False)
            
            # Get cookies from info
            cookies = ydl.cookiejar._cookies.get('.youtube.com', {}).get('/', {})
            visitor_data = cookies.get('VISITOR_INFO1_LIVE').value if 'VISITOR_INFO1_LIVE' in cookies else ''
            
            # Get identity token from headers
            headers = info.get('http_headers', {})
            identity_token = headers.get('X-Youtube-Identity-Token', '')
            
            token_data = {
                'visitorData': visitor_data,
                'poToken': identity_token,
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
            
            if not token_data['visitorData'] or not token_data['poToken']:
                raise Exception('Could not extract required tokens')
            
            # Save token to file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            token_path = os.path.join(script_dir, '..', 'token.json')
            
            with open(token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print('Token saved successfully to token.json')
            print('Token data:', token_data)
            return True
            
    except Exception as e:
        print('Error generating token:', str(e), file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

if __name__ == '__main__':
    success = save_token()
    sys.exit(0 if success else 1) 