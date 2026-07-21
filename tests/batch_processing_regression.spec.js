const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

test.describe.serial('Batch Processing UI Regression & Performance Tests', () => {
  let consoleErrors = [];
  let pageExceptions = [];
  let perfLogs = [];

  test.beforeEach(({ page }) => {
    consoleErrors = [];
    pageExceptions = [];
    perfLogs = [];

    page.on('console', msg => {
      const text = msg.text();
      if (msg.type() === 'error') {
        consoleErrors.push(text);
      }
      if (text.includes('[PERF-FRONTEND]') || text.includes('[PERF-WARNING]')) {
        perfLogs.push(text);
      }
    });

    page.on('pageerror', err => {
      pageExceptions.push(err.message);
    });
  });

  test('Batch processing live incremental updates, post-completion pagination, dashboard & chart rendering', async ({ page }) => {
    test.setTimeout(60000);

    // Create 35 mock questions for robust pagination testing (10/20/30 per page)
    const mockQuestions = Array.from({ length: 35 }, (_, i) => ({
      id: i + 1,
      question: `Sample Test Question #${i + 1} for taxonomy classification`,
      original_question: `Sample Test Question #${i + 1} for taxonomy classification`,
      bloom_level: ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'][i % 6],
      difficulty: ['Easy', 'Medium', 'Hard'][i % 3],
      confidence: (85 + (i % 15)).toFixed(2),
      explanation: `Mock academic explanation for question ${i + 1}`,
      timestamp: '2026-07-20 10:00:00',
      status: i % 2 === 0 ? 'Verified' : 'Needs Review',
      previous_classification: null,
      variants: [],
      notes: '',
      tags: []
    }));

    // Mock backend APIs
    await page.route('**/parse-upload', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          questions: mockQuestions.map(q => q.question),
          filename: 'test_questions.txt'
        })
      });
    });

    await page.route('**/upload-batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ session_id: 'mock-reg-session-1' })
      });
    });

    await page.route('**/start-batch/*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'started' })
      });
    });

    let statusPollCount = 0;
    await page.route('**/batch-status/mock-reg-session-1', async (route) => {
      statusPollCount++;
      let processed = 0;
      let status = 'PROCESSING';

      if (statusPollCount === 1) {
        processed = 5;
      } else if (statusPollCount === 2) {
        processed = 15;
      } else {
        processed = 35;
        status = 'COMPLETED';
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: status,
          processed: processed,
          total: 35,
          speed: '5.0',
          eta: status === 'COMPLETED' ? '0' : '4',
          results: mockQuestions.slice(0, processed)
        })
      });
    });

    await page.route('**/batch-history', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            session_id: 'mock-reg-session-1',
            filename: 'test_questions.txt',
            upload_time: '2026-07-20T10:00:00Z',
            total_questions: 35,
            completed_questions: 35,
            status: 'COMPLETED',
            easy_count: 12,
            medium_count: 12,
            hard_count: 11,
            bloom_counts: { Remember: 6, Understand: 6, Apply: 6, Analyze: 6, Evaluate: 6, Create: 5 },
            avg_confidence: 91.5
          }
        ])
      });
    });

    // 1. Navigate to main page
    await page.goto('http://127.0.0.1:5000/');
    await page.click('a[data-target="view-batch"]');
    await page.waitForSelector('#view-batch', { state: 'visible' });

    // Upload demo file
    const demoFilePath = path.join(__dirname, 'demo.txt');
    await page.setInputFiles('input[type="file"]', demoFilePath);

    const uploadBtn = page.locator('#uploadBtn');
    await expect(uploadBtn).toBeEnabled();
    await uploadBtn.click();

    await page.waitForSelector('#previewTbody tr', { state: 'visible' });
    const startBtn = page.locator('#btnStartProcessingPreview');
    await expect(startBtn).toBeEnabled();
    await startBtn.click();

    // 2. Test Incremental Updates and Live Pagination during processing
    await page.waitForSelector('#batchResultsSection', { state: 'visible' });

    // Check progress bar elements are updated
    await expect(page.locator('#progressText')).toContainText('Processing:');

    // Wait for poll #2 where 15 questions have been classified
    await page.waitForFunction(() => {
      const el = document.getElementById('tablePaginationInfo');
      return el && el.textContent.includes('Showing 1 to 10 of 15');
    }, { timeout: 10000 });

    // Confirm Page 1 displays EXACTLY 10 rows without requiring user click
    const livePage1RowCount = await page.locator('#resultsTbody tr').count();
    expect(livePage1RowCount).toBe(10);

    // Wait for COMPLETED status
    await page.waitForFunction(() => {
      const btn = document.getElementById('btnStopBatch');
      return btn && btn.textContent.includes('Completed');
    }, { timeout: 15000 });

    // 3. Verify Pagination after Completion (10/20/30 rows per page)
    const perPageSelect = page.locator('#itemsPerPageSelect');
    await expect(perPageSelect).toBeVisible();

    // Default or select 10 per page
    await perPageSelect.selectOption('10');
    await page.waitForTimeout(300);
    let rowsCount = await page.locator('#resultsTbody tr').count();
    expect(rowsCount).toBe(10);
    let pagInfo = await page.locator('#tablePaginationInfo').innerText();
    expect(pagInfo).toContain('Showing 1 to 10 of 35');

    // Select 20 per page
    await perPageSelect.selectOption('20');
    await page.waitForTimeout(300);
    rowsCount = await page.locator('#resultsTbody tr').count();
    expect(rowsCount).toBe(20);
    pagInfo = await page.locator('#tablePaginationInfo').innerText();
    expect(pagInfo).toContain('Showing 1 to 20 of 35');

    // Select 50 per page (all 35 items fit on page 1)
    await perPageSelect.selectOption('50');
    await page.waitForTimeout(300);
    rowsCount = await page.locator('#resultsTbody tr').count();
    expect(rowsCount).toBe(35);
    pagInfo = await page.locator('#tablePaginationInfo').innerText();
    expect(pagInfo).toContain('Showing 1 to 35 of 35');

    // Reset to 10 per page for Next/Prev test
    await perPageSelect.selectOption('10');
    await page.waitForTimeout(300);

    // 4. Verify Next / Previous Pagination Navigation
    const nextBtn = page.locator('#tablePagination a').last();
    await nextBtn.click();
    await page.waitForTimeout(300);
    pagInfo = await page.locator('#tablePaginationInfo').innerText();
    expect(pagInfo).toContain('Showing 11 to 20 of 35');

    const prevBtn = page.locator('#tablePagination a').first();
    await prevBtn.click();
    await page.waitForTimeout(300);
    pagInfo = await page.locator('#tablePaginationInfo').innerText();
    expect(pagInfo).toContain('Showing 1 to 10 of 35');

    // 5. Verify Dashboard & Charts Rendered After Completion
    await page.click('a[data-target="view-dashboard"]');
    await page.waitForSelector('#view-dashboard', { state: 'visible' });

    // Check KPI cards
    const dashTotal = await page.locator('#dashTotal').innerText();
    expect(dashTotal.trim()).not.toBe('0');

    // Check chart canvases exist and are rendered
    await expect(page.locator('#dashBloomChart')).toBeVisible();
    await expect(page.locator('#dashDistPieChart')).toBeVisible();

    // 6. Verify zero console errors
    console.log('Console Errors captured during test:', consoleErrors);
    console.log('Page Exceptions captured during test:', pageExceptions);
    expect(consoleErrors.length).toBe(0);
    expect(pageExceptions.length).toBe(0);
  });
});
