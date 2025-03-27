const { generate } = require('youtube-po-token-generator');
const fs = require('fs');
const path = require('path');

async function testTokenGenerator() {
    try {
        console.log('Starting token generation process...');
        
        // Configure proxy if available
        const proxyUrl = process.env.HTTPS_PROXY;
        if (proxyUrl) {
            console.log('Using proxy:', proxyUrl);
            process.env.HTTPS_PROXY = proxyUrl;
            process.env.HTTP_PROXY = proxyUrl;
        } else {
            console.log('No proxy configured');
        }

        // Ensure we're in the correct directory
        const scriptDir = path.dirname(__filename);
        process.chdir(scriptDir);
        console.log('Working directory:', process.cwd());

        // Check if node_modules exists
        const nodeModulesPath = path.join(scriptDir, '..', 'node_modules');
        if (!fs.existsSync(nodeModulesPath)) {
            console.log('node_modules not found, installing dependencies...');
            const { execSync } = require('child_process');
            execSync('npm install', { stdio: 'inherit' });
        }
        
        console.log('Generating YouTube token...');
        const tokenData = await generate();
        
        if (!tokenData || !tokenData.visitorData || !tokenData.poToken) {
            throw new Error('Invalid token data received');
        }

        console.log('Token generated successfully');
        console.log('Visitor Data:', tokenData.visitorData);
        console.log('PoToken:', tokenData.poToken);
        
        // Save token to file
        const tokenPath = path.join(scriptDir, '..', 'token.json');
        const tokenContent = {
            ...tokenData,
            timestamp: Date.now()
        };
        
        fs.writeFileSync(tokenPath, JSON.stringify(tokenContent, null, 2));
        console.log('Token saved to:', tokenPath);
        
        // Output the token data as JSON for the Python script to parse
        console.log(JSON.stringify(tokenContent));
        
    } catch (error) {
        console.error('Error generating token:', error.message);
        console.error('Stack trace:', error.stack);
        process.exit(1);
    }
}

// Run the token generator
testTokenGenerator(); 