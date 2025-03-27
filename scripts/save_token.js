const axios = require('axios');
const fs = require('fs');
const path = require('path');

async function saveToken() {
    try {
        console.log('Getting video info from YouTube...');
        
        // First get the watch page to get cookies and session data
        const response = await axios.get('https://www.youtube.com/watch?v=dQw4w9WgXcQ', {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            }
        });

        // Extract cookies from response
        const cookies = response.headers['set-cookie'] || [];
        const visitorData = cookies.find(cookie => cookie.includes('VISITOR_INFO1_LIVE='))
            ?.split(';')[0]
            ?.split('=')[1] || '';

        console.log('Visitor Data:', visitorData);

        // Extract initial data from the response
        const initialDataMatch = response.data.match(/ytInitialPlayerResponse\s*=\s*({.+?});/);
        let playerData;
        if (initialDataMatch) {
            try {
                playerData = JSON.parse(initialDataMatch[1]);
                console.log('Found initial player data');
            } catch (e) {
                console.log('Failed to parse initial player data:', e.message);
            }
        }

        // Extract streaming data
        const streamingData = playerData?.streamingData;
        if (streamingData) {
            console.log('Found streaming data');
            const formats = [...(streamingData.formats || []), ...(streamingData.adaptiveFormats || [])];
            
            // Find a format with signatureCipher
            const format = formats.find(f => f.signatureCipher);
            if (format) {
                const params = new URLSearchParams(format.signatureCipher);
                const s = params.get('s');
                const sp = params.get('sp');
                const url = params.get('url');
                
                console.log('Found signature cipher components:');
                console.log('s:', s);
                console.log('sp:', sp);
                console.log('url:', url);

                const tokenData = {
                    visitorData: visitorData,
                    signatureTimestamp: playerData.playerConfig?.playerResponse?.playbackContext?.contentPlaybackContext?.signatureTimestamp || "20231229",
                    signature: s,
                    signatureParam: sp,
                    url: url,
                    timestamp: Date.now()
                };

                // Save token to file
                const tokenPath = path.join(__dirname, '..', 'token.json');
                fs.writeFileSync(tokenPath, JSON.stringify(tokenData, null, 2));
                console.log('Token saved successfully to token.json');
                console.log('Token data:', tokenData);

                return tokenData;
            } else {
                throw new Error('No format with signature cipher found');
            }
        } else {
            throw new Error('No streaming data found');
        }
    } catch (error) {
        console.error('Error generating token:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response data:', error.response.data);
        }
        if (error.stack) {
            console.error('Stack trace:', error.stack);
        }
        return null;
    }
}

// Generate and save the token
saveToken().then(result => {
    if (result) {
        console.log('Token saved successfully');
        process.exit(0);
    } else {
        console.error('Failed to save token');
        process.exit(1);
    }
}).catch(error => {
    console.error('Unexpected error:', error);
    process.exit(1);
}); 