const { generatePOToken } = require('@distube/ytdl-core');

async function getPOToken(videoId) {
    try {
        const poToken = await generatePOToken(videoId);
        // Generate a random visitor data string (YouTube format)
        const visitorData = Buffer.from(Math.random().toString()).toString('base64');
        return { token: poToken, visitorData };
    } catch (error) {
        console.error('Error generating PO token:', error);
        return null;
    }
}

// Handle command line arguments
const videoId = process.argv[2];
if (videoId) {
    getPOToken(videoId).then(result => {
        if (result) {
            console.log(JSON.stringify(result));
        } else {
            console.log(JSON.stringify({ error: 'Failed to generate token' }));
        }
    });
}
