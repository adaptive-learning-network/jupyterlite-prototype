import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';

const path = 'notebooks/u03-n08-my-learning-record.ipynb';
const key = 'al-engine:learner-record:v0.1';
const catalog = JSON.parse(readFileSync('app-assets/adaptive-learning/catalog.json', 'utf8'));

test('record opens without code execution and leaves an empty record unchanged', async ({ page }) => {
  await page.goto(`/lab/index.html?path=${path}`);
  const view = page.locator('.al-RecordView');
  await expect(view).toContainText('No attempts recorded yet.');
  await expect(view).toContainText('No reflections recorded yet.');
  await expect(page.locator('.jp-Notebook .cm-content:visible')).toHaveCount(0);
  const before = await page.evaluate(key => localStorage.getItem(key), key);
  await view.getByRole('button', { name: 'Refresh', exact: true }).click();
  expect(await page.evaluate(key => localStorage.getItem(key), key)).toBe(before);
});

test('Run, Clear All Outputs and Run All restore the record without adding attempts', async ({ page }) => {
  await page.goto(`/lab/index.html?path=${path}`);
  const view = page.locator('.al-RecordView');
  await expect(view).toContainText('No attempts recorded yet.');
  const before = await page.evaluate(key => localStorage.getItem(key), key);
  const cell = page.locator('.jp-Notebook .jp-Cell[data-windowed-list-index="1"]');
  const original = await view.elementHandle();
  await cell.click({ position: { x: 40, y: 10 } });
  await page.keyboard.press('Escape');
  await page.keyboard.press('Control+Enter');
  await expect.poll(() => original!.evaluate(node => node.isConnected), { timeout: 90000 }).toBe(false);
  await expect(view).toContainText('No attempts recorded yet.');
  await expect(cell.locator('.cm-content:visible')).toHaveCount(0);
  await page.getByRole('menuitem', { name: 'Edit', exact: true }).click();
  await page.getByRole('menuitem', { name: 'Clear Outputs of All Cells', exact: true }).click();
  await expect(view).toHaveCount(0);
  await page.getByRole('menuitem', { name: 'Run', exact: true }).click();
  await page.getByRole('menuitem', { name: 'Run All Cells', exact: true }).click();
  await expect(view).toContainText('No attempts recorded yet.');
  await expect(cell.locator('.cm-content:visible')).toHaveCount(0);
  expect(await page.evaluate(key => localStorage.getItem(key), key)).toBe(before);
});

test('record shows readable attempts, progress and safe reflections after reload', async ({ page }, testInfo) => {
  const activity = catalog.activities.find((a: { iri: string }) => a.iri.endsWith('#act-dhis2-query'));
  expect(activity).toBeTruthy();
  const record = {
    schema: 'al-learner-record/0.1', learner: 'urn:uuid:11111111-1111-4111-8111-111111111111',
    audience: catalog.audiences[0].iri, guidance: {},
    observations: ['Incorrect', 'Correct'].map((outcome, index) => ({
      iri: `urn:uuid:22222222-2222-4222-8222-22222222222${index}`,
      activity: activity.iri, object: 'urn:exercise:dhis2',
      action: 'https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#OutputValidated',
      outcome: 'https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#' + outcome,
      guidanceLevel: 0, at: `2026-10-19T12:0${index}:00Z`, language: 'python'
    })),
    reflections: { quality: [{ prompt: 'What would you verify?', answer: '<img src=x onerror="alert(1)"> Check the missing onset date.', savedAt: '2026-10-19T12:02:00Z' }] }
  };
  await page.addInitScript(({ key, record }) => {
    if (!localStorage.getItem(key)) localStorage.setItem(key, JSON.stringify(record));
  }, { key, record });
  await page.goto(`/lab/index.html?path=${path}`);
  const view = page.locator('.al-RecordView');
  await expect(view).toContainText('2 recorded attempts');
  await expect(view.getByRole('cell', { name: activity.title, exact: true }).first()).toBeVisible();
  await expect(view).toContainText('Not yet correct');
  await expect(view).toContainText('Correct');
  await expect(view).toContainText('Demonstrated');
  await expect(view).toContainText(record.reflections.quality[0].answer);
  await expect(view.locator('img')).toHaveCount(0);
  const before = await page.evaluate(key => localStorage.getItem(key), key);
  await view.getByRole('button', { name: 'Refresh' }).click();
  // Reopen explicitly: Jupyter's tab-restoration save is debounced.
  await page.goto(`/lab/index.html?path=${path}`);
  await expect(view).toContainText('2 recorded attempts');
  expect(await page.evaluate(key => localStorage.getItem(key), key)).toBe(before);
  await page.screenshot({ path: testInfo.outputPath('learner-record.png') });
});
