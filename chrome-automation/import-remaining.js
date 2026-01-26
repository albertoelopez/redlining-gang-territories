const puppeteer = require('puppeteer-core');
const path = require('path');

const KML_DIR = 'D:\\AI_Projects\\chrome-automation-mcp';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function clickByText(page, text) {
  return await page.evaluate((searchText) => {
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
}

async function importFile(page, filePath, layerName) {
  console.log(`\nImporting: ${layerName}`);

  console.log('  Adding layer...');
  await clickByText(page, 'Add layer');
  await sleep(3000);

  console.log('  Opening import dialog...');
  await clickByText(page, 'Import');
  await sleep(4000);

  let pickerFrame = null;
  for (const frame of page.frames()) {
    if (frame.url().includes('docs.google.com/picker')) {
      pickerFrame = frame;
      break;
    }
  }

  if (!pickerFrame) {
    console.log('  ✗ Picker not found');
    return false;
  }

  const fileInput = await pickerFrame.$('input[type="file"]');
  if (fileInput) {
    console.log('  Uploading...');
    await fileInput.uploadFile(filePath);

    console.log('  Processing (30s)...');
    await sleep(30000);

    console.log(`  ✓ ${layerName} done`);
    return true;
  }

  console.log('  ✗ File input not found');
  return false;
}

async function main() {
  console.log('='.repeat(50));
  console.log('Import Remaining Gang Layers');
  console.log('='.repeat(50));

  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:9222',
    defaultViewport: null,
  });

  const page = (await browser.pages())[0];
  console.log(`Connected: ${await page.title()}`);

  await sleep(2000);

  // Central & East LA
  await importFile(
    page,
    path.join(KML_DIR, 'la_gangs_central_east_utf8.kml'),
    'Central & East LA'
  );

  await sleep(5000);

  // Inglewood & Compton
  await importFile(
    page,
    path.join(KML_DIR, 'la_gangs_inglewood_compton_utf8.kml'),
    'Inglewood & Compton'
  );

  console.log('\n' + '='.repeat(50));
  console.log('Done!');
  console.log('='.repeat(50));

  await browser.disconnect();
}

main().catch(console.error);
