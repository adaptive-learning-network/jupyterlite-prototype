import { expect, Page, test } from '@playwright/test';

// Drive real Unit 3 exercises in both Jupyter kernels and check that the
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

test('Python: exploring the register becomes evidence and unlocks filtering', async ({ page }) => {
  await openNotebook(page, 'exercises/python/02-explore-dataset.ipynb');
  await expect(panel(page).locator('.al-rec-title').first()).toHaveText('1. Unit 1: From data to a public health decision');
  await expect(panel(page).locator('.al-rec-title').filter({ hasText: 'Data or information?' })).toHaveCount(1);

  await runCell(page, 1); // loads pandas and the register
  await runCell(page, 2); // placeholders untouched
  await expect(panel(page).locator('.al-feedback')).toContainText('Not finished yet');

  await runCell(page, 2, [
    'n_records = len(register)',
    "first_date = register['date_given'].min()",
    "last_date = register['date_given'].min()",
    "n_locations = register['location'].nunique()",
    "age_min = int(register['age'].min())",
    "age_max = int(register['age'].max())"
  ].join('\n'));
  await expect(panel(page).locator('.al-feedback')).toContainText('Not yet correct');

  await runCell(page, 2, [
    'n_records = len(register)',
    "first_date = register['date_given'].min()",
    "last_date = register['date_given'].max()",
    "n_locations = register['location'].nunique()",
    "age_min = int(register['age'].min())",
    "age_max = int(register['age'].max())"
  ].join('\n'));
  await expect(panel(page).locator('.al-feedback')).toContainText('Correct. Recorded as evidence.');
  await expect(panel(page).locator('.al-rec-title').filter({ hasText: 'Data or information?' })).toHaveCount(1);
  await expect(panel(page).locator('.al-rec-title').filter({ hasText: 'Filter the records you need' })).toHaveCount(1);
  await expect(panel(page).locator('.al-gap.al-achieved')).toContainText('Explore a dataset with software');
});

test('R: coverage after a hint counts; the same engine serves the R Jupyter kernel', async ({ page }) => {
  await openNotebook(page, 'exercises/r/04-coverage.ipynb');
  await panel(page).getByRole('button', { name: 'Show a hint' }).click();
  await expect(panel(page).locator('.al-hint')).toContainText('Hint 1');

  await runCell(page, 1);
  await runCell(page, 2,
    'coverage_x <- sum(register$vaccine_type == "MMR" & register$dose == 1 & register$location == "District X" & register$age < 5) / ' +
    'population$population_under5[population$location == "District X"]');
  await expect(panel(page).locator('.al-feedback')).toContainText('Correct. Recorded as evidence.');
  await expect(panel(page).locator('.al-gap.al-achieved')).toContainText('Combine variables to produce information');
});

test('the Unit 3 knowledge check opens from the learning panel', async ({ page, context }) => {
  await context.route('https://forms.gle/**', route => route.fulfill({ contentType: 'text/html', body: '<title>Quiz</title>' }));
  await openNotebook(page, 'exercises/python/u03-n01-data-or-information.ipynb');
  const popup = page.waitForEvent('popup');
  await panel(page).getByRole('button', { name: 'Open: Unit 3 knowledge check' }).click();
  expect((await popup).url()).toBe('https://forms.gle/Y4yG5gMbFznczrBd9');
  await expect(panel(page).locator('.al-quizzes')).toContainText('not yet recorded');
});
