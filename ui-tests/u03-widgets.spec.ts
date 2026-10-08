import { expect, Page, test } from '@playwright/test';

const panel = (page: Page) => page.locator('#al-engine-learning');

async function runCell(page: Page, index: number): Promise<void> {
  await page.locator('.jp-Notebook .jp-Cell').nth(index).locator('.cm-content').click();
  await page.keyboard.press('Shift+Enter');
}

async function outcomes(page: Page): Promise<string[]> {
  return page.evaluate(() => {
    const raw = localStorage.getItem('al-engine:learner-record:v0.1');
    if (!raw) return [];
    return (JSON.parse(raw).observations as { outcome: string }[])
      .map(item => item.outcome.split('#').at(-1) ?? '');
  });
}

test('U03 N01 radio choices record incomplete, wrong, and correct attempts', async ({ page }) => {
  await page.context().route('**/*', route => {
    if (new URL(route.request().url()).hostname === '127.0.0.1') return route.continue();
    return route.abort();
  });
  await page.goto('/lab/index.html?path=exercises/python/u03-n01-data-or-information.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  await runCell(page, 1);
  const groups = page.locator('.jp-Notebook .jp-Cell').nth(1).locator('.widget-radio-box');
  await expect(groups).toHaveCount(6, { timeout: 180_000 });
  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete']);

  for (let i = 0; i < 6; i++) {
    await groups.nth(i).getByText('Data', { exact: true }).click();
  }
  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect']);

  for (const i of [1, 4, 5]) {
    await groups.nth(i).getByText('Information', { exact: true }).click();
  }
  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Correct']);
  await expect(panel(page).locator('.al-gap.al-achieved').filter({ hasText: 'Distinguish data from information' })).toHaveCount(1);
});
