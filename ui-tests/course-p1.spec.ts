import { expect, Page, test } from '@playwright/test';

async function run(page: Page, index: number, source?: string) {
  const cell = page.locator(`.jp-Cell[data-windowed-list-index="${index}"]`);
  await cell.scrollIntoViewIfNeeded();
  if (source === undefined && index === 3) await cell.click();
  else {
    await cell.locator('.cm-content').click();
    if (source !== undefined) {
      await page.keyboard.press('ControlOrMeta+a');
      await page.keyboard.insertText(source);
    }
  }
  await page.keyboard.press('Shift+Enter');
}

for (const scenario of [
  { file: 'u03-n03-filter-records', variable: 'n_mmr_dose1_x', correct:
    "n_mmr_dose1_x = int(((register['vaccine_type'] == 'MMR') & (register['dose'] == 1) & (register['location'] == 'District X') & (register['age'] < 5)).sum())" },
  { file: 'u03-n04-coverage', variable: 'coverage_x', correct:
    "numerator = int(((register['vaccine_type'] == 'MMR') & (register['dose'] == 1) & (register['location'] == 'District X') & (register['age'] < 5)).sum())\ncoverage_x = numerator / population.loc[population['location'] == 'District X', 'population_under5'].item()" }
]) {
  test(`${scenario.file}: computation stays visible and only Submit records retries`, async ({ page }) => {
    await page.goto(`/lab/index.html?path=notebooks/${scenario.file}.ipynb`);
    await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({ timeout: 180000 });
    const outcomes = () => page.evaluate(() => JSON.parse(localStorage.getItem('al-engine:learner-record:v0.1')!).observations.map((o: {outcome: string}) => o.outcome.split('#').at(-1)));
    await run(page, 1);
    await run(page, 2);
    await expect.poll(outcomes).toEqual([]);
    await expect(page.locator('.jp-Cell[data-windowed-list-index="2"] .cm-content')).toBeVisible();
    await expect(page.locator('.jp-Cell[data-windowed-list-index="2"] .jp-OutputArea')).not.toContainText('Traceback');
    await run(page, 2, `${scenario.variable} = None`);
    await run(page, 3);
    const submission = page.locator('.jp-CodeCell').filter({hasText:'# Run once to display Submit.'});
    async function submit() {
      await submission.scrollIntoViewIfNeeded();
      await submission.getByRole('button', {name:'Submit',exact:true}).click();
    }
    await submit();
    await expect.poll(outcomes).toEqual(['Incomplete']);
    await run(page, 2, `${scenario.variable} = 0`);
    await expect.poll(outcomes).toEqual(['Incomplete']);
    await submit();
    await expect.poll(outcomes).toEqual(['Incomplete', 'Incorrect']);
    await expect(submission).toContainText('Not yet correct.');
    await run(page, 2, scenario.correct);
    await submit();
    await expect.poll(outcomes).toEqual(['Incomplete', 'Incorrect', 'Correct']);
    await expect(submission).toContainText('Correct.');
    await expect(submission).toContainText('Submitted answer');
  });
}

test('the complete contents and record-view onward link navigate locally', async ({ page }) => {
  const start = await (await page.request.get('/files/notebooks/u00-n00-start-here.ipynb')).json();
  const source = start.cells.find((c: {source: string[]}) => c.source.join('').startsWith('## Course contents')).source.join('');
  const paths = [...source.matchAll(/\]\((u\d\d-n\d\d-[^)]+\.ipynb)\)/g)].map(m => m[1]);
  expect(paths).toHaveLength(22);
  for (const path of paths) expect((await page.request.get('/files/notebooks/' + path)).ok()).toBe(true);
  await page.goto('/lab/index.html?path=notebooks/u00-n00-start-here.ipynb');
  const contents = page.locator('.jp-MarkdownCell').filter({hasText:'Course contents'});
  await contents.scrollIntoViewIfNeeded();
  await expect(contents.locator('a[href$="u03-n03-filter-records.ipynb"]')).toBeVisible();
  await contents.locator('a[href$="u03-n08-my-learning-record.ipynb"]').first().click();
  await expect(page.locator('.jp-Notebook:visible')).toContainText('My learning record');
  const next = page.locator('.jp-Notebook:visible a[href$="u04-n01-source-inventory.ipynb"]');
  await page.locator('.jp-Notebook:visible').hover();
  await expect.poll(async () => { if (await next.count()) return true; await page.mouse.wheel(0,650); return false; }).toBe(true);
  await expect(next).toBeVisible();
  await next.click();
  await expect(page.locator('.jp-Notebook:visible')).toContainText('Find the data Laila needs');
});
