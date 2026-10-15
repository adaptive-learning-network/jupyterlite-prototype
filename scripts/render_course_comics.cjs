// Render native vector teaching art once; commit the PNGs so CI needs no browser
// during notebook generation. Filenames bind each PNG to its vector source hash.
const { chromium } = require('@playwright/test');
const fs = require('node:fs/promises');
const path = require('node:path');
const { createHash } = require('node:crypto');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 400, height: 404 }, deviceScaleFactor: 2 });
  for (const name of (await fs.readdir('artwork')).filter(name => /^laila-unit(?:0[4-9]|1[0-4])-story\.svg$/.test(name))) {
    const source = await fs.readFile(path.join('artwork', name));
    const hash = createHash('sha256').update(source).digest('hex').slice(0, 12);
    await page.setContent(`<html><body style="margin:0;background:white"><img width="400" height="404" src="data:image/svg+xml;base64,${source.toString('base64')}"></body></html>`);
    await page.locator('img').evaluate(img => img.decode());
    const output = path.join('content/exercises/assets', name.replace('.svg', `-${hash}.png`));
    await page.locator('img').screenshot({ path: output });
    process.stdout.write(output + '\n');
  }
  await browser.close();
})().catch(error => { process.stderr.write(String(error)); process.exitCode = 1; });
