'use strict';
// Local-only visual/keyboard acceptance. Use an existing Playwright install.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require(process.env.LIBRE_SITE_PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, 'libre-church/dist');
const output = path.resolve(process.env.LIBRE_SITE_TEST_OUTPUT || path.join(__dirname, 'local-church-acceptance'));
const tests = [], requests = [], external = [], errors = [];

async function main() {
  await fs.mkdir(output, { recursive: true });
  const policy = Object.fromEntries((await fs.readFile(path.join(root, '_headers'), 'utf8')).split('\n')
    .filter(line => line.includes(':')).map(line => { const i = line.indexOf(':'); return [line.slice(0, i).trim(), line.slice(i + 1).trim()]; }));
  const server = http.createServer(async (request, response) => {
    requests.push({ method: request.method, path: request.url });
    if (!['GET', 'HEAD'].includes(request.method)) { response.writeHead(405).end(); return; }
    let file;
    try {
      const location = new URL(request.url, 'http://127.0.0.1').pathname;
      file = path.resolve(root, '.' + decodeURIComponent(location === '/' ? '/index.html' : location));
      if (!file.startsWith(root + path.sep)) { response.writeHead(403).end(); return; }
      const bytes = await fs.readFile(file);
      response.writeHead(200, { ...policy, 'Content-Type': { '.html': 'text/html', '.css': 'text/css', '.svg': 'image/svg+xml', '.xml': 'application/xml' }[path.extname(file)] || 'text/plain' });
      response.end(request.method === 'HEAD' ? undefined : bytes);
    } catch {
      response.writeHead(404, { ...policy, 'Content-Type': 'text/html' });
      response.end(await fs.readFile(path.join(root, '404.html')));
    }
  });
  let browser;
  try {
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
    const origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({ executablePath: process.env.LIBRE_SITE_BROWSER_EXECUTABLE || undefined, headless: true, chromiumSandbox: true,
      args: ['--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run'] });
    const context = await browser.newContext({ serviceWorkers: 'block' });
    await context.route('**/*', route => {
      if (new URL(route.request().url()).origin === origin) return route.continue();
      external.push(route.request().url()); return route.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    async function check(name, fn) {
      try { await fn(); tests.push({ name, status: 'passed' }); console.log('PASS ' + name); }
      catch (error) { tests.push({ name, status: 'failed', error: error.message }); console.error('FAIL ' + name + ': ' + error.message); }
    }
    const response = await page.goto(origin);
    await check('stack/community home is static, canonical and clearly separate from member sign-in', async () => {
      assert.equal(response.status(), 200);
      assert.equal(await page.title(), 'LibreChurch Stack · libre.church');
      assert.equal(await page.locator('h1').textContent(), 'A shared home for church life.');
      assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'), 'https://libre.church/');
      assert.match(await page.locator('.note').textContent(), /Each church runs its own community; there is no shared member sign-in here/);
      assert.equal(await page.locator('script,form,iframe').count(), 0);
      assert.equal((await page.content()).includes('wotbc.heritage.faith'), false);
    });
    await check('navigation preserves the existing Bible destination and correct project sources', async () => {
      assert.equal(await page.locator('nav a[aria-current=page]').getAttribute('href'), 'https://libre.church/');
      assert.equal(await page.locator('nav a').count(), 3);
      const hrefs = await page.locator('a').evaluateAll(nodes => nodes.map(node => node.getAttribute('href')));
      for (const href of ['https://libre.faith/', 'https://libre.show/', 'https://github.com/edydex/heritage-community']) assert.ok(hrefs.includes(href));
      assert.equal(await page.locator('.primary').getAttribute('href'), 'https://github.com/edydex/heritage-community');
    });
    await check('icons load and desktop layout fits', async () => {
      await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.screenshot({ path: path.join(output, 'church-desktop.png'), fullPage: true });
    });
    await check('keyboard skip link reaches main and project action is focusable', async () => {
      await page.keyboard.press('Tab');
      assert.equal(await page.locator('.skip').evaluate(node => node === document.activeElement), true);
      await page.keyboard.press('Enter');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'main');
      await page.keyboard.press('Tab'); await page.keyboard.press('Tab');
      assert.equal(await page.locator('.primary').evaluate(node => node === document.activeElement), true);
    });
    await check('390px mobile layout and navigation fit', async () => {
      await page.setViewportSize({ width: 390, height: 844 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.screenshot({ path: path.join(output, 'church-mobile.png'), fullPage: true });
    });
    await check('dark layout keeps icons loaded and fits', async () => {
      await page.emulateMedia({ colorScheme: 'dark' });
      await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.screenshot({ path: path.join(output, 'church-dark.png'), fullPage: true });
    });
    await check('unknown paths return the local 404 with a home link', async () => {
      const missing = await page.goto(origin + '/missing-acceptance-page');
      assert.equal(missing.status(), 404);
      assert.equal(await page.locator('h1').textContent(), 'Page not found');
      assert.equal(await page.locator('main a').getAttribute('href'), '/');
    });
    await check('no external requests, writes or runtime errors', async () => {
      assert.deepEqual(external, []); assert.deepEqual(errors, []);
      assert.deepEqual([...new Set(requests.map(request => request.method))], ['GET']);
      assert.match(policy['Content-Security-Policy'], /form-action 'none'/);
    });
    const result = { browser: browser.version(), sandboxEnabled: true, tests, externalRequests: external, runtimeErrors: errors, requestMethods: [...new Set(requests.map(request => request.method))] };
    await fs.writeFile(path.join(output, 'results.json'), JSON.stringify(result, null, 2) + '\n');
    assert.ok(tests.every(test => test.status === 'passed'), 'LibreChurch acceptance failed; inspect results.json');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}
main().catch(error => { console.error(error.stack); process.exitCode = 1; });
