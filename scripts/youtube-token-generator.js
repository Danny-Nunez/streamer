const { scrapeYouTubeData } = require("po-token-generator");

const config = {
    headless: true,
    requestInterception: true,
    blockResources: ["image", "stylesheet", "font"],
    cacheOptions: { stdTTL: 600 }, // Cache results for 10 minutes
    viewport: { width: 1280, height: 720 },
};

async function generateToken() {
    try {
        // Use a known video ID to get a fresh token
        const videoId = "dQw4w9WgXcQ";
        const data = await scrapeYouTubeData(videoId, config);
        
        if (!data || !data.visitorData || !data.poToken) {
            throw new Error("Invalid token data received");
        }

        return {
            visitorData: data.visitorData,
            poToken: data.poToken
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