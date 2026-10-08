import { expect, Page, test } from '@playwright/test';

const notebook = 'exercises/python/u01-n01-data-to-decision.ipynb';
const panel = (page: Page) => page.locator('#al-engine-learning');

async function runCell(page: Page, index: number, source?: string): Promise<void> {
  const cell = page.locator('.jp-Notebook .jp-Cell').nth(index);
  await cell.locator('.cm-content').click();
  if (source !== undefined) {
    await page.keyboard.press('ControlOrMeta+a');
    await page.keyboard.insertText(source);
  }
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

test('Unit 1 pilot shows source visuals and records retry-to-success progression', async ({ page }) => {
  await page.goto(`/lab/index.html?path=${notebook}`);
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook .jp-Cell').nth(2)).toBeVisible();
  await expect(page.locator('.jp-Notebook img')).toHaveCount(2);
  await expect(page.locator('.jp-Notebook')).toContainText('Unit 01 · Notebook 01 · Python');
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  await expect(panel(page).locator('.al-rec').filter({ hasText: 'Unit 1: From data to a public health decision' })).toHaveCount(1);
  await runCell(page, 1);

  await runCell(page, 2);
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete']);
  await runCell(page, 2, [
    "priority_district = 'Bombali'",
    'increase = 5',
    "recommended_step = 'verify_reports_and_investigate'"
  ].join('\n'));
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect']);
  await expect(panel(page).locator('.al-gap.al-achieved').filter({ hasText: 'Justify a public health action from data' })).toHaveCount(0);

  await runCell(page, 2, [
    'weeks = {district: {} for district in {r["district"] for r in reports}}',
    'for row in reports:',
    '    weeks[row["district"]][row["week"]] = row["reported_cases"]',
    'changes = {district: counts["current"] - counts["previous"] for district, counts in weeks.items()}',
    'priority_district = max(changes, key=changes.get)',
    'increase = changes[priority_district]',
    "recommended_step = 'verify_reports_and_investigate'"
  ].join('\n'));
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Correct']);
  await expect(panel(page).locator('.al-gap.al-achieved').filter({ hasText: 'Justify a public health action from data' })).toHaveCount(1);
  await expect(panel(page).locator('.al-rec').filter({ hasText: 'Data or information?' })).toHaveCount(1);

  await page.reload();
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Correct']);
});
