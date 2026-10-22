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

test('U03 N06: guided practice, targeted help, different cases and persistent reassessment', async ({page},testInfo)=>{
  test.setTimeout(360000);
  const key='al-engine:learner-record:v0.1';
  const read=()=>page.evaluate(key=>JSON.parse(localStorage.getItem(key)!),key);
  await page.goto('/lab/index.html?path=notebooks/u03-n06-case-or-aggregate.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({timeout:180000});
  await runCell(page,1);
  const setup=page.locator('.jp-Cell[data-windowed-list-index="1"]');
  const feedback=setup.locator('.al-classification-feedback');
  const submit=setup.getByRole('button',{name:'Submit',exact:true});
  const another=setup.getByRole('button',{name:'Try another case',exact:true});
  const gap=panel(page).locator('.al-gap').filter({hasText:'Distinguish case-based and aggregate datasets'});
  async function choose(values:Record<string,string>) {
    for(const [id,value] of Object.entries(values))await setup.locator('.al-dataset-'+id).getByRole('radio',{name:value,exact:true}).check();
  }
  async function send() {
    const count=(await read()).observations.length;
    await submit.click();await expect.poll(async()=>(await read()).observations.length).toBe(count+1);
    await expect(submit).toBeEnabled();
  }
  await expect(setup.getByRole('radio')).toHaveCount(10);
  await expect(setup.locator('input[type="radio"]:checked')).toHaveCount(0);
  await expect(another).toBeDisabled();
  await send();await expect(feedback).toContainText('table(s) A, B, C, D, E');
  for(let i=0;i<3;i++) {
    await setup.getByRole('button',{name:'Show a hint',exact:true}).click();
    await expect.poll(async()=>(await read()).taskAttempts.at(-1).guidanceLevel).toBe(i+1);
    await expect(submit).toBeEnabled();
  }
  await choose({a:'Case-based',b:'Case-based',c:'Case-based',d:'Case-based',e:'Case-based'});
  await send();await expect(feedback).toContainText('Table B: Incorrect.');
  await expect(panel(page).locator('.al-task-help')).toContainText('grouped summary');
  await choose({b:'Aggregate',c:'Aggregate',e:'Aggregate'});
  await send();await expect(setup).toContainText('Practice completed with assistance');
  await expect(gap).not.toHaveClass(/al-achieved/);await expect(gap).not.toContainText('Competent');
  const practiceId=(await read()).taskAttempts.at(-1).id;
  const before=(await read()).observations.length;
  await runCell(page,1);await expect(another).toBeEnabled();
  expect((await read()).taskAttempts.at(-1).id).toBe(practiceId);
  expect((await read()).observations.length).toBe(before);
  await expect(setup).toContainText('Hint 3:');
  await another.click();await expect(setup.getByRole('radio')).toHaveCount(6);
  let active=(await read()).taskAttempts.at(-1);expect(active.taskId).toBe('new-case-1');expect(active.guidanceLevel).toBe(0);
  await expect(setup.getByRole('button',{name:'Show a hint',exact:true})).toBeDisabled();
  await choose({a:'Case-based'});await send();
  await expect(feedback).toContainText('No answer feedback is shown yet.');
  await expect(feedback).not.toContainText('Table A: Correct');
  expect((await read()).observations.at(-1).criteria.every((r:{outcome:string})=>r.outcome==='incomplete')).toBe(true);
  await choose({a:'Aggregate',b:'Aggregate',c:'Case-based'});await send();
  await expect(panel(page).locator('.al-task-help')).toContainText('individual-record');
  await choose({a:'Case-based'});await send();
  await expect(setup).toContainText('New case completed after feedback; try another case');
  await expect(gap).not.toHaveClass(/al-achieved/);
  const firstId=(await read()).taskAttempts.at(-1).id;
  await page.reload();await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({timeout:180000});
  await runCell(page,1);await expect(another).toBeEnabled();
  active=(await read()).taskAttempts.at(-1);expect(active.id).toBe(firstId);expect(active.submissions).toBe(2);
  await expect(setup.locator('.al-dataset-a').getByRole('radio',{name:'Case-based',exact:true})).toBeChecked();
  await another.click();await expect(setup).toContainText('Another reporting situation 2');
  await choose({a:'Aggregate',b:'Case-based',c:'Aggregate'});await send();
  await expect(gap).toHaveClass(/al-achieved/);
  await expect(gap).toContainText('Demonstrated on a different case');await expect(gap).not.toContainText('Competent');
  const saved=await read();expect(saved.observations.at(-1).attempt.guidanceLevel).toBe(0);
  expect(saved.observations.at(-1).attempt.submissions).toBe(1);
  expect(saved.observations.some((o:{guidanceLevel:number})=>o.guidanceLevel===3)).toBe(true);
  expect(saved.observations.at(-1).criteria).toHaveLength(3);
  await page.setViewportSize({width:1000,height:900});await setup.screenshot({path:testInfo.outputPath('classification-transfer.png')});
  await setup.getByRole('button',{name:'Return to practice',exact:true}).click();
  await expect(setup.getByRole('radio')).toHaveCount(10);
  expect((await read()).taskAttempts.at(-1).guidanceLevel).toBe(3);
  await page.goto('/lab/index.html?path=notebooks/u03-n08-my-learning-record.ipynb');
  await expect(page.locator('.al-RecordView')).toContainText('Demonstrated on a different case');
  await expect(page.locator('.al-RecordView')).toContainText('new-case-2');
  await expect(page.locator('.al-RecordView')).toContainText('Classification feedback');
});

test('U03 N06: a failed storage write preserves history and does not consume a new case',async({page})=>{
  test.setTimeout(240000);
  const key='al-engine:learner-record:v0.1';
  await page.goto('/lab/index.html?path=notebooks/u03-n06-case-or-aggregate.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toBeVisible({timeout:180000});
  await runCell(page,1);
  const setup=page.locator('.jp-Cell[data-windowed-list-index="1"]');
  const feedback=setup.locator('.al-classification-feedback');
  for(const [id,value] of Object.entries({a:'Case-based',b:'Aggregate',c:'Aggregate',d:'Case-based',e:'Aggregate'})) {
    await setup.locator('.al-dataset-'+id).getByRole('radio',{name:value,exact:true}).check();
  }
  const submit=setup.getByRole('button',{name:'Submit',exact:true});
  await submit.click();await expect(feedback).toContainText('All classifications are correct.');
  const before=await page.evaluate(key=>localStorage.getItem(key),key);
  await page.evaluate(key=>{
    const original=Storage.prototype.setItem;
    (globalThis as typeof globalThis & {restoreTaskStorage:()=>void}).restoreTaskStorage=()=>{Storage.prototype.setItem=original;};
    Storage.prototype.setItem=function(name,value){if(name===key)throw new DOMException('Storage full','QuotaExceededError');return original.call(this,name,value);};
  },key);
  await submit.click();await expect(feedback).toContainText('Your earlier record is unchanged.');
  expect(await page.evaluate(key=>localStorage.getItem(key),key)).toBe(before);
  await setup.getByRole('button',{name:'Try another case',exact:true}).click();
  await expect(feedback).toContainText('Your earlier record is unchanged.');
  expect(await page.evaluate(key=>localStorage.getItem(key),key)).toBe(before);
  await page.evaluate(()=>(globalThis as typeof globalThis & {restoreTaskStorage:()=>void}).restoreTaskStorage());
  await setup.getByRole('button',{name:'Try another case',exact:true}).click();
  await expect(setup).toContainText('Another reporting situation 1');
  const saved=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)!),key);
  expect(saved.taskAttempts).toHaveLength(2);expect(saved.observations).toHaveLength(1);
});
