const axios = require('axios');

async function generateToken() {
    try {
        // Generate a random video ID to get a fresh token
        const randomVideoId = 'dQw4w9WgXcQ'; // Using a known video ID
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 1000000);
        const visitorData = Buffer.from(`${timestamp}.${random}`).toString('base64');

        const response = await axios.get(`https://www.youtube.com/watch?v=${randomVideoId}`, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
        });

        const html = response.data;
        const tokenMatch = html.match(/"poToken":"([^"]+)"/);
        
        if (!tokenMatch) {
            console.error('No token found in response');
            return null;
        }

        return {
            visitorData,
            poToken: tokenMatch[1]
        };
    } catch (error) {
        console.error('Error generating token:', error.message);
        return null;
    }
}

// Generate and output the token
generateToken().then(result => {
    if (result) {
        console.log(JSON.stringify(result));
    } else {
        console.log(JSON.stringify({ error: 'Failed to generate token' }));
    }
}).catch(error => {
    console.error('Unexpected error:', error);
    process.exit(1);
}); 