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
  await sleep(2000);

  console.log('  Opening import dialog...');
  await clickByText(page, 'Import');
  await sleep(3000);

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

    console.log('  Processing (20s)...');
    await sleep(20000);

    console.log(`  ✓ ${layerName} done`);
    return true;
  }

  console.log('  ✗ File input not found');
  return false;
}

async function main() {
  console.log('='.repeat(50));
  console.log('Import All Gang Territories (Merged + New)');
  console.log('='.repeat(50));

  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:9222',
    defaultViewport: null,
  });

  const page = (await browser.pages())[0];
  console.log(`Connected: ${await page.title()}`);

  await sleep(2000);

  const files = [
    { file: 'la_gangs_central_east.kml', name: 'Central & East LA (280)' },
    { file: 'la_gangs_south_la.kml', name: 'South Los Angeles (344)' },
    { file: 'la_gangs_southbay_compton.kml', name: 'South Bay & Compton (231)' },
    { file: 'la_gangs_sfv.kml', name: 'San Fernando Valley (124)' },
    { file: 'la_gangs_sgv.kml', name: 'San Gabriel & IE (370)' },
    { file: 'la_gangs_longbeach.kml', name: 'Long Beach (65)' },
  ];

  for (const { file, name } of files) {
    await importFile(page, path.join(KML_DIR, file), name);
    await sleep(3000);
  }

  console.log('\n' + '='.repeat(50));
  console.log('Done! All gang territories imported.');
  console.log('='.repeat(50));

  await browser.disconnect();
}

main().catch(console.error);
