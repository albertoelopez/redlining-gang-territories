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

async function main() {
  console.log('='.repeat(50));
  console.log('Import All HOLC Grades (Merged)');
  console.log('='.repeat(50));

  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:9222',
    defaultViewport: null,
  });

  const page = (await browser.pages())[0];
  console.log(`Connected: ${await page.title()}`);

  await sleep(2000);

  console.log('\nAdding layer...');
  await clickByText(page, 'Add layer');
  await sleep(2000);

  console.log('Opening import dialog...');
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
    console.log('✗ Picker not found');
    await browser.disconnect();
    return;
  }

  const fileInput = await pickerFrame.$('input[type="file"]');
  if (fileInput) {
    console.log('Uploading la_all_grades.kml (493 areas)...');
    await fileInput.uploadFile(path.join(KML_DIR, 'la_all_grades.kml'));

    console.log('Processing (15s)...');
    await sleep(15000);

    console.log('✓ Done!');
  } else {
    console.log('✗ File input not found');
  }

  await browser.disconnect();
}

main().catch(console.error);
