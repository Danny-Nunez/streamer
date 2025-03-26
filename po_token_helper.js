const { generatePOToken } = require('@distube/ytdl-core');

async function getPOToken(videoId) {
    try {
        const poToken = await generatePOToken(videoId);
        return poToken;
    } catch (error) {
        console.error('Error generating PO token:', error);
        return null;
    }
}

// Handle command line arguments
const videoId = process.argv[2];
if (videoId) {
    getPOToken(videoId).then(token => {
        if (token) {
            console.log(JSON.stringify({ token }));
        } else {
            console.log(JSON.stringify({ error: 'Failed to generate token' }));
        }
    });
}
