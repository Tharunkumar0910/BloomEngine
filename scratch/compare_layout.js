const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5000/');
  
  // Set viewport to a typical desktop size
  await page.setViewportSize({ width: 1440, height: 900 });

  const getMetrics = async (id) => {
    return await page.evaluate((elId) => {
      const el = document.getElementById(elId);
      if (!el) return { id: elId, error: 'Not found' };
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      return {
        id: elId,
        rect: {
          x: rect.x,
          y: rect.y,
          width: rect.width,
          height: rect.height,
          top: rect.top,
          left: rect.left
        },
        display: style.display,
        position: style.position,
        padding: style.padding,
        margin: style.margin,
        overflow: style.overflow,
        height: style.height,
        minHeight: style.minHeight,
        marginTop: style.marginTop,
        paddingTop: style.paddingTop,
        boxSizing: style.boxSizing
      };
    }, id);
  };

  const results = {};

  // 1. Dashboard active
  results['view-dashboard'] = await getMetrics('view-dashboard');

  // 2. Switch to manual, measure
  await page.click('a[data-target="view-manual"]');
  await page.waitForTimeout(500);
  results['view-manual'] = await getMetrics('view-manual');

  // 3. Switch to batch, measure
  await page.click('a[data-target="view-batch"]');
  await page.waitForTimeout(500);
  results['view-batch'] = await getMetrics('view-batch');
  
  // 4. Open Question Workspace (sliding drawer) and measure
  // We can open the drawer by switching to dashboard, clicking a question's inspect button or similar
  await page.click('a[data-target="view-dashboard"]');
  await page.waitForTimeout(500);
  
  // Wait for history table to load if any, or trigger drawer
  // Let's see if we can trigger the drawer directly
  await page.evaluate(() => {
    const drawer = document.getElementById('questionDetailDrawer');
    if (drawer) drawer.classList.remove('translate-x-full');
  });
  await page.waitForTimeout(500);
  results['questionDetailDrawer'] = await getMetrics('questionDetailDrawer');

  console.log(JSON.stringify(results, null, 2));

  await browser.close();
})();
