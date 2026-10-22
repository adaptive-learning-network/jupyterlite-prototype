import { expect, Page, test } from '@playwright/test';

const panel = (page: Page) => page.locator('#al-engine-learning');

async function runCell(page: Page, index: number): Promise<void> {
  const cell = page.locator(`.jp-Notebook .jp-Cell[data-windowed-list-index="${index}"]`);
  await cell.scrollIntoViewIfNeeded();
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
  await page.goto('/lab/index.html?path=notebooks/u03-n01-data-or-information.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  await expect(page.locator('.jp-Notebook .jp-Cell[data-windowed-list-index="1"]').locator('.jp-InputArea')).toBeHidden();
  await runCell(page, 1);
  const board = page.locator('.jp-Notebook .jp-Cell[data-windowed-list-index="1"]').locator('.board');
  await expect(board.locator('.card')).toHaveCount(6, { timeout: 180_000 });
  await expect(page.locator('.jp-Notebook .jp-Cell[data-windowed-list-index="1"]').locator('.jp-InputArea')).toBeHidden();
  await page.getByRole('button', {name:'Submit',exact:true}).click();
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete']);
  await expect(page.locator('.jp-Notebook')).toContainText('Not complete yet.');

  await board.locator('.card[data-item="a"]').dragTo(board.locator('.zone[data-zone="data"]'), {
    sourcePosition: { x: 18, y: 18 }, targetPosition: { x: 30, y: 80 }
  });
  await expect(board.locator('.zone[data-zone="data"] .card[data-item="a"]')).toBeVisible();
  for (const letter of ['B', 'C', 'D', 'E', 'F']) {
    await board.getByRole('combobox', { name: `Move item ${letter} to` }).selectOption('data');
  }
  await page.getByRole('button', {name:'Submit',exact:true}).click();
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect']);
  await expect(page.locator('.jp-Notebook')).toContainText('Not yet correct.');

  for (const letter of ['B', 'E', 'F']) {
    await board.getByRole('combobox', { name: `Move item ${letter} to` }).selectOption('information');
  }
  await page.getByRole('button', {name:'Submit',exact:true}).click();
  await expect.poll(() => outcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Correct']);
  await expect(page.locator('.jp-Notebook')).toContainText('Your classifications distinguish raw observations from information.');
  await expect(panel(page).locator('.al-gap.al-achieved').filter({ hasText: 'Distinguish data from information' })).toHaveCount(1);
});

test('U03 N05 radio choices provide inline feedback and record retries', async ({ page }, testInfo) => {
  await page.goto('/lab/index.html?path=notebooks/u03-n05-machine-readable.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({timeout:180000});
  await runCell(page, 1);
  const setup = page.locator('.jp-Cell[data-windowed-list-index="1"]');
  const choices = setup.getByRole('radio');
  const submit = setup.getByRole('button', {name:'Submit',exact:true});
  await expect(choices).toHaveCount(3);
  await expect(setup.locator('input[type="radio"]:checked')).toHaveCount(0);
  await expect(setup.locator('.jp-InputArea')).toBeHidden();
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete']);
  await expect(setup).toContainText('Select an answer first.');
  await choices.nth(1).check();
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete','Incorrect']);
  await expect(setup).toContainText('Vaccine Type already has its own column.');
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete','Incorrect','Incorrect']);
  await choices.nth(2).check();
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete','Incorrect','Incorrect','Correct']);
  await expect(setup).toContainText('Each value has its own cell.');
  await expect(panel(page).locator('.al-gap.al-achieved').filter({hasText:'Recognise machine-readable dataset structure'})).toHaveCount(1);
  await page.setViewportSize({width:1000,height:900});
  await setup.scrollIntoViewIfNeeded();
  await setup.screenshot({path:testInfo.outputPath('machine-readable-radio-feedback.png')});
});

test('U03 N06 classifies each table with radio choices and records retries', async ({ page }, testInfo) => {
  await page.goto('/lab/index.html?path=notebooks/u03-n06-case-or-aggregate.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({timeout:180000});
  await runCell(page, 1);
  const setup = page.locator('.jp-Cell[data-windowed-list-index="1"]');
  const submit = setup.getByRole('button', {name:'Submit',exact:true});
  await expect(setup.getByRole('radio')).toHaveCount(10);
  await expect(setup.locator('input[type="radio"]:checked')).toHaveCount(0);
  await expect(setup.locator('.jp-InputArea')).toBeHidden();
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete']);
  await expect(setup).toContainText('Choose a classification for table(s) A, B, C, D, E.');
  await setup.locator('.al-dataset-a').getByRole('radio',{name:'Case-based',exact:true}).check();
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete','Incomplete']);
  await expect(setup).toContainText('Choose a classification for table(s) B, C, D, E.');
  for (const letter of ['b','c','d','e']) {
    await setup.locator('.al-dataset-'+letter).getByRole('radio',{name:'Case-based',exact:true}).check();
  }
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete','Incomplete','Incorrect']);
  await expect(setup).toContainText('Table A: Correct.');
  await expect(setup).toContainText('Table B: Incorrect.');
  await expect(setup).toContainText('Table D: Correct.');
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete','Incomplete','Incorrect','Incorrect']);
  for (const letter of ['b','c','e']) {
    await setup.locator('.al-dataset-'+letter).getByRole('radio',{name:'Aggregate',exact:true}).check();
  }
  await submit.click();
  await expect.poll(()=>outcomes(page)).toEqual(['Incomplete','Incomplete','Incorrect','Incorrect','Correct']);
  await expect(setup).toContainText('All five classifications are correct.');
  await expect(panel(page).locator('.al-gap.al-achieved').filter({hasText:'Distinguish case-based and aggregate datasets'})).toHaveCount(1);
  await page.setViewportSize({width:1000,height:1000});
  await setup.screenshot({path:testInfo.outputPath('case-aggregate-radio-feedback.png')});
});
