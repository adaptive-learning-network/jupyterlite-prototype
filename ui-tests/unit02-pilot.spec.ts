import { expect, Page, test } from '@playwright/test';

const panel = (page: Page) => page.locator('#al-engine-learning');

async function runCell(page: Page, index: number): Promise<void> {
  const cell = page.locator(`.jp-Notebook .jp-Cell[data-windowed-list-index="${index}"]`);
  await cell.scrollIntoViewIfNeeded();
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
  await page.goto('/lab/index.html?path=notebooks/u02-n01-system-map.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect.poll(() => page.locator('.jp-Notebook img').count()).toBeGreaterThanOrEqual(2);
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

async function learnerMode(page: Page) {
  await page.route('**/jupyter-lite.json', async route => {
    const response=await route.fetch();const config=await response.json();
    config['jupyter-config-data']={...config['jupyter-config-data'],alCourseReviewMode:false};
    await route.fulfill({response,json:config});
  });
}
async function saveAndReload(page: Page, marker: string) {
  await page.goto('/lab/index.html?path=notebooks/u00-n00-start-here.ipynb');
  await expect(panel(page)).toBeVisible();
  const cell=page.locator('.jp-Cell[data-windowed-list-index="2"]');
  await cell.scrollIntoViewIfNeeded();await cell.dblclick();
  await cell.locator('.cm-content').click();await page.keyboard.press('ControlOrMeta+a');
  await page.keyboard.insertText(marker);await page.keyboard.press('Shift+Enter');
  await page.keyboard.press('ControlOrMeta+s');
  await expect(page.locator('.jp-mod-dirty')).toHaveCount(0);
  await expect(page.getByRole('dialog',{name:'File Save Error'})).toHaveCount(0);
  await page.reload();await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook')).toContainText(marker);
}
test('the unified course notebook saves in a fresh learner browser',async({page})=>{
  await learnerMode(page);await saveAndReload(page,'Local course save test');
});
test('repairs a missing browser course directory before saving',async({page})=>{
  await learnerMode(page);
  await page.route('**/api/contents/all.json',async route=>{
    const response=await route.fetch();const index=await response.json();
    index.content=index.content.filter((item:{name:string})=>item.name!=='notebooks');
    await route.fulfill({response,json:index});
  });
  await saveAndReload(page,'Recovered local course response');
});
test('saves a course notebook whose browser model has a Windows path',async({page})=>{
  await learnerMode(page);
  await page.route('**/api/contents/notebooks/all.json',async route=>{
    const response=await route.fetch();const index=await response.json();
    for(const item of index.content as {name:string;path:string}[]) {
      if(item.name==='u00-n00-start-here.ipynb') item.path=item.path.replaceAll('/','\\');
    }
    await route.fulfill({response,json:index});
  });
  await saveAndReload(page,'Windows path save recovered');
});
test('Unit 2 includes local slide previews and PDF pages',async({page})=>{
  await page.goto('/lab/index.html?path=notebooks/u02-n01-system-map.ipynb');
  await expect(panel(page)).toBeVisible();
  const notebook=await(await page.request.get('/files/notebooks/u02-n01-system-map.ipynb')).json();
  const gallery=notebook.cells.map((cell:{source:string[]})=>cell.source.join('')).join('\n');
  expect(gallery).toContain('assets/slide-previews/unit-2-001.jpg');
  expect(gallery).toContain('unit-2-version-2-slides.pdf#page=1');
  expect((await page.request.get('/files/notebooks/assets/slide-previews/unit-2-001.jpg')).ok()).toBe(true);
  expect((await page.request.get('/files/notebooks/assets/unit-2-version-2-slides.pdf')).ok()).toBe(true);
});
test('the integrated dataset lesson starts the Python kernel in the course folder',async({page})=>{
  await page.goto('/lab/index.html?path=notebooks/u03-n02-explore-dataset.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook')).toContainText('Using Software to Explore Datasets');
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({timeout:180000});
});
