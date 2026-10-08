import { expect, Page, test } from '@playwright/test';

const panel = (page: Page) => page.locator('#al-engine-learning');

async function runCell(page: Page, index: number): Promise<void> {
  const cell = page.locator('.jp-Notebook .jp-Cell').nth(index);
  if (index === 1) await cell.click(); // the infrastructure source is collapsed
  else await cell.locator('.cm-content').click();
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

test('U03 N01 drag bins record incomplete, wrong, and correct attempts', async ({ page }) => {
  await page.context().route('**/*', route => {
    if (new URL(route.request().url()).hostname === '127.0.0.1') return route.continue();
    return route.abort();
  });
  await page.goto('/lab/index.html?path=exercises/python/u03-n01-data-or-information.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  await expect(page.locator('.jp-Notebook .jp-Cell').nth(1).locator('.jp-InputArea')).toBeHidden();
  await runCell(page, 1);
  const board = page.locator('.jp-Notebook .jp-Cell').nth(1).locator('.board');
  await expect(board.locator('.card')).toHaveCount(6, { timeout: 180_000 });
  await expect(page.locator('.jp-Notebook .jp-Cell').nth(1).locator('.jp-InputArea')).toBeHidden();
  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete']);

  await board.locator('.card[data-item="a"]').dragTo(board.locator('.zone[data-zone="data"]'), {
    sourcePosition: { x: 18, y: 18 }, targetPosition: { x: 30, y: 80 }
  });
  await expect(board.locator('.zone[data-zone="data"] .card[data-item="a"]')).toBeVisible();
  for (const letter of ['B', 'C', 'D', 'E', 'F']) {
    await board.getByRole('combobox', { name: `Move item ${letter} to` }).selectOption('data');
  }
  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect']);

  for (const letter of ['B', 'E', 'F']) {
    await board.getByRole('combobox', { name: `Move item ${letter} to` }).selectOption('information');
  }
  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Correct']);
  await expect(panel(page).locator('.al-gap.al-achieved').filter({ hasText: 'Distinguish data from information' })).toHaveCount(1);
});
