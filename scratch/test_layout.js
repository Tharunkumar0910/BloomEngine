const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5000/');
  
  // Wait for sidebar nav
  await page.waitForSelector('a[data-target="view-dashboard"]');

  const views = ['view-dashboard', 'view-manual', 'view-batch', 'view-analytics', 'view-modelinfo'];
  const results = {};

  for (const viewId of views) {
    // Click tab to activate view
    await page.click(`a[data-target="${viewId}"]`);
    await page.waitForTimeout(200);

    results[viewId] = await page.evaluate((id) => {
      const el = document.getElementById(id);
      if (!el) return null;
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      
      // Let's also check first children of this view
      const firstChild = el.firstElementChild;
      const firstChildRect = firstChild ? firstChild.getBoundingClientRect() : null;
      const firstChildStyle = firstChild ? window.getComputedStyle(firstChild) : null;

      return {
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
        firstChild: firstChild ? {
          tagName: firstChild.tagName,
          id: firstChild.id,
          className: firstChild.className,
          rect: {
            x: firstChildRect.x,
            y: firstChildRect.y,
            width: firstChildRect.width,
            height: firstChildRect.height,
            top: firstChildRect.top
          },
          margin: firstChildStyle.margin,
          padding: firstChildStyle.padding,
          display: firstChildStyle.display,
          position: firstChildStyle.position
        } : null
      };
    }, viewId);
  }

  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})();
