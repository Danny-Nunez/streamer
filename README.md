# YouTube Audio Stream Extractor

This service extracts audio stream URLs from YouTube videos for web streaming. It uses a combination of Python and Node.js to handle token generation and stream extraction.

## Prerequisites

- Python 3.8+
- Node.js 20.11.0+
- npm 10.5.0+

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd pytubefix
```

2. Set up Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
SERVER_ENV=true
PROXY_URL=  # Optional: your proxy URL if needed
```

## Server Deployment

1. Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
npm install
```

2. Start the server:
```bash
python youtube_stream.py
```

## Usage

Send a GET request to the server with a YouTube URL:

```bash
python youtube_stream.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The server will return JSON containing the audio stream information, including:
- Stream URL
- Format
- Bitrate
- File size
- Title
- Author
- Length

## Important Notes

1. Token Generation:
   - The service automatically generates and caches YouTube tokens
   - Tokens are refreshed hourly
   - Token data is stored in `token.json`

2. Error Handling:
   - The service includes comprehensive error handling
   - Failed requests will return appropriate error messages
   - Multiple client types (ANDROID, IOS, WEB) are tried in sequence

3. Proxy Support:
   - Optional proxy support for server deployment
   - Configure proxy settings in the `.env` file

## Maintenance

- Monitor `token.json` for token validity
- Keep Node.js and Python packages updated
- Check logs for any token generation or stream extraction errors

## Troubleshooting

1. If token generation fails:
   - Check Node.js version and dependencies
   - Verify network connectivity
   - Check proxy settings if using a proxy

2. If stream extraction fails:
   - Verify YouTube URL format
   - Check token validity
   - Review server logs for specific errors

## Security Considerations

- Keep your `.env` file secure and never commit it to version control
- Regularly update dependencies for security patches
- Monitor token usage and implement rate limiting if needed
