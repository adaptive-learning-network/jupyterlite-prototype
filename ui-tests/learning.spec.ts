import { expect, Page, test } from '@playwright/test';

// Drive real exercises in both Jupyter kernels and check that the
// adaptive-learning engine records observations and adapts recommendations.

async function openNotebook(page: Page, path: string): Promise<void> {
  await page.goto(`/lab/index.html?path=${path}`);
  await expect(page.locator('#al-engine-learning')).toBeVisible();
  await expect(page.locator('.jp-Notebook .jp-Cell').nth(2)).toBeVisible();
  // Wait for the Jupyter kernel to be idle before running cells.
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({ timeout: 180_000 });
}

async function runCell(page: Page, index: number, source?: string): Promise<void> {
  const cell = page.locator('.jp-Notebook .jp-Cell').nth(index);
  await cell.locator('.cm-content').click();
  if (source !== undefined) {
    await page.keyboard.press('ControlOrMeta+a');
    await page.keyboard.type(source);
  }
  await page.keyboard.press('Shift+Enter');
}

const panel = (page: Page) => page.locator('#al-engine-learning');

test('Python: a correct answer becomes evidence and unlocks the next activity', async ({ page }) => {
  await openNotebook(page, 'exercises/python/01-frequency.ipynb');
  await expect(panel(page).locator('.al-rec-title').first()).toHaveText('1. Count cases by exposure');

  await runCell(page, 1);
  await runCell(page, 2); // placeholder untouched
  await expect(panel(page).locator('.al-feedback')).toContainText('Not finished yet');

  await runCell(page, 2, 'ill_exposed = 29');
  await expect(panel(page).locator('.al-feedback')).toContainText('Not yet correct');

  await runCell(page, 2, 'ill_exposed = sum(a == 1 and i == 1 for a, i in zip(ate_salad, ill))');
  await expect(panel(page).locator('.al-feedback')).toContainText('Correct. Recorded as evidence.');
  await expect(panel(page).locator('.al-rec-title').first()).toHaveText('1. Calculate attack rates');
  await expect(panel(page).locator('.al-gap.al-achieved')).toContainText('Count cases by exposure');
});

test('R: hints within the ceiling count; the same engine serves the R Jupyter kernel', async ({ page }) => {
  await openNotebook(page, 'exercises/r/01-frequency.ipynb');
  await panel(page).getByRole('button', { name: 'Show a hint' }).click();
  await expect(panel(page).locator('.al-hint')).toContainText('Hint 1');

  await runCell(page, 1);
  await runCell(page, 2, 'ill_exposed <- sum(ate_salad == 1 & ill == 1)');
  await expect(panel(page).locator('.al-feedback')).toContainText('Correct. Recorded as evidence.');
  await expect(panel(page).locator('.al-rec-title').first()).toHaveText('1. Calculate attack rates');
});
