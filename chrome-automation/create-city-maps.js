const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CITIES = [
  'chicago',
  'detroit',
  'philadelphia',
  'cleveland',
  'st_louis',
  'baltimore',
  'pittsburgh',
  'san_francisco',
  'new_orleans',
  'atlanta',
  'new_york_city'
];

const PROJECT_ROOT = 'D:\\AI_Projects\\redlining_project';
const GANG_DIR = path.join(PROJECT_ROOT, 'gang_territories');

function getCityDisplayName(city) {
  const names = {
    'chicago': 'Chicago',
    'detroit': 'Detroit',
    'philadelphia': 'Philadelphia',
    'cleveland': 'Cleveland',
    'st_louis': 'St. Louis',
    'baltimore': 'Baltimore',
    'pittsburgh': 'Pittsburgh',
    'san_francisco': 'San Francisco',
    'new_orleans': 'New Orleans',
    'atlanta': 'Atlanta',
    'new_york_city': 'New York City'
  };
  return names[city] || city;
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitForSelector(page, selector, timeout = 10000) {
  try {
    await page.waitForSelector(selector, { timeout });
    return true;
  } catch {
    return false;
  }
}

async function clickByText(page, text, partial = false) {
  const clicked = await page.evaluate((searchText, isPartial) => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while (node = walker.nextNode()) {
      const nodeText = node.textContent.trim();
      const matches = isPartial ? nodeText.includes(searchText) : nodeText === searchText;
      if (matches) {
        const parent = node.parentElement;
        if (parent && parent.offsetParent !== null) {
          parent.click();
          return true;
        }
      }
    }
    return false;
  }, text, partial);
  return clicked;
}

async function uploadKMLFile(page, filePath, layerName) {
  console.log(`    Uploading: ${layerName}`);
  console.log(`    File: ${filePath}`);

  // Click "Add layer"
  await sleep(1500);
  const addedLayer = await clickByText(page, 'Add layer');
  if (addedLayer) {
    console.log('    ✓ Clicked "Add layer"');
    await sleep(2000);
  }

  // Click "Import"
  const clickedImport = await clickByText(page, 'Import');
  if (!clickedImport) {
    console.log('    ✗ Could not find Import button');
    return false;
  }
  console.log('    ✓ Clicked "Import"');
  await sleep(3000);

  // Find the Google Picker iframe
  const frames = page.frames();
  let pickerFrame = null;

  for (const frame of frames) {
    const url = frame.url();
    if (url.includes('docs.google.com/picker')) {
      pickerFrame = frame;
      break;
    }
  }

  if (!pickerFrame) {
    // Try to find any frame with file input
    for (const frame of frames) {
      try {
        const hasFileInput = await frame.evaluate(() => {
          return document.querySelector('input[type="file"]') !== null;
        });
        if (hasFileInput) {
          pickerFrame = frame;
          break;
        }
      } catch (e) {
        // Frame might not be accessible
      }
    }
  }

  if (!pickerFrame) {
    // Try main page file input
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.uploadFile(filePath);
      await sleep(5000);
      console.log(`    ✓ Uploaded via main page input`);
      return true;
    }
    console.log('    ✗ No picker frame found');
    return false;
  }

  // Find and use file input in picker
  try {
    await sleep(2000);
    const fileInputHandle = await pickerFrame.$('input[type="file"]');

    if (fileInputHandle) {
      await fileInputHandle.uploadFile(filePath);
      console.log('    ✓ File uploaded, waiting for processing...');
      await sleep(8000); // KML files can take time to process

      // Try to click any confirmation button
      await pickerFrame.evaluate(() => {
        const selectBtn = document.querySelector('[data-action="select"], .picker-actions button');
        if (selectBtn) selectBtn.click();
      });

      await sleep(3000);
      console.log(`    ✓ Layer imported: ${layerName}`);
      return true;
    }
  } catch (error) {
    console.log('    ✗ Error uploading:', error.message);
  }

  return false;
}

async function createCityMap(page, city) {
  const displayName = getCityDisplayName(city);
  const holcFile = path.join(PROJECT_ROOT, `${city}_holc.kml`);
  const gangFile = path.join(GANG_DIR, `${city}_gangs.kml`);

  console.log(`\n${'='.repeat(60)}`);
  console.log(`Creating map for: ${displayName}`);
  console.log('='.repeat(60));

  // Check files exist
  if (!fs.existsSync(holcFile)) {
    console.log(`  ✗ HOLC file not found: ${holcFile}`);
    return null;
  }
  if (!fs.existsSync(gangFile)) {
    console.log(`  ✗ Gang file not found: ${gangFile}`);
    return null;
  }

  // Navigate to Google My Maps
  console.log('\n  Navigating to Google My Maps...');
  await page.goto('https://www.google.com/maps/d/create', { waitUntil: 'networkidle2' });
  await sleep(3000);

  // Set map title
  console.log('  Setting map title...');
  try {
    // Click on "Untitled map" to edit title
    const clickedTitle = await clickByText(page, 'Untitled map');
    if (clickedTitle) {
      await sleep(1000);

      // Find and fill the title input
      const titleInput = await page.$('input[aria-label="Map title"]');
      if (titleInput) {
        await titleInput.click({ clickCount: 3 }); // Select all
        await titleInput.type(`${displayName} - Redlining & Gang Territories`);

        // Find and fill description
        const descInput = await page.$('textarea[aria-label="Map description"]');
        if (descInput) {
          await descInput.type(`HOLC Redlining (1939) and modern gang territories in ${displayName}`);
        }

        // Save
        await clickByText(page, 'Save');
        await sleep(2000);
        console.log('  ✓ Map title set');
      }
    }
  } catch (e) {
    console.log('  Could not set title, continuing...');
  }

  // Import HOLC redlining layer
  console.log('\n  Importing HOLC redlining data...');
  const holcSuccess = await uploadKMLFile(page, holcFile, `${displayName} HOLC (1939)`);

  if (!holcSuccess) {
    console.log('  ✗ Failed to import HOLC layer');
  }

  await sleep(2000);

  // Import gang territories layer
  console.log('\n  Importing gang territories...');
  const gangSuccess = await uploadKMLFile(page, gangFile, `${displayName} Gang Territories`);

  if (!gangSuccess) {
    console.log('  ✗ Failed to import gang layer');
  }

  await sleep(2000);

  // Get the map URL
  const mapUrl = page.url();
  console.log(`\n  ✓ Map created: ${mapUrl}`);

  return mapUrl;
}

async function main() {
  // Get city from command line args, or do all
  const args = process.argv.slice(2);
  let citiesToProcess = CITIES;

  if (args.length > 0 && args[0] !== '--all') {
    citiesToProcess = args.filter(arg => CITIES.includes(arg.toLowerCase()));
    if (citiesToProcess.length === 0) {
      console.log('Usage: node create-city-maps.js [city1] [city2] ... or --all');
      console.log('Available cities:', CITIES.join(', '));
      process.exit(1);
    }
  }

  console.log('='.repeat(60));
  console.log('Google My Maps - City Map Creator');
  console.log('='.repeat(60));
  console.log(`\nCities to process: ${citiesToProcess.map(getCityDisplayName).join(', ')}`);

  try {
    console.log('\nConnecting to Chrome...');

    // Try localhost first (Windows), then WSL2 host IP
    let browser;
    const urls = ['http://127.0.0.1:9222', 'http://172.23.160.1:9222'];

    for (const url of urls) {
      try {
        console.log(`  Trying ${url}...`);
        browser = await puppeteer.connect({
          browserURL: url,
          defaultViewport: null,
        });
        console.log(`  ✓ Connected via ${url}`);
        break;
      } catch (e) {
        console.log(`  ✗ ${url} failed`);
      }
    }

    if (!browser) {
      throw new Error('Could not connect to Chrome');
    }

    const pages = await browser.pages();
    const page = pages[0];
    console.log('✓ Connected to Chrome');

    const results = [];

    for (const city of citiesToProcess) {
      try {
        const url = await createCityMap(page, city);
        results.push({ city, url, success: !!url });

        // Pause between cities to avoid rate limiting
        if (citiesToProcess.indexOf(city) < citiesToProcess.length - 1) {
          console.log('\n  Waiting before next city...');
          await sleep(5000);
        }
      } catch (error) {
        console.log(`  ✗ Error creating map for ${city}:`, error.message);
        results.push({ city, url: null, success: false });
      }
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('SUMMARY');
    console.log('='.repeat(60));

    for (const result of results) {
      const status = result.success ? '✓' : '✗';
      const displayName = getCityDisplayName(result.city);
      console.log(`${status} ${displayName}: ${result.url || 'Failed'}`);
    }

    const successCount = results.filter(r => r.success).length;
    console.log(`\nTotal: ${successCount}/${results.length} maps created`);

    // Save results to file
    const resultsFile = path.join(PROJECT_ROOT, 'map_urls.json');
    fs.writeFileSync(resultsFile, JSON.stringify(results, null, 2));
    console.log(`\nResults saved to: ${resultsFile}`);

    await browser.disconnect();

  } catch (error) {
    console.error('Error:', error.message);
    console.log('\nMake sure Chrome is running with remote debugging:');
    console.log('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\\ChromeDebug"');
  }
}

main();
