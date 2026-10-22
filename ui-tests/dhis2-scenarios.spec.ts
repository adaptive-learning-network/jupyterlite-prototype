import { expect, Page, test } from '@playwright/test';

// Each test gets a fresh browser context. These scenarios operate the real
// JupyterLite notebook and Learning panel without asking a tester to solve it.
const NOTEBOOK = 'notebooks/u03-n07-dhis2-query.ipynb';

const panel = (page: Page) => page.locator('#al-engine-learning');
const recommendation = (page: Page, title: string) => panel(page).locator('.al-rec').filter({ hasText: title });
const achieved = (page: Page, capability: string) => panel(page).locator('.al-gap.al-achieved').filter({ hasText: capability });

async function openPilot(page: Page): Promise<void> {
  await page.goto(`/lab/index.html?path=${NOTEBOOK}`);
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  await runCell(page, 1);
}

async function runCell(page: Page, index: number | string, source?: string): Promise<void> {
  if (typeof index === 'string') {
    const document = await (await page.request.get('/files/' + NOTEBOOK)).json();
    index = document.cells.findIndex((cell:{id:string})=>cell.id===index);
    expect(index).toBeGreaterThanOrEqual(0);
  }
  const cell = page.locator(`.jp-Notebook .jp-Cell[data-windowed-list-index="${index}"]`);
  await cell.scrollIntoViewIfNeeded();
  const editor=cell.locator('.cm-content');
  if(source!==undefined && !await editor.isVisible()) await cell.locator('.jp-Cell-inputCollapser').click();
  if(await editor.isVisible()) await editor.click();
  else await cell.click();
  if (source !== undefined) {
    await page.keyboard.press('ControlOrMeta+a');
    await page.keyboard.insertText(source);
  }
  await page.keyboard.press('Shift+Enter');
}

async function expectObservation(page: Page, count: number, feedback: string): Promise<void> {
  await expect(panel(page).locator('.al-footer')).toContainText(`${count} observations`);
  await expect(panel(page).locator('.al-feedback')).toContainText(feedback);
}

async function recordedOutcomes(page: Page): Promise<string[]> {
  return page.evaluate(() => {
    const raw = localStorage.getItem('al-engine:learner-record:v0.1');
    if (!raw) throw new Error('No browser-local learner record');
    return (JSON.parse(raw).observations as { outcome: string }[])
      .map(observation => observation.outcome.split('#').at(-1) ?? '');
  });
}

async function suppliedCode(page:Page,id:string):Promise<string> {
 const document=await(await page.request.get('/files/'+NOTEBOOK)).json();
 return document.cells.find((cell:{id:string})=>cell.id===id).source.join('');
}
async function runGuidedSteps(page:Page):Promise<void> {
 for(const id of ['district-code','dictionary-code','events-code','flatten-code','summary-code']) await runCell(page,id);
}
async function submit(page:Page):Promise<void> {
 const document=await(await page.request.get('/files/'+NOTEBOOK)).json();
 const index=document.cells.findIndex((cell:{id:string})=>cell.id==='submit');
 await page.locator(`.jp-Cell[data-windowed-list-index="${index}"]`).scrollIntoViewIfNeeded();
 await page.locator('.jp-Notebook').getByRole('button',{name:'Submit',exact:true}).click();
}

test('DHIS2: guided tables, retries, and success update the learner record', async ({ page },testInfo) => {
  await openPilot(page);
  await runCell(page,'submit');
  await submit(page);
  await expectObservation(page,1,'Not finished yet');
  await expect.poll(()=>recordedOutcomes(page)).toEqual(['Incomplete']);
  await expect(page.locator('.jp-Notebook')).toContainText('Not complete yet.');
  await runGuidedSteps(page);
  const summary=await suppliedCode(page,'summary-code');
  const summaryIndex=(await(await page.request.get('/files/'+NOTEBOOK)).json()).cells.findIndex((c:{id:string})=>c.id==='summary-code');
  const summaryCell=page.locator(`.jp-Cell[data-windowed-list-index="${summaryIndex}"]`);
  await expect(summaryCell).toContainText('Missing onset dates');
  await expect(summaryCell).toContainText('2021-10-18');
  await expect(summaryCell).toContainText('2021-11-04');
  await summaryCell.locator('.jp-OutputArea').screenshot({path:testInfo.outputPath('guided-summary.png')});
  await runCell(page,'summary-code',summary+'\nn_missing_onset = 0');
  await submit(page);
  await expectObservation(page,2,'Not yet correct');
  await expect(page.locator('.jp-Notebook')).toContainText('Check the district, date field, and summary.');
  await runCell(page,'summary-code',summary+'\nlast_onset = first_onset');
  await submit(page);
  await expectObservation(page,3,'Not yet correct');
  await runCell(page,'summary-code',summary);
  await submit(page);
  await expectObservation(page,4,'Correct. Recorded as evidence.');
  await expect.poll(()=>recordedOutcomes(page)).toEqual(['Incomplete','Incorrect','Incorrect','Correct']);
  await expect(page.locator('.jp-Notebook')).toContainText('Guided exploration complete.');
  await expect(achieved(page,'Explore a dataset with software')).toHaveCount(1);
  await expect(recommendation(page,'Explore the immunisation register')).toHaveCount(0);
  await page.reload();
  await expect(panel(page)).toBeVisible();
  await expect.poll(()=>recordedOutcomes(page)).toEqual(['Incomplete','Incorrect','Incorrect','Correct']);
});

test('DHIS2: repeated correct guided runs count as one exercise',async({page})=>{
 await openPilot(page);await runGuidedSteps(page);await runCell(page,'submit');
 await submit(page);await expectObservation(page,1,'Correct. Recorded as evidence.');
 await submit(page);await expectObservation(page,2,'Correct. Recorded as evidence.');
 await expect(achieved(page,'Explore a dataset with software')).toHaveCount(1);
});

test('DHIS2: missingno renders locally and preserves source blanks',async({page},testInfo)=>{
 const external:string[]=[];
 await page.context().route('**/*',route=>{
  if(new URL(route.request().url()).hostname==='127.0.0.1')return route.continue();
  external.push(route.request().url());return route.abort();
 });
 await openPilot(page);await runGuidedSteps(page);
 const plot=await suppliedCode(page,'missingness-code');
 // Fail the actual render if the reported deprecation recurs; do not hide warnings.
 const strictPlot=plot.replace('show_missingness_matrix(quality_view,',
  'import warnings\nfrom matplotlib import MatplotlibDeprecationWarning\nwith warnings.catch_warnings():\n    warnings.simplefilter("error", MatplotlibDeprecationWarning)\n    show_missingness_matrix(quality_view,');
 await runCell(page,'missingness-code',strictPlot);
 const document=await(await page.request.get('/files/'+NOTEBOOK)).json();
 const index=document.cells.findIndex((cell:{id:string})=>cell.id==='missingness-code');
 const visual=page.locator(`.jp-Cell[data-windowed-list-index="${index}"]`);
 const chart=visual.locator('.jp-OutputArea img[src^="data:image/svg+xml"]');
 await expect(chart).toHaveCount(1,{timeout:180000});
 await expect.poll(()=>chart.evaluate((img:HTMLImageElement)=>img.complete && img.naturalWidth>300 && img.naturalHeight>150)).toBe(true);
 await expect(visual).toContainText('Missing values');
 await expect(visual.locator('.jp-OutputArea')).toContainText('Rash onset date');
 await expect(visual.locator('.jp-OutputArea')).not.toContainText(/MatplotlibDeprecationWarning|Traceback/);
 await chart.screenshot({path:testInfo.outputPath('missingno-matrix.png')});
 await visual.locator('.jp-OutputArea').screenshot({path:testInfo.outputPath('missingno-full-output.png')});
 // Assert against the live Python state, not a duplicated plot fixture.
 const summary=await suppliedCode(page,'summary-code');
 await runCell(page,'summary-code',summary+'\nassert onset_rows[2]["onset"] == ""\nassert events[2]["dataValues"][0]["value"] == ""\nassert quality_view["Rash onset date"].isna().sum() == 1\nprint("Missingness pilot verified: one normalized blank; source unchanged.")');
 const summaryIndex=document.cells.findIndex((cell:{id:string})=>cell.id==='summary-code');
 await expect(page.locator(`.jp-Cell[data-windowed-list-index="${summaryIndex}"]`)).toContainText('Missingness pilot verified: one normalized blank; source unchanged.');
 expect(external).toEqual([]);
 await expect.poll(()=>recordedOutcomes(page)).toEqual([]);
});

test('DHIS2: three hints leave a correct attempt outside capability evidence',async({page})=>{
 await openPilot(page);
 for(let level=1;level<=3;level++){
  await panel(page).locator('.al-hint-button').click();
  if(level===3)await page.getByRole('dialog',{name:'This hint is close to the answer'}).getByRole('button',{name:'Show hint'}).click();
  await expect(panel(page).locator('.al-hint').last()).toContainText(`Hint ${level}`);
 }
 await runGuidedSteps(page);await runCell(page,'submit');await submit(page);
 await expectObservation(page,1,'Correct. Recorded, but with this much help it does not count as evidence.');
 await expect(achieved(page,'Explore a dataset with software')).toHaveCount(0);
});
