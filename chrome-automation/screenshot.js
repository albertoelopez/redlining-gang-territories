const puppeteer = require('puppeteer-core');

async function main() {
  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:9222',
    defaultViewport: null,
  });

  const pages = await browser.pages();
  const page = pages[0];

  console.log('Page title:', await page.title());
  console.log('Taking screenshot...');

  await page.screenshot({ path: 'map_screenshot.png', fullPage: false });

  console.log('Screenshot saved to map_screenshot.png');
  await browser.disconnect();
}

main().catch(console.error);
