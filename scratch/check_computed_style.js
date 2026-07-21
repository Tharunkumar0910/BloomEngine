const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5000/');
  
  // Navigate to Bulk Processing
  await page.click('a[data-target="view-batch"]');
  await page.waitForTimeout(500);

  const getComputedStyleInfo = async (selector) => {
    return await page.evaluate((sel) => {
      const el = document.querySelector(sel);
      if (!el) return { selector: sel, error: 'Not found' };
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      return {
        selector: sel,
        tagName: el.tagName,
        rect: {
          x: rect.x,
          y: rect.y,
          width: rect.width,
          height: rect.height,
          top: rect.top,
          left: rect.left
        },
        position: style.position,
        display: style.display,
        flexDirection: style.flexDirection,
        gridTemplateColumns: style.gridTemplateColumns,
        overflow: style.overflow,
        overflowY: style.overflowY,
        marginTop: style.marginTop,
        marginBottom: style.marginBottom,
        paddingTop: style.paddingTop,
        paddingBottom: style.paddingBottom,
        height: style.height,
        minHeight: style.minHeight,
        maxHeight: style.maxHeight,
        top: style.top,
        zIndex: style.zIndex
      };
    }, selector);
  };

  const selectors = [
    'html',
    'body',
    'div.min-h-screen', // parent
    'div.lg\\:pl-\\[260px\\]', // content wrapper
    'header', // sticky header
    'main', // main content
    '#view-batch', // view batch itself
    '#view-batch > div.mb-6', // view batch header title wrapper
    '#view-batch > div.rounded-xl', // upload card wrapper
    '#batchResultsSection' // results table section
  ];

  const styles = [];
  for (const sel of selectors) {
    styles.push(await getComputedStyleInfo(sel));
  }

  console.log(JSON.stringify(styles, null, 2));

  await browser.close();
})();
