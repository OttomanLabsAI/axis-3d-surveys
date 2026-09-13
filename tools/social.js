// Render the social share thumbnail (1200x630) in the site's own design
// language, with the self-hosted fonts, and write it to
// public/assets/img/social.jpg. Every page points its Open Graph and Twitter
// image tags at that file.
//
//   NODE_PATH=/opt/node22/lib/node_modules node tools/social.js
//
// Serves public/ on a local port so the card can use the site's fonts, logo
// and photographs; needs the globally installed Playwright and its Chromium.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const PUBLIC = path.resolve(__dirname, '..', 'public');
const OUT = path.join(PUBLIC, 'assets', 'img', 'social.jpg');
const TYPES = { '.css': 'text/css', '.webp': 'image/webp', '.png': 'image/png', '.woff2': 'font/woff2', '.svg': 'image/svg+xml' };

const CARD = `<!doctype html><html lang="en-GB"><head><meta charset="utf-8">
<link rel="stylesheet" href="/fonts/fonts.css">
<style>
  html, body { margin: 0; background: #09162a; }
  .card { position: relative; width: 1200px; height: 630px; overflow: hidden; background: #09162a; color: #fff; font-family: Mulish, Arial, sans-serif; }
  .card .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 30%; opacity: .3; }
  .card .shade { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(9,22,42,.92) 0%, rgba(9,22,42,.55) 60%, rgba(9,22,42,.35) 100%); }
  .card .rule { position: absolute; left: 0; right: 0; top: 0; height: 10px; background: #e31e24; }
  .card .logo { position: absolute; left: 72px; top: 66px; height: 104px; width: auto; }
  .card h1 { position: absolute; left: 72px; top: 214px; margin: 0; font: 700 96px/1 Rajdhani, "Arial Narrow", Arial, sans-serif; letter-spacing: 1px; text-transform: uppercase; color: #fff; }
  .card h1 .red { color: #e31e24; }
  .card p { position: absolute; left: 72px; top: 428px; margin: 0; width: 820px; font: 400 31px/1.35 Mulish, Arial, sans-serif; color: rgba(255,255,255,.9); }
  .card .strip { position: absolute; left: 0; right: 0; bottom: 0; height: 72px; background: #000080; display: flex; align-items: center; justify-content: space-between; padding: 0 72px; font: 600 27px/1 Rajdhani, "Arial Narrow", Arial, sans-serif; letter-spacing: 1.5px; text-transform: uppercase; }
  .card .strip span::before { content: ""; display: inline-block; width: 12px; height: 12px; background: #e31e24; margin-right: 16px; vertical-align: 1px; }
</style></head><body>
<div class="card">
  <img class="bg" src="/assets/img/band-bg.webp" alt="">
  <div class="shade"></div>
  <div class="rule"></div>
  <img class="logo" src="/assets/img/logo-light.png" alt="Axis 3D Surveys">
  <h1>Need accurate<br><span class="red">surveys?</span></h1>
  <p>Reliable 3D scans and as-built models delivered when you need them. Scan-to-BIM, as-built verification, 4D planning and monitoring across the UK.</p>
  <div class="strip"><span>axis3dsurveys.com</span><span>07460 844015</span></div>
</div>
</body></html>`;

const server = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/card') { res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); return res.end(CARD); }
  const file = path.join(PUBLIC, p);
  if (!file.startsWith(PUBLIC) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end('not found'); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.goto(`http://127.0.0.1:${port}/card`, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight));
  await page.locator('.card').screenshot({ path: OUT, type: 'jpeg', quality: 86 });
  await browser.close();
  server.close();
  console.log(`wrote ${path.relative(process.cwd(), OUT)} (${Math.round(fs.statSync(OUT).size / 1024)} KB); fonts loaded: ${fonts.join(', ')}`);
})().catch(e => { console.error(e); process.exit(1); });
