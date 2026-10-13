import { expect, Page, test } from '@playwright/test';

const panel = (page: Page) => page.locator('#al-engine-learning');

async function runCell(page: Page, index: number): Promise<void> {
  const cell = page.locator('.jp-Notebook .jp-Cell').nth(index);
  if (index === 1) await cell.click();
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

async function selectStage(select: ReturnType<Page['locator']>, stage: string): Promise<void> {
  const value = await select.locator('option').filter({ hasText: stage }).getAttribute('value');
  expect(value).not.toBeNull();
  await select.selectOption(value!);
}

async function moveStage(select: ReturnType<Page['locator']>, button: ReturnType<Page['locator']>,
                         stage: string, expected: string[]): Promise<void> {
  await selectStage(select, stage);
  await button.click();
  await expect.poll(async () => (await select.locator('option').allTextContents())
    .map(text => text.replace(/\u00a0/g, ' ')), { timeout: 15_000 }).toEqual(expected);
}

test('Unit 2 system map records a wrong route and a corrected route', async ({ page }) => {
  await page.goto('/lab/index.html?path=exercises/python/u02-n01-system-map.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook img')).toHaveCount(2);
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  await runCell(page, 1);
  const setup = page.locator('.jp-Notebook .jp-Cell').nth(1);
  await expect(setup.locator('select')).toHaveCount(2, { timeout: 180_000 });

  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete']);
  const selectors = setup.locator('select');
  const buttons = setup.getByRole('button');
  await moveStage(selectors.nth(0), buttons.nth(0), 'Electronic patient records', [
    'Electronic patient records', 'District health information system', 'Ministry of Health', 'Electronic case alerts and reports']);
  await moveStage(selectors.nth(1), buttons.nth(2), 'Electronic laboratory records', [
    'Electronic laboratory reports', 'Electronic laboratory records', 'Ministry of Health', 'District health information system']);
  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect']);
  await expect(panel(page).locator('.al-rec').filter({ hasText: 'Unit 2: Map Laila' })).toHaveCount(1);

  await moveStage(selectors.nth(0), buttons.nth(0), 'Electronic case alerts and reports', [
    'Electronic patient records', 'District health information system', 'Electronic case alerts and reports', 'Ministry of Health']);
  await moveStage(selectors.nth(0), buttons.nth(0), 'Electronic case alerts and reports', [
    'Electronic patient records', 'Electronic case alerts and reports', 'District health information system', 'Ministry of Health']);
  await moveStage(selectors.nth(1), buttons.nth(3), 'Ministry of Health', [
    'Electronic laboratory reports', 'Electronic laboratory records', 'District health information system', 'Ministry of Health']);
  await moveStage(selectors.nth(1), buttons.nth(2), 'Electronic laboratory records', [
    'Electronic laboratory records', 'Electronic laboratory reports', 'District health information system', 'Ministry of Health']);
  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Correct']);
  await expect(panel(page).locator('.al-gap.al-achieved')).toContainText('Trace a report through health information systems');
  await expect(panel(page).locator('.al-rec').filter({ hasText: 'Data or information?' })).toHaveCount(1);
});

test('Unit 2 knowledge check reading saves in a fresh browser', async ({ page }) => {
  await page.goto('/lab/index.html?path=readings/ucsf/u02-n02-knowledge-check.ipynb');
  await expect(page.locator('.jp-Notebook .jp-Cell')).toHaveCount(4);
  await page.getByRole('dialog').getByRole('button', { name: 'No Kernel' }).click();
  const cell = page.locator('.jp-Notebook .jp-Cell').nth(2);
  await cell.click();
  await page.keyboard.press('Enter');
  await cell.locator('.cm-content').click();
  await page.keyboard.press('ControlOrMeta+a');
  await page.keyboard.insertText('Local save test');
  await page.keyboard.press('ControlOrMeta+s');
  await expect(page.getByRole('dialog', { name: 'File Save Error' })).toHaveCount(0);
  await page.goto('/lab/index.html?path=readings/ucsf/u02-n02-knowledge-check.ipynb');
  await expect(page.locator('.jp-Notebook')).toContainText('Local save test');
});

test('repairs a missing browser reading directory before saving', async ({ page }) => {
  // Reproduce an older static site whose notebook is present but whose parent
  // directory is absent from JupyterLite's contents index.
  await page.route('**/api/contents/readings/all.json', async route => {
    const response = await route.fetch();
    const index = await response.json();
    index.content = index.content.filter((item: { name: string }) => item.name !== 'ucsf');
    await route.fulfill({ response, json: index });
  });
  await page.goto('/lab/index.html?path=readings/ucsf/u02-n02-knowledge-check.ipynb');
  await expect(page.locator('.jp-Notebook .jp-Cell')).toHaveCount(4);
  const missingDirDialog = page.getByRole('dialog', { name: 'Directory not found' });
  if (await missingDirDialog.isVisible()) {
    await missingDirDialog.getByRole('button', { name: 'Close' }).click();
  }
  const noKernel = page.getByRole('dialog').getByRole('button', { name: 'No Kernel' });
  if (await noKernel.isVisible()) await noKernel.click();
  const responseCell = page.locator('.jp-Notebook .jp-Cell').nth(2);
  await responseCell.click();
  await page.keyboard.press('Enter');
  await responseCell.locator('.cm-content').click();
  await page.keyboard.press('ControlOrMeta+a');
  await page.keyboard.insertText('Recovered local response');
  await page.keyboard.press('ControlOrMeta+s');
  await expect(page.getByRole('dialog', { name: 'File Save Error' })).toHaveCount(0);
  await page.goto('/lab/index.html?path=readings/ucsf/u02-n02-knowledge-check.ipynb');
  await expect(page.locator('.jp-Notebook')).toContainText('Recovered local response');
});
