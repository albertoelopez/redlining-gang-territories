const puppeteer = require('puppeteer-core');
const path = require('path');

const KML_FILES = [
  { file: 'los_angeles_grade_D.kml', name: 'LA Redlined (1939)' },
  { file: 'chicago_grade_D.kml', name: 'Chicago Redlined (1939)' },
  { file: 'detroit_grade_D.kml', name: 'Detroit Redlined (1939)' },
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

async function importKML(page, filePath, layerName, isFirst) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Importing: ${layerName}`);
  console.log(`File: ${filePath}`);
  console.log('='.repeat(50));

  await sleep(1500);

  // Click Import (or Add layer first if not first file)
  if (!isFirst) {
    console.log('  Clicking "Add layer"...');
    await clickByText(page, 'Add layer');
    await sleep(2000);
  }

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
    // Try to find any iframe with file input
    for (const frame of frames) {
      try {
        const hasFileInput = await frame.evaluate(() => {
          return document.querySelector('input[type="file"]') !== null;
        });
        if (hasFileInput) {
          pickerFrame = frame;
          console.log('  ✓ Found frame with file input');
          break;
        }
      } catch (e) {
        // Frame might not be accessible
      }
    }
  }

  if (!pickerFrame) {
    console.log('  ✗ No picker frame found, trying main page file input...');

    // Try to find file input on main page (might be hidden)
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.uploadFile(filePath);
      await sleep(5000);
      console.log(`  ✓ Uploaded via main page input`);
      return true;
    }

    console.log('  ✗ Could not find file input');
    return false;
  }

  // Look for file input in the picker iframe
  console.log('  Looking for file input in picker...');

  try {
    // Wait for upload area to be ready
    await sleep(2000);

    // Find file input in picker
    const fileInputHandle = await pickerFrame.$('input[type="file"]');

    if (fileInputHandle) {
      console.log('  ✓ Found file input in picker');
      await fileInputHandle.uploadFile(filePath);
      console.log('  ✓ File uploaded, waiting for processing...');
      await sleep(5000);

      // Check if we need to click any confirmation button
      await pickerFrame.evaluate(() => {
        const selectBtn = document.querySelector('[data-action="select"], .picker-actions button');
        if (selectBtn) selectBtn.click();
      });

      await sleep(3000);
      console.log(`  ✓ Imported ${layerName}`);
      return true;
    } else {
      console.log('  File input not found in picker, trying to click upload area...');

      // Try clicking on upload area to trigger file chooser
      const uploadClicked = await pickerFrame.evaluate(() => {
        const uploadArea = document.querySelector('[data-view="upload"], .picker-upload, [class*="upload"]');
        if (uploadArea) {
          uploadArea.click();
          return true;
        }
        return false;
      });

      if (uploadClicked) {
        await sleep(2000);
        const fileInputAfterClick = await pickerFrame.$('input[type="file"]');
        if (fileInputAfterClick) {
          await fileInputAfterClick.uploadFile(filePath);
          await sleep(5000);
          console.log(`  ✓ Uploaded ${layerName}`);
          return true;
        }
      }
    }
  } catch (error) {
    console.log('  Error accessing picker:', error.message);
  }

  console.log('  ✗ Could not upload file');
  return false;
}

async function main() {
  console.log('='.repeat(50));
  console.log('Google My Maps KML Import Automation');
  console.log('='.repeat(50));

  try {
    console.log('\nConnecting to Chrome...');
    const browser = await puppeteer.connect({
      browserURL: 'http://127.0.0.1:9222',
      defaultViewport: null,
    });

    const pages = await browser.pages();
    const page = pages[0];

    console.log(`Connected! Page: ${await page.title()}`);

    await sleep(2000);

    // Import each KML file
    let successCount = 0;
    for (let i = 0; i < KML_FILES.length; i++) {
      const kml = KML_FILES[i];
      const filePath = path.join(KML_DIR, kml.file);

      const success = await importKML(page, filePath, kml.name, i === 0);
      if (success) successCount++;

      await page.screenshot({ path: `D:\\AI_Projects\\chrome-automation-mcp\\step${i + 1}.png` });
      console.log(`  Screenshot: step${i + 1}.png`);

      await sleep(2000);
    }

    console.log('\n' + '='.repeat(50));
    console.log(`DONE! ${successCount}/${KML_FILES.length} files imported`);
    console.log('='.repeat(50));

    await browser.disconnect();

  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
