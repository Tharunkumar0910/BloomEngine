const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// Helper to parse CSV and return raw questions
function parseRawQuestions() {
  const csvPath = path.join(__dirname, '../manual_review.csv');
  const content = fs.readFileSync(csvPath, 'utf8');
  const lines = content.split('\n');
  const questions = [];
  
  // Skip header, parse lines
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    
    // Parse comma separated values, handling quotes
    const cols = [];
    let current = '';
    let inQuotes = false;
    for (let j = 0; j < line.length; j++) {
      const char = line[j];
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        cols.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    cols.push(current);
    
    if (cols.length >= 2 && cols[0]) {
      questions.push(cols[0]);
    }
  }
  return questions.slice(0, 100);
}

// Generate the 100 mock processed results
function generateMockResults(rawQuestions) {
  return rawQuestions.map((q, idx) => {
    // Alternate difficulties and statuses for testing badges
    const difficulty = idx % 3 === 0 ? 'Easy' : (idx % 3 === 1 ? 'Medium' : 'Hard');
    const status = idx % 4 === 0 ? 'Verified' : (idx % 4 === 1 ? 'Approved' : (idx % 4 === 2 ? 'Needs Review' : 'Rejected'));
    const bloom = idx % 6 === 0 ? 'Remember' : (idx % 6 === 1 ? 'Understand' : (idx % 6 === 2 ? 'Apply' : (idx % 6 === 3 ? 'Analyze' : (idx % 6 === 4 ? 'Evaluate' : 'Create'))));
    
    return {
      id: idx + 1,
      question: q + ` (Processed #${idx + 1})`,
      original_question: q,
      bloom_level: bloom,
      difficulty: difficulty,
      confidence: (90 + (idx % 10)).toFixed(2),
      explanation: `This is a mock validation explanation for question #${idx + 1}.`,
      timestamp: '2026-07-17 12:00:00',
      status: status,
      previous_classification: null,
      variants: [],
      notes: '',
      tags: ['MockTag', `Tag-${bloom}`]
    };
  });
}

test.describe('Bulk Processing Pagination & Structure Audit', () => {
  test('Upload file, process 100 questions, and verify pagination layout & structure', async ({ page }) => {
    test.setTimeout(120000); // 2 minutes
    
    // Register console event listeners
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error(`[Browser Error] ${msg.text()}`);
      } else {
        console.log(`[Browser Console] ${msg.text()}`);
      }
    });

    page.on('pageerror', err => {
      console.error(`[Browser Exception] ${err.message}`);
    });
    
    const rawQuestions = parseRawQuestions();
    const mockResults = generateMockResults(rawQuestions);
    
    console.log(`--- Intercepting API calls for ${rawQuestions.length} questions ---`);
    
    // Route /parse-upload
    await page.route('**/parse-upload', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          questions: rawQuestions,
          filename: 'manual_review.csv'
        })
      });
    });
    
    // Route /upload-batch
    await page.route('**/upload-batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: 'mock-session-123'
        })
      });
    });
    
    // Route /start-batch/*
    await page.route('**/start-batch/mock-session-123', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'started'
        })
      });
    });
    
    // Route /batch-status/*
    let requestCount = 0;
    await page.route('**/batch-status/mock-session-123', async (route) => {
      requestCount++;
      // Simulate progress
      const isCompleted = requestCount >= 2;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: isCompleted ? 'COMPLETED' : 'PROCESSING',
          processed: isCompleted ? 100 : 50,
          total: 100,
          speed: '25.0',
          eta: isCompleted ? '0' : '2',
          results: isCompleted ? mockResults : mockResults.slice(0, 50)
        })
      });
    });
    
    // Go to home page
    await page.goto('http://127.0.0.1:5000/');
    
    // Navigate to Bulk Processing
    await page.click('a[data-target="view-batch"]');
    await page.waitForSelector('#view-batch', { state: 'visible' });
    
    // Select dummy file to trigger upload input
    console.log('Uploading mock file...');
    const demoFilePath = path.join(__dirname, 'demo.txt');
    await page.setInputFiles('input[type="file"]', demoFilePath);
    
    // Click upload
    const uploadBtn = page.locator('#uploadBtn');
    await expect(uploadBtn).toBeEnabled();
    await uploadBtn.click();
    
    // Wait for the preview table
    await page.waitForSelector('#previewTbody tr', { state: 'visible' });
    const previewCount = await page.locator('#previewTbody tr').count();
    console.log(`Preview shows ${previewCount} questions`);
    expect(previewCount).toBe(100);
    
    // Click Start Processing
    const startBtn = page.locator('#btnStartProcessingPreview');
    await expect(startBtn).toBeEnabled();
    await startBtn.click();
    
    // Wait for batchResultsSection to be visible and have rows
    await page.waitForSelector('#batchResultsSection', { state: 'visible' });
    await page.waitForSelector('#resultsTbody tr', { state: 'visible' });
    
    // Wait for COMPLETED status
    await page.waitForFunction(() => {
      const btn = document.getElementById('btnStopBatch');
      return btn && btn.textContent.includes('Completed');
    }, { timeout: 10000 });
    
    console.log('Processing completed!');
    
    // Create base path for saving screenshots inside conversation dir
    const screenshotsDir = 'C:/Users/pushp/.gemini/antigravity/brain/1c511c5d-e6c9-4b94-a8a7-a58d85c5788a';
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    }
    
    // Validate pagination and structure page by page
    for (let pageNum = 1; pageNum <= 10; pageNum++) {
      console.log(`Checking page ${pageNum}...`);
      
      // Click page number button or next page chevron
      if (pageNum > 1) {
        // Find pagination link with text content pageNum
        const pageBtn = page.locator(`#tablePagination a:has-text("${pageNum}")`).first();
        await pageBtn.click();
        await page.waitForTimeout(300);
      }
      
      // Verify exactly 10 rows
      const rows = page.locator('#resultsTbody tr');
      const count = await rows.count();
      console.log(`Page ${pageNum} has ${count} questions`);
      expect(count).toBe(10);
      
      // Check structure of questions on the page
      for (let i = 0; i < count; i++) {
        const questionText = await rows.nth(i).locator('td').nth(1).innerText();
        expect(questionText.trim().length).toBeGreaterThan(0);
        
        // Ensure difficulty and status badges render successfully
        const statusBadge = await rows.nth(i).locator('td').nth(2).innerText();
        const diffBadge = await rows.nth(i).locator('td').nth(3).innerText();
        expect(statusBadge.length).toBeGreaterThan(0);
        expect(diffBadge.length).toBeGreaterThan(0);
      }
      
      // Save screenshot of the table view
      const screenshotPath = path.join(screenshotsDir, `page_${pageNum}_table.png`);
      await page.screenshot({ path: screenshotPath });
      console.log(`Saved screenshot for Page ${pageNum} Table to: ${screenshotPath}`);
      
      // Click the first question cell on this page to open detail drawer
      console.log(`Opening drawer for first question on page ${pageNum}...`);
      const firstRowQuestionCell = rows.nth(0).locator('td').nth(1);
      await firstRowQuestionCell.click();
      
      // Verify drawer structure
      const drawer = page.locator('#questionDetailDrawer');
      // Wait for drawer to slide open (transition)
      await page.waitForTimeout(400);
      await expect(drawer).toBeVisible();
      
      const drawerQuestion = await page.locator('#drawerQuestion').innerText();
      expect(drawerQuestion.trim().length).toBeGreaterThan(0);
      
      // Save screenshot of the drawer view
      const drawerScreenshotPath = path.join(screenshotsDir, `page_${pageNum}_drawer.png`);
      await page.screenshot({ path: drawerScreenshotPath });
      console.log(`Saved drawer screenshot for Page ${pageNum} to: ${drawerScreenshotPath}`);
      
      // Close drawer
      const closeBtn = page.locator('#closeDrawerBtn');
      await closeBtn.click();
      await page.waitForTimeout(400);
    }
    
    console.log('--- ALL PAGINATION & STRUCTURE AUDIT CHECKS PASSED SUCCESSFULLY ---');
  });
});
