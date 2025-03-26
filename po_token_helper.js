const axios = require('axios');

async function getPOToken(videoId) {
    try {
        console.log(`Attempting to get token for video ID: ${videoId}`);
        
        // Generate a more reliable visitor data string
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 1000000);
        const visitorData = Buffer.from(`${timestamp}.${random}`).toString('base64');
        
        // Make a request to YouTube to get the token
        const response = await axios.get(`https://www.youtube.com/watch?v=${videoId}`, {
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

        // Extract the token from the response
        const html = response.data;
        const tokenMatch = html.match(/"poToken":"([^"]+)"/);
        
        if (!tokenMatch) {
            console.error('No token found in response');
            return null;
        }

        const token = tokenMatch[1];
        console.log('Successfully generated token and visitor data');
        
        return { 
            token, 
            visitorData,
            timestamp: timestamp 
        };
    } catch (error) {
        console.error('Error generating PO token:', error.message);
        if (error.stack) {
            console.error('Stack trace:', error.stack);
        }
        return null;
    }
}

// Handle command line arguments
const videoId = process.argv[2];
if (!videoId) {
    console.error('Please provide a video ID as an argument');
    process.exit(1);
}

getPOToken(videoId).then(result => {
    if (result) {
        console.log(JSON.stringify(result, null, 2));
    } else {
        console.log(JSON.stringify({ error: 'Failed to generate token' }));
    }
}).catch(error => {
    console.error('Unexpected error:', error);
    process.exit(1);
});
