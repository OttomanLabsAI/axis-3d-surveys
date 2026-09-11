// Full-page screenshots of every template at desktop and phone width, plus an
// overflow check (any page wider than its viewport fails).
//
//   NODE_PATH=/opt/node22/lib/node_modules node scripts/screenshots.js [outDir]
//
// Serves public/ on a local port; needs the globally installed Playwright and
// its Chromium (PLAYWRIGHT_BROWSERS_PATH is set in the remote environment).
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const PUBLIC = path.resolve(__dirname, '..', 'public');
const OUT = path.resolve(process.argv[2] || '.render-check/pages');
const PAGES = ['/', '/about-us/', '/our-services/', '/our-projects/', '/contact-us/', '/service/scan-to-bim/', '/project/measured-survey-commercial-headquarters-london/', '/team/endrit-badallaj/', '/improvements/', '/404.html'];
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.png': 'image/png', '.txt': 'text/plain' };

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p.endsWith('/')) p += 'index.html';
  const file = path.join(PUBLIC, p);
  if (!file.startsWith(PUBLIC) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end('not found'); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  let failures = 0;
  for (const [label, width, height] of [['desktop', 1440, 900], ['phone', 390, 844]]) {
    const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    for (const route of PAGES) {
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(`http://127.0.0.1:${port}${route}`, { waitUntil: 'networkidle' });
      await page.evaluate(() => document.fonts.ready);
      // Scroll through the page so lazily loaded images are fetched before the capture
      await page.evaluate(async () => {
        document.documentElement.style.scrollBehavior = 'auto';  // the site scrolls smoothly; the capture must not
        for (let y = 0; y < document.documentElement.scrollHeight; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 80)); }
        window.scrollTo(0, 0);
        await new Promise(r => setTimeout(r, 300));
      });
      await page.waitForLoadState('networkidle');
      await page.waitForFunction(() => Array.from(document.images).every(i => i.complete), null, { timeout: 5000 }).catch(() => {});
      const over = await page.evaluate(() => Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth);
      const name = (route === '/' ? 'home' : route.replace(/^\/|\/$/g, '').replace(/[\/.]/g, '-')) + '-' + label + '.png';
      await page.screenshot({ path: path.join(OUT, name), fullPage: true });
      const flag = over > 0 ? `OVERFLOW +${over}px` : 'ok';
      if (over > 0 || errors.length) failures++;
      console.log(`${label.padEnd(8)} ${route.padEnd(58)} ${flag}${errors.length ? '  JS errors: ' + errors.join(' | ') : ''}`);
    }
    await ctx.close();
  }
  await browser.close();
  server.close();
  console.log(failures ? `\n${failures} page(s) need attention` : '\nNo horizontal overflow, no script errors.');
  process.exit(failures ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
