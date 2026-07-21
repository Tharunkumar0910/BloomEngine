const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function run() {
  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Log all console messages
  page.on('console', msg => {
    console.log(`[BROWSER CONSOLE] [${msg.type()}] ${msg.text()}`);
  });

  // Log all page exceptions
  page.on('pageerror', err => {
    console.error(`[BROWSER EXCEPTION] ${err.stack}`);
  });

  // Log all network requests and responses
  page.on('request', req => {
    console.log(`[NETWORK REQ] ${req.method()} ${req.url()}`);
  });
  page.on('response', res => {
    console.log(`[NETWORK RES] ${res.status()} ${res.url()}`);
  });

  console.log('Navigating to http://127.0.0.1:5000/ ...');
  await page.goto('http://127.0.0.1:5000/');
  await page.waitForTimeout(2000);

  // Click on Bulk Processing tab
  console.log('Clicking Bulk Processing tab...');
  const bulkTab = page.locator('a:has-text("Bulk Processing")').first();
  await bulkTab.click();
  await page.waitForTimeout(1000);

  // Upload demo.txt
  console.log('Uploading demo.txt...');
  const demoFilePath = path.join(__dirname, '../tests/demo.txt');
  await page.setInputFiles('input[type="file"]', demoFilePath);

  // Click UploadBtn
  console.log('Clicking Upload button...');
  const uploadBtn = page.locator('#uploadBtn');
  await uploadBtn.click();

  // Wait for preview table
  console.log('Waiting for preview table...');
  await page.waitForSelector('#previewTbody tr', { timeout: 10000 });
  await page.waitForTimeout(1000);

  // Click Start Processing
  console.log('Clicking Start Processing...');
  const startBtn = page.locator('#btnStartProcessingPreview');
  
  // Set up dialog handler to log and dismiss any alert
  page.on('dialog', async dialog => {
    console.log(`[BROWSER DIALOG] [${dialog.type()}] Message: ${dialog.message()}`);
    await dialog.dismiss();
  });

  await startBtn.click();
  console.log('Waiting for batch processing to complete...');
  const stopBatchBtn = page.locator('#btnStopBatch');
  for (let i = 0; i < 60; i++) {
    const disabled = await stopBatchBtn.isDisabled();
    if (disabled) {
      break;
    }
    await page.waitForTimeout(1000);
  }
  console.log('Batch processing completed!');
  await page.waitForTimeout(2000);

  console.log('Closing browser...');
  await browser.close();
}

run().catch(err => {
  console.error('Test script failed:', err);
});
