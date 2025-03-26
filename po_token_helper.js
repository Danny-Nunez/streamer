const { getInfo } = require('@distube/ytdl-core');

async function getPOToken(videoId) {
    try {
        console.log(`Attempting to get info for video ID: ${videoId}`);
        const info = await getInfo(`https://www.youtube.com/watch?v=${videoId}`, {
            lang: 'en',
            requestOptions: {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
            }
        });

        console.log('Successfully retrieved video info');
        
        // Generate a more reliable visitor data string
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 1000000);
        const visitorData = Buffer.from(`${timestamp}.${random}`).toString('base64');
        
        if (!info.poToken) {
            console.error('No poToken found in video info');
            return null;
        }

        console.log('Successfully generated token and visitor data');
        return { 
            token: info.poToken, 
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
