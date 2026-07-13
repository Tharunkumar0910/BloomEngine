const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');

// Read questions
const records = parse(fs.readFileSync(path.join(__dirname, '../benchmark_questions.csv')), {
  columns: true,
  skip_empty_lines: true
});

let results = [];
let performanceLog = [];

test.describe.serial('BloomAI Benchmark Suite', () => {

  test.beforeAll(() => {
    if (!fs.existsSync(path.join(__dirname, '../playwright_failures'))) {
      fs.mkdirSync(path.join(__dirname, '../playwright_failures'));
    }
  });

  test('Warmup Run', async ({ page }) => {
    test.setTimeout(90000);
    await page.goto('/');
    
    // Navigate to Studio
    await page.click('a[data-target="view-manual"]');
    await page.waitForSelector('#manualQuestion', { state: 'visible' });

    // Submit warmup question
    await page.fill('#manualQuestion', 'What is DBMS?');
    await page.click('#btnClassify');

    // Wait for classification result
    await page.waitForSelector('#singleResultSection', { state: 'visible', timeout: 90000 });
    
    // Clear
    await page.click('#btnClear');
    // Result discarded
  });

  for (let i = 0; i < records.length; i++) {
    const record = records[i];
    const expectedBloom = record.Expected_Bloom || 'Remember';
    
    test(`Benchmark [${i+1}/${records.length}]: ${expectedBloom}`, async ({ page }) => {
      test.setTimeout(90000);
      
      await page.goto('/');
      await page.click('a[data-target="view-manual"]');
      await page.waitForSelector('#manualQuestion', { state: 'visible' });

      // In case we need to clear previous run
      await page.click('#btnClear').catch(() => {});

      await page.fill('#manualQuestion', record.Question);
      
      const startTime = Date.now();
      await page.click('#btnClassify');

      // Wait for result UI to populate and spinner to disappear
      await page.waitForSelector('#singleResultSection', { state: 'visible', timeout: 90000 });
      // Ensure the text isn't a placeholder
      await expect(page.locator('#resBloom')).not.toHaveText('-', { timeout: 90000 });

      const endTime = Date.now();
      const responseTimeMs = endTime - startTime;
      performanceLog.push(responseTimeMs);

      const predictedBloom = await page.textContent('#resBloom');
      const predictedDifficulty = await page.textContent('#resDiff');
      const confText = await page.textContent('#resConfText');
      const confidence = parseFloat(confText.replace('%', ''));
      const passFail = predictedBloom.trim() === expectedBloom.trim() ? 'PASS' : 'FAIL';

      if (passFail === 'FAIL') {
        const safeName = expectedBloom.trim() + '_' + (i+1).toString().padStart(2, '0');
        await page.screenshot({ path: path.join(__dirname, `../playwright_failures/${safeName}.png`) });
      }

      results.push({
        Question: record.Question,
        Expected_Bloom: expectedBloom,
        Predicted_Bloom: predictedBloom.trim(),
        Predicted_Difficulty: predictedDifficulty.trim(),
        Confidence: confidence,
        Pass_Fail: passFail,
        Response_Time_MS: responseTimeMs
      });
      
      await page.click('#btnClear');
    });
  }

  test.afterAll(async () => {
    // 1. Export benchmark_results.csv
    const csvHeader = 'Question,Expected_Bloom,Predicted_Bloom,Predicted_Difficulty,Confidence,Pass_Fail,Response_Time_MS\n';
    const csvRows = results.map(r => `"${r.Question.replace(/"/g, '""')}",${r.Expected_Bloom},${r.Predicted_Bloom},${r.Predicted_Difficulty},${r.Confidence},${r.Pass_Fail},${r.Response_Time_MS}`).join('\n');
    fs.writeFileSync(path.join(__dirname, '../benchmark_results.csv'), csvHeader + csvRows);

    // 2. Generate benchmark_report.json
    const levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'];
    const accReport = { overall_accuracy: 0 };
    let correctCount = 0;

    levels.forEach(lvl => {
      const targetResults = results.filter(r => r.Expected_Bloom === lvl);
      if (targetResults.length > 0) {
        const passes = targetResults.filter(r => r.Pass_Fail === 'PASS').length;
        correctCount += passes;
        accReport[`${lvl.toLowerCase()}_accuracy`] = (passes / targetResults.length) * 100;
      } else {
        accReport[`${lvl.toLowerCase()}_accuracy`] = 0;
      }
    });
    
    accReport.overall_accuracy = (correctCount / results.length) * 100;

    // Confidence Analysis
    const correctResults = results.filter(r => r.Pass_Fail === 'PASS');
    const incorrectResults = results.filter(r => r.Pass_Fail === 'FAIL');
    
    accReport.correct_predictions_avg_confidence = correctResults.length > 0 
      ? correctResults.reduce((sum, r) => sum + r.Confidence, 0) / correctResults.length : 0;
      
    accReport.incorrect_predictions_avg_confidence = incorrectResults.length > 0 
      ? incorrectResults.reduce((sum, r) => sum + r.Confidence, 0) / incorrectResults.length : 0;

    fs.writeFileSync(path.join(__dirname, '../benchmark_report.json'), JSON.stringify(accReport, null, 2));

    // 3. Generate confusion_matrix.json
    const confMatrix = {};
    levels.forEach(expected => {
      confMatrix[expected] = {};
      levels.forEach(predicted => {
        confMatrix[expected][predicted] = 0;
      });
    });

    results.forEach(r => {
      if (confMatrix[r.Expected_Bloom] !== undefined && confMatrix[r.Expected_Bloom][r.Predicted_Bloom] !== undefined) {
        confMatrix[r.Expected_Bloom][r.Predicted_Bloom] += 1;
      }
    });

    fs.writeFileSync(path.join(__dirname, '../confusion_matrix.json'), JSON.stringify(confMatrix, null, 2));

    // 4. Generate misclassification_report.json
    const misclassifications = {};
    results.forEach(r => {
      if (r.Pass_Fail === 'FAIL') {
        const key = `${r.Expected_Bloom}_to_${r.Predicted_Bloom}`;
        misclassifications[key] = (misclassifications[key] || 0) + 1;
      }
    });

    fs.writeFileSync(path.join(__dirname, '../misclassification_report.json'), JSON.stringify(misclassifications, null, 2));

    // 5. Generate performance_report.json
    if (performanceLog.length > 0) {
      const avg = performanceLog.reduce((a, b) => a + b, 0) / performanceLog.length;
      const min = Math.min(...performanceLog);
      const max = Math.max(...performanceLog);
      const total = performanceLog.reduce((a, b) => a + b, 0);

      const perfReport = {
        average_response_time_ms: avg,
        fastest_response_time_ms: min,
        slowest_response_time_ms: max,
        total_runtime_ms: total
      };

      fs.writeFileSync(path.join(__dirname, '../performance_report.json'), JSON.stringify(perfReport, null, 2));
    }
  });
});
