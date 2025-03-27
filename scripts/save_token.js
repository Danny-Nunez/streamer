const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function saveToken() {
    let browser = null;
    try {
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        
        // Set viewport and user agent
        await page.setViewport({ width: 1280, height: 720 });
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

        // Navigate to YouTube
        await page.goto('https://www.youtube.com', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        // Get cookies and visitor data
        const cookies = await page.cookies();
        const visitorData = cookies.find(cookie => cookie.name === 'VISITOR_INFO1_LIVE')?.value || '';

        // Navigate to a video page
        await page.goto('https://www.youtube.com/watch?v=dQw4w9WgXcQ', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        // Wait for the page to load and get the PoToken
        await page.waitForFunction(() => {
            const scripts = document.getElementsByTagName('script');
            for (const script of scripts) {
                const content = script.textContent;
                if (content && content.includes('"poToken"')) {
                    const match = content.match(/"poToken":"([^"]+)"/);
                    return match ? match[1] : null;
                }
            }
            return null;
        }, { timeout: 10000 });

        // Extract PoToken from page content
        const pageContent = await page.content();
        const poTokenMatch = pageContent.match(/"poToken":"([^"]+)"/);
        
        if (!poTokenMatch) {
            throw new Error('PoToken not found in page content');
        }

        const tokenData = {
            visitorData,
            poToken: poTokenMatch[1],
            timestamp: Date.now()
        };

        // Save token to file
        const tokenPath = path.join(__dirname, '..', 'token.json');
        fs.writeFileSync(tokenPath, JSON.stringify(tokenData, null, 2));
        console.log('Token saved successfully to token.json');

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

// Generate and save the token
saveToken().then(result => {
    if (result) {
        console.log('Token saved successfully');
    } else {
        console.error('Failed to save token');
        process.exit(1);
    }
}).catch(error => {
    console.error('Unexpected error:', error);
    process.exit(1);
}); 