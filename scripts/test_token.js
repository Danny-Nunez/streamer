const { generate } = require('youtube-po-token-generator');

async function testTokenGenerator() {
    try {
        console.log('Generating YouTube token...');
        
        // Configure proxy if available
        const proxyUrl = process.env.HTTPS_PROXY;
        if (proxyUrl) {
            console.log('Using proxy:', proxyUrl);
            process.env.HTTPS_PROXY = proxyUrl;
            process.env.HTTP_PROXY = proxyUrl;
        }
        
        const tokenData = await generate();
        console.log('Token generated successfully:');
        console.log(JSON.stringify(tokenData, null, 2));
        
        // Save token to file
        const fs = require('fs');
        fs.writeFileSync('token.json', JSON.stringify({
            ...tokenData,
            timestamp: Date.now()
        }));
        console.log('Token saved to token.json');
    } catch (error) {
        console.error('Error generating token:', error);
        process.exit(1);
    }
}

// Run the token generator
testTokenGenerator(); 