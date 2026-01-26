const puppeteer = require('puppeteer-core');

(async () => {
  try {
    console.log('Connecting to Chrome...');
    const browser = await puppeteer.connect({
      browserURL: 'http://127.0.0.1:9222',
      defaultViewport: null,
    });
    const pages = await browser.pages();
    console.log(`Connected! Found ${pages.length} tabs:`);
    for (let i = 0; i < pages.length; i++) {
      const title = await pages[i].title();
      const url = pages[i].url();
      console.log(`  ${i}: ${title} - ${url}`);
    }
    console.log('\nConnection successful!');
    await browser.disconnect();
  } catch (e) {
    console.error('Error:', e.message);
    console.log('\nMake sure Chrome was started with: --remote-debugging-port=9222');
  }
})();
