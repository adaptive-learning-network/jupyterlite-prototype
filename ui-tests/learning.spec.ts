import { expect, Page, test } from '@playwright/test';

// Drive real Unit 3 exercises in the Python Jupyter kernel and check that the
// adaptive-learning engine records observations and adapts recommendations.

async function openNotebook(page: Page, path: string): Promise<void> {
  await page.goto(`/lab/index.html?path=${path}`);
  await expect(page.locator('#al-engine-learning')).toBeVisible();
  // Wait for the Jupyter kernel to be idle before running cells.
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({ timeout: 180_000 });
}

async function runCell(page: Page, index: number, source?: string): Promise<void> {
  const cell = page.locator(`.jp-Notebook .jp-Cell[data-windowed-list-index="${index}"]`);
  await cell.scrollIntoViewIfNeeded();
  if (index === 3 && source === undefined) await cell.click();
  else await cell.locator('.cm-content').click();
  if (source !== undefined) {
    await page.keyboard.press('ControlOrMeta+a');
    await page.keyboard.type(source);
  }
  await page.keyboard.press('Shift+Enter');
}

const panel = (page: Page) => page.locator('#al-engine-learning');

test('Python: exploring the register becomes evidence and unlocks filtering', async ({ page }) => {
  await openNotebook(page, 'notebooks/u03-n02-explore-dataset.ipynb');
  await expect(panel(page).locator('.al-rec-title').first()).toHaveText('1. Unit 1: From data to a public health decision');
  await expect(panel(page).locator('.al-rec-title').filter({ hasText: 'Data or information?' })).toHaveCount(1);

  await runCell(page, 1); // loads pandas and the register
  await runCell(page, 2); // supplied computation alone is unscored
  await runCell(page, 2, "n_records = None\nfirst_date = None\nlast_date = None\nn_locations = None\nage_min = None\nage_max = None");
  await expect(panel(page).locator('.al-feedback')).toHaveCount(0);
  await runCell(page, 3);
  async function submit() {
    const cell = page.locator('.jp-CodeCell').filter({hasText:'# Run once to display Submit.'});
    await cell.scrollIntoViewIfNeeded();
    await cell.getByRole('button', {name:'Submit',exact:true}).click();
  }
  await submit();
  await expect(panel(page).locator('.al-feedback')).toContainText('Not finished yet');

  await runCell(page, 2, [
    'n_records = len(register)',
    "first_date = register['date_given'].min()",
    "last_date = register['date_given'].min()",
    "n_locations = register['location'].nunique()",
    "age_min = int(register['age'].min())",
    "age_max = int(register['age'].max())"
  ].join('\n'));
  await submit();
  await expect(panel(page).locator('.al-feedback')).toContainText('Not yet correct');

  await runCell(page, 2, [
    'n_records = len(register)',
    "first_date = register['date_given'].min()",
    "last_date = register['date_given'].max()",
    "n_locations = register['location'].nunique()",
    "age_min = int(register['age'].min())",
    "age_max = int(register['age'].max())"
  ].join('\n'));
  await submit();
  await expect(panel(page).locator('.al-feedback')).toContainText('Correct. Recorded as evidence.');
  await expect(panel(page).locator('.al-rec-title').filter({ hasText: 'Data or information?' })).toHaveCount(1);
  await expect(panel(page).locator('.al-rec-title').filter({ hasText: 'Unit 2: Trace Laila' })).toHaveCount(1);
  await expect(panel(page).locator('.al-gap.al-achieved')).toContainText('Explore a dataset with software');
});

test('the Python course has no external assessment or unavailable R selector', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('al-engine:preferred-language', 'r'));
  await openNotebook(page, 'notebooks/u03-n01-data-or-information.ipynb');
  await expect(panel(page).locator('.al-quizzes')).toHaveCount(0);
  await expect(panel(page).locator('.al-language')).toHaveCount(0);
  await expect(panel(page)).toContainText('Python notebooks');
  await expect(panel(page).getByRole('button', {name:'Open',exact:true}).first()).toBeEnabled();
  await panel(page).getByRole('button', {name:'Open',exact:true}).first().click();
  await expect(page.locator('.jp-Notebook:visible')).toContainText('From data to a public health decision');
});
