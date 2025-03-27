const axios = require('axios');

async function generateToken() {
    try {
        // Generate a more reliable visitor data string
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 1000000);
        const visitorData = Buffer.from(`${timestamp}.${random}`).toString('base64');

        // First get the initial page to get cookies
        const response = await axios.get('https://www.youtube.com', {
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

        // Extract cookies from the response
        const cookies = response.headers['set-cookie'];
        if (!cookies) {
            throw new Error('No cookies received from YouTube');
        }

        // Now get the video page with cookies
        const videoResponse = await axios.get('https://www.youtube.com/watch?v=dQw4w9WgXcQ', {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Cookie': cookies.join('; '),
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
        });

        const html = videoResponse.data;
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
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response headers:', error.response.headers);
        }
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