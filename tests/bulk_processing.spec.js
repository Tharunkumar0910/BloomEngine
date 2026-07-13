const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe.serial('Bulk Processing Interactive QA Audit', () => {
  let consoleErrors = [];
  let consoleWarnings = [];
  let pageExceptions = [];
  let failedRequests = [];
  let processingTimeMs = 0;
  let renderingTimeMs = 0;

  test('E2E Processing Flow', async ({ page }) => {
    test.setTimeout(900000); // 15 minutes total timeout for manual upload + processing

    // Listen to console events
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      } else if (msg.type() === 'warning') {
        consoleWarnings.push(msg.text());
      }
    });

    page.on('pageerror', err => {
      pageExceptions.push(err.message);
    });

    page.on('requestfailed', request => {
      failedRequests.push({
        url: request.url(),
        errorText: request.failure().errorText || 'Unknown error'
      });
    });

    // ==========================================
    // STEP 1: Page Load & Initial Check
    // ==========================================
    console.log('--- STEP 1: INITIAL PAGE LOAD ---');
    await page.goto('/');

    // Navigate to Bulk Processing
    await page.click('a[data-target="view-batch"]');
    await page.waitForSelector('#view-batch', { state: 'visible' });

    // Verify initial layout elements are visible
    await expect(page.locator('#dropZone')).toBeVisible();
    await expect(page.locator('#uploadBtn')).toBeVisible();
    await expect(page.locator('#uploadBtn')).toBeDisabled(); // Initially disabled

    console.log('Initial page check complete. No console errors yet:', consoleErrors.length === 0);

    // Save initial check stats
    fs.writeFileSync(path.join(__dirname, '../tests/initial_check.json'), JSON.stringify({
      consoleErrors,
      consoleWarnings,
      pageExceptions,
      failedRequests
    }, null, 2));

    console.log('WAITING_FOR_USER_UPLOAD');
    // Automate file selection if the test is running programmatically and tests/demo.txt exists
    const demoFilePath = path.join(__dirname, 'demo.txt');
    if (fs.existsSync(demoFilePath)) {
      console.log('Found demo.txt, uploading automatically...');
      await page.setInputFiles('input[type="file"]', demoFilePath);
      // Wait for upload button to be enabled and click it
      const uploadBtn = page.locator('#uploadBtn');
      await expect(uploadBtn).toBeEnabled();
      await uploadBtn.click();
    }

    // Wait for the preview table to be populated
    await page.waitForSelector('#previewTbody tr', { timeout: 60000 });

    // ==========================================
    // STEP 2: Preview Verification
    // ==========================================
    console.log('--- STEP 2: PREVIEW VERIFICATION ---');

    // Verify file name display
    const fileName = await page.locator('#fileNameDisplay').innerText().catch(() => 'Unknown');
    console.log('Uploaded File Name:', fileName);

    // Fetch parsed questions from the preview table
    const previewRows = await page.locator('#previewTbody tr').all();
    console.log(`Number of questions in preview: ${previewRows.length}`);

    const questionsText = [];
    let hasDuplicates = false;
    let hasTruncated = false;
    let hasEncodingIssues = false;

    for (const row of previewRows) {
      const text = await row.locator('.preview-text').innerText();
      if (questionsText.includes(text)) {
        hasDuplicates = true;
      }
      questionsText.push(text);

      // Check for potential encoding issue or truncation indicators
      if (text.includes('') || text.includes('undefined')) {
        hasEncodingIssues = true;
      }
      if (text.trim().length < 5) {
        hasTruncated = true;
      }
    }

    console.log('Extracted Questions Count:', questionsText.length);
    console.log('Duplicate questions found:', hasDuplicates);
    console.log('Encoding issues found:', hasEncodingIssues);
    console.log('Truncated questions found:', hasTruncated);

    // Save step 2 verification results
    fs.writeFileSync(path.join(__dirname, '../tests/preview_check.json'), JSON.stringify({
      fileName,
      questionCount: previewRows.length,
      questions: questionsText,
      hasDuplicates,
      hasEncodingIssues,
      hasTruncated
    }, null, 2));

    // ==========================================
    // STEP 3: Start Processing & Wait
    // ==========================================
    console.log('--- STEP 3: PROCESSING PIPELINE ---');
    const startProcessingBtn = page.locator('#btnStartProcessingPreview');
    await expect(startProcessingBtn).toBeVisible();

    const processingStartTime = Date.now();
    await startProcessingBtn.click();

    // Verify progress panel and stats row appear
    await expect(page.locator('#liveProgressPanel')).toBeVisible();
    await expect(page.locator('#liveStatsRow')).toBeVisible();

    // Wait until processing finishes by waiting for '#btnStopBatch' to be disabled or show Completed/Stopped
    const stopBatchBtn = page.locator('#btnStopBatch');
    await expect(stopBatchBtn).toBeDisabled({ timeout: 600000 }); // Wait up to 10 mins

    const processingEndTime = Date.now();
    processingTimeMs = processingEndTime - processingStartTime;
    console.log(`Processing completed in ${processingTimeMs} ms.`);

    // Verify results table rendered
    const renderingStartTime = Date.now();
    await expect(page.locator('#batchResultsSection')).toBeVisible();
    await expect(page.locator('#resultsTbody tr').first()).toBeVisible();
    const renderingEndTime = Date.now();
    renderingTimeMs = renderingEndTime - renderingStartTime;

    // ==========================================
    // STEP 4: Processed Results Verification
    // ==========================================
    console.log('--- STEP 4: PROCESSED QUESTIONS VERIFICATION ---');
    const resultRows = await page.locator('#resultsTbody tr').all();
    console.log(`Number of results in table: ${resultRows.length}`);

    let processedResults = [];
    for (let i = 0; i < Math.min(resultRows.length, 10); i++) { // Verify first 10 rows via drawer
      const row = resultRows[i];
      const questionText = await row.locator('td:nth-child(2)').innerText();
      const statusText = await row.locator('td:nth-child(3)').innerText();
      const difficultyText = await row.locator('td:nth-child(4)').innerText();

      // Open detail drawer for this row to verify bloom level, confidence, and explanation
      await row.locator('td:nth-child(2)').click();
      await page.waitForSelector('#questionDetailDrawer', { state: 'visible' });

      const drawerId = await page.locator('#drawerQuestionId').innerText();
      const drawerBloom = await page.locator('#drawerBloom').innerText();
      const drawerDiff = await page.locator('#drawerDiff').innerText();
      const drawerConfText = await page.locator('#drawerConfText').innerText();
      const drawerExplanation = await page.locator('#drawerExplanation').innerHTML();

      processedResults.push({
        id: drawerId,
        question: questionText,
        status: statusText,
        difficulty: difficultyText,
        bloomLevel: drawerBloom,
        confidence: drawerConfText,
        explanation: drawerExplanation
      });

      // Close drawer
      await page.click('#closeDrawerBtn');
      await expect(page.locator('#questionDetailDrawer')).toHaveClass(/translate-x-full/);
    }

    fs.writeFileSync(path.join(__dirname, '../tests/processed_results.json'), JSON.stringify({
      processingTimeMs,
      renderingTimeMs,
      processedResults
    }, null, 2));

    // ==========================================
    // STEP 5: Interactive UI Actions Testing
    // ==========================================
    console.log('--- STEP 5: INTERACTIVE ACTIONS ---');
    
    // 5.1 Search
    const searchInput = page.locator('#searchTable');
    if (await searchInput.isVisible()) {
      await searchInput.fill(questionsText[0]);
      await page.waitForTimeout(500); // Wait for filter
      const filteredRowsCount = await page.locator('#resultsTbody tr').count();
      console.log(`Search for first question filtered to ${filteredRowsCount} rows.`);
      await searchInput.fill(''); // Clear search
      await page.waitForTimeout(500);
    }

    // 5.2 Filter by Status
    const statusFilter = page.locator('#filterStatus');
    if (await statusFilter.isVisible()) {
      await statusFilter.selectOption('Needs Review');
      await page.waitForTimeout(500);
      const filteredCount = await page.locator('#resultsTbody tr').count();
      console.log(`Filter by Needs Review returned ${filteredCount} rows.`);
      await statusFilter.selectOption(''); // Clear filter
      await page.waitForTimeout(500);
    }

    // 5.3 Export buttons
    let exportSucceeded = true;
    const downloadPromiseAllCSV = page.waitForEvent('download').catch(() => null);
    await page.click('button:has-text("Export All")');
    await page.click('#btnExportAllCSV');
    const downloadCSV = await downloadPromiseAllCSV;
    if (downloadCSV) {
      console.log('Export All CSV Downloaded successfully.');
    } else {
      console.log('Export All CSV Download Failed/Timeout');
      exportSucceeded = false;
    }

    // 5.4 Open Drawer & edit components
    if (resultRows.length > 0) {
      await resultRows[0].locator('td:nth-child(2)').click();
      await page.waitForSelector('#questionDetailDrawer', { state: 'visible' });

      // Change status select
      await page.locator('#drawerStatusSelect').selectOption('Approved');
      await page.waitForTimeout(300);

      // Edit Notes
      await page.locator('#drawerNotes').fill('QA Test verified notes.');
      await page.waitForTimeout(300);

      // Tags test
      await page.locator('#drawerTagInput').fill('QATestTag');
      await page.click('#btnDrawerAddTag');
      await page.waitForTimeout(300);

      // Close drawer
      await page.click('#closeDrawerBtn');
      await expect(page.locator('#questionDetailDrawer')).toHaveClass(/translate-x-full/);
    }

    // 5.5 Carousel Navigation check
    const prevCarouselBtn = page.locator('#btnPrevQuestion');
    const nextCarouselBtn = page.locator('#btnNextQuestion');
    let carouselWorking = false;
    if (await nextCarouselBtn.isVisible() && !(await nextCarouselBtn.isDisabled())) {
      await nextCarouselBtn.click();
      await page.waitForTimeout(300);
      const counterText = await page.locator('#carouselCounter').innerText();
      console.log('Carousel Counter Text:', counterText);
      if (counterText.includes('2 /')) {
        carouselWorking = true;
      }
    }

    // 5.6 Delete Action (assert button is removed)
    const deleteBtn = page.locator('#resultsTbody tr button[title="Delete"]').first();
    const isDeleteBtnVisible = await deleteBtn.isVisible();
    console.log('Delete button is visible (should be false):', isDeleteBtnVisible);
    expect(isDeleteBtnVisible).toBe(false);
    let deleteSucceeded = false;

    // Check if other drawer buttons are dead UI
    const brokenButtons = [];
    if (resultRows.length > 0) {
      await resultRows[0].locator('td:nth-child(2)').click();
      await page.waitForSelector('#questionDetailDrawer', { state: 'visible' });
    }
    
    const drawerAnalyticsBtn = page.locator('#btnDrawerAnalytics');
    if (await drawerAnalyticsBtn.isVisible()) {
      await drawerAnalyticsBtn.click();
      await page.waitForSelector('#view-analytics', { state: 'visible' });
      await page.click('a[data-target="view-batch"]');
      await page.waitForSelector('#view-batch', { state: 'visible' });
    } else {
      brokenButtons.push('btnDrawerAnalytics');
    }

    fs.writeFileSync(path.join(__dirname, '../tests/interactive_check.json'), JSON.stringify({
      exportSucceeded,
      carouselWorking,
      deleteSucceeded,
      brokenButtons,
      consoleErrors,
      consoleWarnings,
      pageExceptions,
      failedRequests
    }, null, 2));

    console.log('--- ALL QA E2E TEST STEPS FINISHED ---');
  });
});
