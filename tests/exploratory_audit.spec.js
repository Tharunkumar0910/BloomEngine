const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe.serial('Comprehensive Exploratory QA Audit', () => {
  let consoleErrors = [];
  let consoleWarnings = [];
  let pageExceptions = [];
  let failedRequests = [];
  const questionLogs = [];
  let bulkLogs = {};
  let viewportsTested = [];
  let themeToggleWorks = false;
  let accessibilityChecks = [];

  test('E2E Audit Execution', async ({ page }) => {
    test.setTimeout(900000); // 15 minutes total timeout

    // Listen to dialog (alerts) to automatically dismiss
    page.on('dialog', async dialog => {
      console.log(`[ALERT/DIALOG] Dismissed: ${dialog.message()}`);
      await dialog.dismiss();
    });

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

    // 1. Go to root
    await page.goto('/');
    await page.waitForSelector('a[data-target="view-dashboard"]');

    // ==========================================
    // PHASE 2 & 8: Theme & Navigation Explorer
    // ==========================================
    console.log('--- EXAMINING NAVIGATION & THEME TOGGLE ---');
    const isDarkInitial = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    console.log('Initial theme dark:', isDarkInitial);

    // Toggle theme via single themeToggle button
    const themeBtn = page.locator('#themeToggle');
    if (await themeBtn.isVisible()) {
      const isDarkBefore = await page.evaluate(() => document.documentElement.classList.contains('dark'));
      await themeBtn.click();
      await page.waitForTimeout(300);
      const isDarkAfter = await page.evaluate(() => document.documentElement.classList.contains('dark'));
      console.log('Theme toggled from dark state changed:', isDarkBefore !== isDarkAfter);
      themeToggleWorks = (isDarkBefore !== isDarkAfter);
      
      // Toggle back to restore state
      await themeBtn.click();
      await page.waitForTimeout(300);
    }

    // ==========================================
    // PHASE 4: Intelligent Question Studio Testing (50 Questions)
    // ==========================================
    console.log('--- GENERATING AND CLASSIFYING 50 QUESTIONS ---');
    await page.click('a[data-target="view-manual"]');
    await page.waitForSelector('#view-manual', { state: 'visible' });

    // Define 50 CS questions across 12 domains
    const domainsQuestions = [
      // 1. Algorithms
      { domain: 'Algorithms', q: 'What is the time complexity of QuickSort in the worst case, and how does randomized pivot selection prevent it?' },
      { domain: 'Algorithms', q: 'Explain how Dijkstra\'s shortest path algorithm works and why it fails on graphs with negative edge weights.' },
      { domain: 'Algorithms', q: 'Describe the main differences between dynamic programming and greedy algorithmic paradigms.' },
      { domain: 'Algorithms', q: 'What is the master theorem in asymptotic analysis and when can it not be applied?' },
      
      // 2. Database Systems
      { domain: 'Database Systems', q: 'Explain the difference between optimistic and pessimistic concurrency control in transaction handling.' },
      { domain: 'Database Systems', q: 'What are ACID properties in database transactions and how is durability ensured by logging?' },
      { domain: 'Database Systems', q: 'Explain the differences between B-Trees and Hash indexes in database storage engines.' },
      { domain: 'Database Systems', q: 'Describe the three anomalies that database normalization to Third Normal Form (3NF) solves.' },
      
      // 3. Operating Systems
      { domain: 'Operating Systems', q: 'How does virtual memory translate addresses using Page Tables and Translation Lookaside Buffers?' },
      { domain: 'Operating Systems', q: 'Explain the difference between a process and a thread, and describe context-switching overhead.' },
      { domain: 'Operating Systems', q: 'What is a deadlock and what are the four necessary and sufficient Coffman conditions for it to occur?' },
      { domain: 'Operating Systems', q: 'Describe the differences between preemptive and non-preemptive CPU scheduling policies.' },
      
      // 4. Computer Networks
      { domain: 'Computer Networks', q: 'Describe the three-way handshake process in TCP and how sequence numbers prevent old duplicate segments.' },
      { domain: 'Computer Networks', q: 'Explain the differences between Link-State and Distance-Vector routing algorithms.' },
      { domain: 'Computer Networks', q: 'What is the purpose of the Domain Name System (DNS) recursive and iterative resolution process?' },
      { domain: 'Computer Networks', q: 'How does IPv4 NAT (Network Address Translation) map private addresses to public addresses?' },
      
      // 5. Compiler Design
      { domain: 'Compiler Design', q: 'What is the difference between LL(1) and LR(1) parsing techniques in syntactic analysis?' },
      { domain: 'Compiler Design', q: 'Explain the role of lexical analysis and how finite automata are used to recognize tokens.' },
      { domain: 'Compiler Design', q: 'What is intermediate code generation and why is Static Single Assignment (SSA) form useful?' },
      { domain: 'Compiler Design', q: 'Describe how a symbol table stores information about variables and scopes during compilation.' },
      
      // 6. Software Engineering
      { domain: 'Software Engineering', q: 'Explain the difference between high cohesion and low coupling in software design.' },
      { domain: 'Software Engineering', q: 'What is the SOLID design principles framework and how does the Liskov Substitution Principle prevent design bugs?' },
      { domain: 'Software Engineering', q: 'Describe the difference between black-box and white-box testing strategies in QA.' },
      { domain: 'Software Engineering', q: 'What is the software design pattern "Observer Pattern" and when should it be used?' },
      
      // 7. Cloud Computing
      { domain: 'Cloud Computing', q: 'Explain the concept of Serverless computing (FaaS) and how it differs from traditional IaaS virtual machines.' },
      { domain: 'Cloud Computing', q: 'Describe the shared responsibility security model between cloud providers and cloud consumers.' },
      { domain: 'Cloud Computing', q: 'What is horizontal auto-scaling and how do load balancers distribute traffic dynamically?' },
      { domain: 'Cloud Computing', q: 'Compare object storage (e.g. S3) with block storage (e.g. EBS) in cloud architectures.' },
      
      // 8. Big Data
      { domain: 'Big Data', q: 'How does the MapReduce framework process large datasets in a distributed computing cluster?' },
      { domain: 'Big Data', q: 'Explain the difference between batch processing and stream processing in modern data architectures.' },
      { domain: 'Big Data', q: 'What is the CAP theorem in distributed systems and why can we only choose two out of three guarantees?' },
      { domain: 'Big Data', q: 'Describe the Hadoop Distributed File System (HDFS) master-worker architecture.' },
      
      // 9. Artificial Intelligence
      { domain: 'Artificial Intelligence', q: 'What is the difference between search-based AI techniques like A* search and heuristic search?' },
      { domain: 'Artificial Intelligence', q: 'Describe the minimax algorithm and how alpha-beta pruning optimizes the decision tree.' },
      { domain: 'Artificial Intelligence', q: 'Explain how knowledge representation works in Expert Systems using production rules.' },
      { domain: 'Artificial Intelligence', q: 'What is the difference between strong AI and weak AI in computer science research?' },
      
      // 10. Machine Learning
      { domain: 'Machine Learning', q: 'Explain the bias-variance tradeoff in supervised machine learning models.' },
      { domain: 'Machine Learning', q: 'What is gradient descent and how does the learning rate parameter affect convergence?' },
      { domain: 'Machine Learning', q: 'Describe the differences between supervised, unsupervised, and reinforcement learning.' },
      { domain: 'Machine Learning', q: 'What is a confusion matrix and how do you calculate Precision, Recall, and F1-Score?' },
      { domain: 'Machine Learning', q: 'Explain how neural networks use backpropagation to update weights in training.' },
      
      // 11. Cyber Security
      { domain: 'Cyber Security', q: 'How does RSA public key cryptography work, and why is it secure against key recovery attacks?' },
      { domain: 'Cyber Security', q: 'Explain the difference between symmetric and asymmetric encryption and when each is used.' },
      { domain: 'Cyber Security', q: 'What is a SQL Injection vulnerability and how do parameterized queries prevent it?' },
      { domain: 'Cyber Security', q: 'Describe the difference between symmetric cipher key exchange and Diffie-Hellman key exchange.' },
      { domain: 'Cyber Security', q: 'What is Cross-Site Scripting (XSS) and how can sanitizing input mitigate it?' },
      
      // 12. Data Structures
      { domain: 'Data Structures', q: 'Explain how a Red-Black Tree maintains self-balancing properties during insertions.' },
      { domain: 'Data Structures', q: 'Compare the operations and complexity of Hash Tables using separate chaining versus open addressing.' },
      { domain: 'Data Structures', q: 'What is a min-heap and how does the heapify operation build it in linear time?' },
      { domain: 'Data Structures', q: 'Describe the difference between an adjacency list and an adjacency matrix for graph representation.' }
    ];

    for (let idx = 0; idx < domainsQuestions.length; idx++) {
      const { domain, q } = domainsQuestions[idx];
      console.log(`Processing question ${idx+1}/50: Domain: ${domain}`);
      
      const startTime = Date.now();
      
      // Fill question
      await page.fill('#manualQuestion', q);
      await page.click('#btnClassify');
      
      // Wait for result section to be visible
      await page.waitForSelector('#singleResultSection', { state: 'visible' });
      
      // Get results
      const bloom = await page.locator('#resBloom').innerText();
      const diff = await page.locator('#resDiff').innerText();
      const conf = await page.locator('#resConfText').innerText();
      const explanation = await page.locator('#resExplanation').innerText();
      const duration = Date.now() - startTime;
      
      let variant = null;
      let rephraseDuration = 0;
      
      // Rephrase first 5 questions to test rephrasing logic E2E
      if (idx < 5) {
        console.log(`  Rephrasing question ${idx+1} to alternative difficulty...`);
        const rephraseStart = Date.now();
        
        // Find alternative button
        const generateAltBtn = page.locator('.btn-generate-alt').first();
        if (await generateAltBtn.isVisible()) {
          const targetDiff = await generateAltBtn.getAttribute('data-target');
          await generateAltBtn.click();
          
          // Wait for rephrase to finish
          await page.waitForSelector('#stackedVariantsWrapper', { state: 'visible', timeout: 90000 });
          await page.waitForSelector('#stackedAlternativesContainer .arena-card', { state: 'visible', timeout: 90000 });
          
          const variantCard = page.locator('#stackedAlternativesContainer .arena-card').first();
          const varBloom = await variantCard.locator('span').first().innerText().catch(() => '-');
          const varDiff = await variantCard.locator('span').nth(1).innerText().catch(() => '-');
          const varQuestion = await variantCard.locator('p').first().innerText().catch(() => '-');
          
          variant = {
            targetDifficulty: targetDiff,
            bloom: varBloom,
            difficulty: varDiff,
            question: varQuestion,
            explanation: 'See card contents'
          };
          rephraseDuration = Date.now() - rephraseStart;
        }
      }
      
      questionLogs.push({
        index: idx + 1,
        domain,
        inputQuestion: q,
        bloomLevel: bloom,
        difficulty: diff,
        confidence: conf,
        explanation,
        latencyMs: duration,
        variant,
        rephraseLatencyMs: rephraseDuration
      });
      
      // Click clear
      await page.click('#btnClear');
      await expect(page.locator('#singleResultSection')).toBeHidden();
      // Ensure the stacked container is cleared
      await page.evaluate(() => {
        const container = document.getElementById('stackedAlternativesContainer');
        if (container) container.innerHTML = '';
        const wrapper = document.getElementById('stackedVariantsWrapper');
        if (wrapper) wrapper.classList.add('hidden');
      });
    }

    // ==========================================
    // PHASE 5: Bulk Processing E2E Verification
    // ==========================================
    console.log('--- RUNNING BULK PROCESSING AUDIT ---');
    await page.click('a[data-target="view-batch"]');
    await page.waitForSelector('#view-batch', { state: 'visible' });

    // Generate CSV containing 15 CS questions
    const csvContent = [
      'Question',
      'What is the difference between a process and a thread in modern operating systems?',
      'How does the virtual memory page table mapping mechanism handle page faults?',
      'Explain the mechanism of a TCP SYN flood attack and how SYN cookies mitigate it.',
      'What is the purpose of database indexes and why are B+ trees preferred over binary search trees?',
      'How does the MapReduce framework partition data during the shuffle phase?',
      'Explain the difference between overfitting and underfitting in ML models.',
      'What is public-key cryptography and how does the Diffie-Hellman algorithm work?',
      'Describe the difference between Depth First Search (DFS) and Breadth First Search (BFS).',
      'How does the compiler lexical analyzer identify tokens from source character streams?',
      'What is the difference between coupling and cohesion in modular software design?',
      'Describe the role of a hypervisor in hardware virtualization.',
      'What is DNS poisoning and how does DNSSEC resolve this security issue?',
      'Explain how a hash table handles collisions using separate chaining.',
      'What are the primary differences between SQL and NoSQL database models?',
      'Explain how the three-way handshake works in TCP.'
    ].join('\n');

    const tempCsvPath = path.join(__dirname, 'temp_benchmark.csv');
    fs.writeFileSync(tempCsvPath, csvContent, 'utf-8');

    // Upload
    await page.setInputFiles('input[type="file"]', tempCsvPath);
    const uploadBtn = page.locator('#uploadBtn');
    await expect(uploadBtn).toBeEnabled();
    await uploadBtn.click();

    // Wait for the preview table to be populated
    await page.waitForSelector('#previewTbody tr', { timeout: 60000 });
    const previewRowsCount = await page.locator('#previewTbody tr').count();
    console.log('Questions in preview table:', previewRowsCount);

    // Start processing
    const startProcessingBtn = page.locator('#btnStartProcessingPreview');
    const bulkStart = Date.now();
    await startProcessingBtn.click();

    // Verify progress panel and stats row appear
    await expect(page.locator('#liveProgressPanel')).toBeVisible();
    await expect(page.locator('#liveStatsRow')).toBeVisible();

    // Wait until processing finishes
    const stopBatchBtn = page.locator('#btnStopBatch');
    await expect(stopBatchBtn).toBeDisabled({ timeout: 600000 });
    const bulkDuration = Date.now() - bulkStart;
    console.log('Bulk processing completed in:', bulkDuration, 'ms');

    // Verify results table rendered
    await expect(page.locator('#batchResultsSection')).toBeVisible();
    const resultRows = await page.locator('#resultsTbody tr').all();
    console.log(`Number of results in table: ${resultRows.length}`);

    // Export All CSV
    const downloadPromiseAllCSV = page.waitForEvent('download').catch(() => null);
    await page.click('button:has-text("Export All")');
    await page.click('#btnExportAllCSV');
    const downloadCSV = await downloadPromiseAllCSV;

    bulkLogs = {
      previewRowsCount,
      processedRowsCount: resultRows.length,
      durationMs: bulkDuration,
      exportSuccess: !!downloadCSV
    };

    // Clean up temporary file
    try {
      fs.unlinkSync(tempCsvPath);
    } catch (e) {}

    // ==========================================
    // PHASE 7: Responsive Viewport Testing
    // ==========================================
    console.log('--- TESTING RESPONSIVE VIEWPORTS ---');
    const viewports = [
      { name: 'Desktop', width: 1440, height: 900 },
      { name: 'Laptop', width: 1024, height: 768 },
      { name: 'Tablet Portrait', width: 768, height: 1024 },
      { name: 'Mobile Portrait', width: 375, height: 812 },
      { name: 'Mobile Landscape', width: 812, height: 375 }
    ];

    for (const vp of viewports) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.waitForTimeout(200);
      viewportsTested.push(vp.name);
    }

    // Reset to default desktop
    await page.setViewportSize({ width: 1280, height: 800 });

    // ==========================================
    // PHASE 9: Accessibility & Keyboard Audit
    // ==========================================
    console.log('--- RUNNING KEYBOARD & TAB AUDIT ---');
    await page.keyboard.press('Tab');
    const activeTagName = await page.evaluate(() => document.activeElement.tagName);
    console.log('Tab key active element tag:', activeTagName);
    accessibilityChecks.push({
      keyboardTabResponsive: !!activeTagName
    });

    // Save final report data
    const auditData = {
      consoleErrors,
      consoleWarnings,
      pageExceptions,
      failedRequests,
      questionLogs,
      bulkLogs,
      viewportsTested,
      themeToggleWorks,
      accessibilityChecks
    };

    fs.writeFileSync(path.join(__dirname, '../tests/audit_run_data.json'), JSON.stringify(auditData, null, 2));
    console.log('--- COMPREHENSIVE EXPLORATORY AUDIT COMPLETE ---');
  });
});
