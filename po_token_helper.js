const { generateToken } = require('youtube-po-token-generator');

async function getPOToken(videoId) {
    try {
        console.log(`Attempting to get token for video ID: ${videoId}`);
        
        // Generate a more reliable visitor data string
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 1000000);
        const visitorData = Buffer.from(`${timestamp}.${random}`).toString('base64');
        
        // Get the token using the generator
        const token = await generateToken(videoId);
        
        if (!token) {
            console.error('Failed to generate token');
            return null;
        }

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
