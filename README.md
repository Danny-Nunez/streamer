# YouTube Audio Stream Extractor

A Python script that extracts audio stream URLs from YouTube videos for web streaming. This tool is designed to work reliably in server environments with proxy support.

## Features

- Extracts audio stream URLs from YouTube videos
- Supports proxy rotation for server deployment
- Caches YouTube tokens for improved performance
- Handles various YouTube URL formats
- Returns detailed stream information including format, bitrate, and file size

## Prerequisites

- Python 3.8 or higher
- Node.js 20.11.0 or higher
- npm 10.5.0 or higher

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd pytubefix
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Node.js dependencies:
```bash
npm install
```

5. Create a `.env` file with your proxy configuration:
```env
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
PROXY_HOST=your_proxy_host
SERVER_ENV=true
```

## Usage

Run the script with a YouTube URL as an argument:

```bash
python youtube_stream.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The script will return:
- Stream URL
- Format information
- Bitrate
- File size
- Video title and author
- Duration

## Proxy Configuration

The script supports proxy rotation for server deployment. Configure your proxy settings in the `.env` file:

```env
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
PROXY_HOST=your_proxy_host
```

Available proxy ports: 10001-10007

## Error Handling

The script includes:
- Automatic proxy rotation on failure
- Token caching and renewal
- Comprehensive error reporting
- Retry logic for failed requests

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
