const { generate } = require('youtube-po-token-generator');
const fs = require('fs');
const path = require('path');

async function testTokenGenerator() {
    try {
        // Use stderr for logging
        console.error('Starting token generation process...');
        
        // Configure proxy if available
        const proxyUrl = process.env.HTTPS_PROXY;
        if (proxyUrl) {
            console.error('Using proxy:', proxyUrl);
            process.env.HTTPS_PROXY = proxyUrl;
            process.env.HTTP_PROXY = proxyUrl;
        } else {
            console.error('No proxy configured');
        }

        // Ensure we're in the correct directory
        const scriptDir = path.dirname(__filename);
        process.chdir(scriptDir);
        console.error('Working directory:', process.cwd());

        // Check if node_modules exists
        const nodeModulesPath = path.join(scriptDir, '..', 'node_modules');
        if (!fs.existsSync(nodeModulesPath)) {
            console.error('node_modules not found, installing dependencies...');
            const { execSync } = require('child_process');
            execSync('npm install', { stdio: 'inherit' });
        }
        
        console.error('Generating YouTube token...');
        const tokenData = await generate();
        
        if (!tokenData || !tokenData.visitorData || !tokenData.poToken) {
            throw new Error('Invalid token data received');
        }

        console.error('Token generated successfully');
        console.error('Visitor Data:', tokenData.visitorData);
        console.error('PoToken:', tokenData.poToken);
        
        // Save token to file
        const tokenPath = path.join(scriptDir, '..', 'token.json');
        const tokenContent = {
            ...tokenData,
            timestamp: Date.now()
        };
        
        fs.writeFileSync(tokenPath, JSON.stringify(tokenContent, null, 2));
        console.error('Token saved to:', tokenPath);
        
        // Output only the JSON data to stdout
        process.stdout.write(JSON.stringify(tokenContent));
        
    } catch (error) {
        console.error('Error generating token:', error.message);
        console.error('Stack trace:', error.stack);
        process.exit(1);
    }
}

// Run the token generator
testTokenGenerator(); 