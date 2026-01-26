const puppeteer = require('puppeteer-core');

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function checkMapExport(page, mapUrl, mapName) {
  console.log(`\nChecking: ${mapName}`);
  console.log(`URL: ${mapUrl}`);

  await page.goto(mapUrl, { waitUntil: 'networkidle2', timeout: 60000 });
  await sleep(3000);

  // Look for menu/export options
  const pageText = await page.evaluate(() => document.body.innerText);

  // Check if there's a download/export option
  const hasExport = pageText.toLowerCase().includes('download kml') ||
                    pageText.toLowerCase().includes('export');

  console.log(`  Has export option visible: ${hasExport}`);

  // Try clicking the menu (three dots)
  const menuClicked = await page.evaluate(() => {
    const menuBtn = document.querySelector('[aria-label*="menu"], [aria-label*="Menu"], [data-tooltip*="menu"]');
    if (menuBtn) {
      menuBtn.click();
      return true;
    }
    // Try finding by icon
    const dots = document.querySelector('button svg, [role="button"] svg');
    if (dots) {
      dots.closest('button, [role="button"]').click();
      return true;
    }
    return false;
  });

  if (menuClicked) {
    await sleep(2000);
    const menuText = await page.evaluate(() => document.body.innerText);
    console.log(`  Menu options found: ${menuText.includes('Download KML') ? 'YES - Download KML available!' : 'No download option'}`);

    if (menuText.includes('Download KML')) {
      return { canExport: true, mapName, mapUrl };
    }
  }

  // Check for the KML download link pattern
  // Google My Maps KML export URL pattern: https://www.google.com/maps/d/kml?mid=MAP_ID
  const mapId = mapUrl.match(/mid=([^&]+)/)?.[1];
  if (mapId) {
    const kmlUrl = `https://www.google.com/maps/d/kml?mid=${mapId}`;
    console.log(`  Potential KML URL: ${kmlUrl}`);
    return { canExport: 'maybe', kmlUrl, mapId, mapName };
  }

  return { canExport: false, mapName };
}

async function main() {
  console.log('='.repeat(50));
  console.log('Checking Gang Territory Maps for Export');
  console.log('='.repeat(50));

  const maps = [
    { url: 'https://www.google.com/maps/d/viewer?mid=1ul5yqMj7_JgM5xpfOn5gtlO-bTk', name: 'LA Gang Map' },
    { url: 'https://www.google.com/maps/d/viewer?mid=16mwL1secIRSyCH5sYNyAE3U_rAPC_D8I', name: 'Chicago Gang Map' },
    { url: 'https://www.google.com/maps/d/viewer?mid=1DoDpgLSdHmsdFJXjqsbybzyDZUKJ59vw', name: 'Detroit Gang Map' },
  ];

  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:9222',
    defaultViewport: null,
  });

  const pages = await browser.pages();
  const page = pages[0];

  const results = [];
  for (const map of maps) {
    const result = await checkMapExport(page, map.url, map.name);
    results.push(result);
  }

  console.log('\n' + '='.repeat(50));
  console.log('RESULTS:');
  console.log('='.repeat(50));
  results.forEach(r => {
    console.log(`${r.mapName}: ${r.canExport ? 'CAN EXPORT' : 'Cannot export directly'}`);
    if (r.kmlUrl) console.log(`  Try: ${r.kmlUrl}`);
  });

  await browser.disconnect();
}

main().catch(console.error);
