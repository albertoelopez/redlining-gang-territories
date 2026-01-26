const puppeteer = require('puppeteer-core');
const path = require('path');

const KML_FILES = [
  { file: 'la_gang_territories.kml', name: 'LA Gang Territories' },
  { file: 'chicago_gang_territories.kml', name: 'Chicago Gang Territories' },
  { file: 'detroit_gang_territories.kml', name: 'Detroit Gang Territories' },
];

const KML_DIR = 'D:\\AI_Projects\\chrome-automation-mcp';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function clickByText(page, text) {
  const clicked = await page.evaluate((searchText) => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while (node = walker.nextNode()) {
      if (node.textContent.trim() === searchText) {
        const parent = node.parentElement;
        if (parent && parent.offsetParent !== null) {
          parent.click();
          return true;
        }
      }
    }
    return false;
  }, text);
  return clicked;
}

async function importKML(page, filePath, layerName) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Importing: ${layerName}`);
  console.log(`File: ${filePath}`);
  console.log('='.repeat(50));

  await sleep(1500);

  // Click Add layer
  console.log('  Clicking "Add layer"...');
  await clickByText(page, 'Add layer');
  await sleep(2000);

  // Click Import
  console.log('  Clicking "Import"...');
  await clickByText(page, 'Import');
  await sleep(3000);

  // Find the Google Picker iframe
  console.log('  Looking for Google Picker iframe...');

  const frames = page.frames();
  let pickerFrame = null;

  for (const frame of frames) {
    const url = frame.url();
    if (url.includes('docs.google.com/picker')) {
      pickerFrame = frame;
      console.log('  ✓ Found Picker iframe');
      break;
    }
  }

  if (!pickerFrame) {
    console.log('  ✗ Could not find Picker iframe');
    return false;
  }

  // Look for file input in the picker iframe
  console.log('  Looking for file input in picker...');

  try {
    await sleep(2000);

    const fileInputHandle = await pickerFrame.$('input[type="file"]');

    if (fileInputHandle) {
      console.log('  ✓ Found file input in picker');
      await fileInputHandle.uploadFile(filePath);
      console.log('  ✓ File uploaded, waiting for processing...');

      // Gang territory files are larger, need more time
      console.log('  (Large file - this may take a moment...)');
      await sleep(15000);

      // Check for any confirmation dialogs
      await pickerFrame.evaluate(() => {
        const selectBtn = document.querySelector('[data-action="select"], .picker-actions button');
        if (selectBtn) selectBtn.click();
      });

      await sleep(5000);
      console.log(`  ✓ Imported ${layerName}`);
      return true;
    }
  } catch (error) {
    console.log('  Error accessing picker:', error.message);
  }

  console.log('  ✗ Could not upload file');
  return false;
}

async function main() {
  console.log('='.repeat(50));
  console.log('Google My Maps - Gang Territory Import');
  console.log('='.repeat(50));

  try {
    console.log('\nConnecting to Chrome...');
    const browser = await puppeteer.connect({
      browserURL: 'http://127.0.0.1:9222',
      defaultViewport: null,
    });

    const pages = await browser.pages();
    const page = pages[0];

    // Make sure we're on the right page
    const currentUrl = page.url();
    if (!currentUrl.includes('google.com/maps/d/')) {
      console.log('Navigating to your map...');
      await page.goto('https://www.google.com/maps/d/edit?mid=1ZVrmucM25m7EJEK6l7TeSxQ6fhKaCbk', {
        waitUntil: 'networkidle2',
        timeout: 60000
      });
    }

    console.log(`Connected! Page: ${await page.title()}`);

    await sleep(2000);

    // Import each gang territory file
    let successCount = 0;
    for (let i = 0; i < KML_FILES.length; i++) {
      const kml = KML_FILES[i];
      const filePath = path.join(KML_DIR, kml.file);

      const success = await importKML(page, filePath, kml.name);
      if (success) successCount++;

      await page.screenshot({ path: `D:\\AI_Projects\\chrome-automation-mcp\\gang_step${i + 1}.png` });
      console.log(`  Screenshot: gang_step${i + 1}.png`);

      await sleep(3000);
    }

    console.log('\n' + '='.repeat(50));
    console.log(`DONE! ${successCount}/${KML_FILES.length} gang territory files imported`);
    console.log('='.repeat(50));
    console.log('\nYour map now has redlining AND gang territory overlays!');

    await browser.disconnect();

  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
