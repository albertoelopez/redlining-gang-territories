const puppeteer = require('puppeteer-core');
const path = require('path');

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

async function main() {
  console.log('='.repeat(50));
  console.log('Importing LA Gang Territories (Retry)');
  console.log('='.repeat(50));

  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:9222',
    defaultViewport: null,
  });

  const pages = await browser.pages();
  const page = pages[0];
  console.log(`Connected! Page: ${await page.title()}`);

  await sleep(2000);

  // Click Add layer
  console.log('\nClicking "Add layer"...');
  await clickByText(page, 'Add layer');
  await sleep(2000);

  // Click Import
  console.log('Clicking "Import"...');
  await clickByText(page, 'Import');
  await sleep(3000);

  // Find picker iframe
  console.log('Looking for Picker iframe...');
  let pickerFrame = null;
  for (const frame of page.frames()) {
    if (frame.url().includes('docs.google.com/picker')) {
      pickerFrame = frame;
      console.log('✓ Found Picker iframe');
      break;
    }
  }

  if (!pickerFrame) {
    console.log('✗ Picker not found');
    await browser.disconnect();
    return;
  }

  await sleep(2000);

  // Find and use file input
  const fileInput = await pickerFrame.$('input[type="file"]');
  if (fileInput) {
    console.log('✓ Found file input');
    const filePath = path.join(KML_DIR, 'la_gang_territories.kml');
    console.log(`Uploading: ${filePath}`);
    await fileInput.uploadFile(filePath);
    console.log('✓ File sent to upload');

    // Just wait - don't try to interact with the frame again
    console.log('Waiting 30 seconds for processing (large file)...');
    await sleep(30000);

    console.log('✓ Done waiting - check your map!');
  } else {
    console.log('✗ File input not found');
  }

  await browser.disconnect();
  console.log('\nDisconnected. Check Chrome to see if LA imported.');
}

main().catch(console.error);
