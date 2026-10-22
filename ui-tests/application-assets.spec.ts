import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';

test('site loader and frontend bytes match the current compiled extension', async ({ request }) => {
  const built = JSON.parse(readFileSync('al_engine/labextension/package.json', 'utf8'));
  const load = built.jupyterlab._build.load.replace(/\\+/g, '/');
  const config = await (await request.get('/jupyter-lite.json')).json();
  const extension = config['jupyter-config-data'].federated_extensions.find((item: {name: string}) => item.name === 'jupyterlite-al-engine');
  expect(extension.load).toBe(load);
  const response = await request.get('/extensions/jupyterlite-al-engine/' + load);
  expect(response.ok()).toBe(true);
  expect(await response.body()).toEqual(readFileSync('al_engine/labextension/' + load));
});

test('adaptive resources load outside the learner contents drive', async ({ page, request }) => {
  const listing = await (await request.get('/api/contents/all.json')).json();
  const names = listing.content.map((item: { name: string }) => item.name);
  expect(names).toEqual(['notebooks']);
  expect(names).not.toContain('al');
  expect(names).not.toContain('checks');
  expect((await request.get('/files/al/catalog.json')).status()).toBe(404);
  expect((await request.get('/files/checks/u01-data-to-decision.py')).status()).toBe(404);

  const config = await (await request.get('/jupyter-lite.json')).json();
  const base = config['jupyter-config-data'].alAssetsBaseUrl as string;
  expect(base).toMatch(/^assets\/adaptive-learning\/[0-9a-f]{20}\/$/);
  const catalog = await (await request.get(`/${base}catalog.json`)).json();
  expect(catalog.schema).toBe('al-catalog-projection/0.1');
  expect(await (await request.get(`/${base}checks/u01-data-to-decision.py`)).text())
    .toContain('AL_OBSERVATION');

  await page.goto('/lab/index.html');
  await expect(page.locator('#al-engine-learning')).toBeVisible();
  await expect(page.locator('.jp-DirListing-itemText').filter({ hasText: /^notebooks$/ })).toBeVisible();
  await expect(page.locator('.jp-DirListing-itemText').filter({ hasText: /^(al|checks|readings|exercises)$/ })).toHaveCount(0);
});

test('an unavailable check preserves the learner record and can be retried', async ({ page }) => {
  await page.goto('/lab/index.html?path=notebooks/u01-n01-data-to-decision.ipynb');
  const panel = page.locator('#al-engine-learning');
  await expect(panel).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toHaveCount(1, { timeout: 180_000 });
  const setup = page.locator('.jp-Notebook .jp-Cell[data-windowed-list-index="1"]');
  await setup.scrollIntoViewIfNeeded();
  await setup.locator('.cm-content').click();
  await page.keyboard.press('Shift+Enter');
  await expect(setup.locator('.jp-OutputArea')).toContainText('Kambia', { timeout: 180_000 });
  const exercise = page.locator('.jp-Notebook .jp-Cell[data-windowed-list-index="2"]');
  await exercise.scrollIntoViewIfNeeded();
  await exercise.locator('.cm-content').click();
  await page.keyboard.press('Shift+Enter');
  const submission = page.locator('.jp-Notebook .jp-Cell[data-windowed-list-index="3"]');
  await submission.scrollIntoViewIfNeeded();
  await submission.click();
  await page.keyboard.press('Shift+Enter');
  await submission.getByRole('button', {name:'Submit',exact:true}).click();
  await expect(panel.locator('.al-feedback')).toContainText('Not finished yet');
  const before = await page.evaluate(() => localStorage.getItem('al-engine:learner-record:v0.1'));
  // Inject the failed response at fetch: service-worker-controlled requests do
  // not consistently pass through Playwright's network routes.
  await page.evaluate(() => {
    const original = window.fetch.bind(window);
    const probe = { fail: true, requests: [] as string[] };
    (window as unknown as { alAssetProbe: typeof probe }).alAssetProbe = probe;
    window.fetch = async (input, init) => {
      const url = input instanceof Request ? input.url : String(input);
      if (url.includes('/assets/adaptive-learning/') && url.endsWith('/checks/u01-data-to-decision.py')) {
        probe.requests.push(url);
        if (probe.fail) return new Response('Temporarily unavailable', { status: 503 });
      }
      return original(input, init);
    };
  });
  await submission.getByRole('button', {name:'Submit',exact:true}).click();
  await expect(panel.locator('.al-feedback')).toContainText('HTTP 503');
  expect(await page.evaluate(() => localStorage.getItem('al-engine:learner-record:v0.1'))).toBe(before);

  await page.evaluate(() => { (window as unknown as { alAssetProbe: { fail: boolean } }).alAssetProbe.fail = false; });
  await submission.getByRole('button', {name:'Submit',exact:true}).click();
  await expect(panel.locator('.al-feedback')).toContainText('Not finished yet');
  await expect(panel.locator('.al-footer')).toContainText('2 observations');
  const requests = await page.evaluate(() => (window as unknown as { alAssetProbe: { requests: string[] } }).alAssetProbe.requests);
  expect(requests).toHaveLength(2);
  expect(requests.every(url => url.includes('/assets/adaptive-learning/'))).toBe(true);
});
