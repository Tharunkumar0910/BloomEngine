const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5000/');
  
  const views = ['view-dashboard', 'view-manual', 'view-batch', 'view-analytics', 'view-modelinfo'];
  
  const hierarchy = await page.evaluate((viewIds) => {
    return viewIds.map(id => {
      const el = document.getElementById(id);
      if (!el) return { id, error: 'Not found' };
      
      const path = [];
      let parent = el.parentElement;
      while (parent) {
        path.push({
          tagName: parent.tagName,
          id: parent.id,
          className: parent.className
        });
        parent = parent.parentElement;
      }
      
      return {
        id,
        parentPath: path
      };
    });
  }, views);
  
  console.log(JSON.stringify(hierarchy, null, 2));
  await browser.close();
})();
