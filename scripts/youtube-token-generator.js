const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function loadSavedToken() {
    try {
        const tokenPath = path.join(__dirname, '..', 'token.json');
        if (fs.existsSync(tokenPath)) {
            const tokenData = JSON.parse(fs.readFileSync(tokenPath, 'utf8'));
            // Check if token is less than 1 hour old
            if (Date.now() - tokenData.timestamp < 3600000) {
                return tokenData;
            }
        }
    } catch (error) {
        console.error('Error loading saved token:', error.message);
    }
    return null;
}

async function generateToken() {
    // Try to load saved token first
    const savedToken = await loadSavedToken();
    if (savedToken) {
        console.log('Using saved token');
        return savedToken;
    }

    let browser = null;
    try {
        browser = await puppeteer.launch({
            headless: "new",
            executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1280,720'
            ]
        });

        const page = await browser.newPage();
        
        // Block unnecessary resources
        await page.setRequestInterception(true);
        page.on('request', (request) => {
            const resourceType = request.resourceType();
            if (['image', 'stylesheet', 'font', 'media'].includes(resourceType)) {
                request.abort();
            } else {
                request.continue();
            }
        });

        // Set viewport and user agent
        await page.setViewport({ width: 1280, height: 720 });
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

        console.log('Navigating to YouTube...');
        // Navigate to YouTube
        await page.goto('https://www.youtube.com', {
            waitUntil: 'networkidle2',
            timeout: 60000
        });

        // Get cookies and visitor data
        const cookies = await page.cookies();
        const visitorData = cookies.find(cookie => cookie.name === 'VISITOR_INFO1_LIVE')?.value || '';
        console.log('Got visitor data:', visitorData);

        console.log('Navigating to video page...');
        // Navigate to a video page
        await page.goto('https://www.youtube.com/watch?v=dQw4w9WgXcQ', {
            waitUntil: 'networkidle2',
            timeout: 60000
        });

        console.log('Waiting for page content...');
        // Wait for some content to load
        await page.waitForSelector('script', { timeout: 30000 });

        // Extract PoToken using page evaluation
        const poToken = await page.evaluate(() => {
            const ytcfg = window.ytcfg?.get?.('ID_TOKEN');
            if (ytcfg) return ytcfg;

            // Try alternative method
            for (const script of document.getElementsByTagName('script')) {
                const content = script.textContent || '';
                const match = content.match(/"ID_TOKEN":"([^"]+)"/);
                if (match) return match[1];
                
                const poMatch = content.match(/"poToken":"([^"]+)"/);
                if (poMatch) return poMatch[1];
            }
            return null;
        });

        if (!poToken) {
            throw new Error('PoToken not found in page content');
        }

        console.log('Found PoToken');
        const tokenData = {
            visitorData,
            poToken,
            timestamp: Date.now()
        };

        // Save the new token
        const tokenPath = path.join(__dirname, '..', 'token.json');
        fs.writeFileSync(tokenPath, JSON.stringify(tokenData, null, 2));
        console.log('Token data:', tokenData);

        return tokenData;
    } catch (error) {
        console.error('Error generating token:', error.message);
        return null;
    } finally {
        if (browser) {
            await browser.close();
        }
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