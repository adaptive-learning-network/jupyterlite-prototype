import { expect, test, Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

async function reveal(page: Page, phrase: string) {
  const doc=await (await page.request.get('/files/notebooks/u01-n01-data-to-decision.ipynb')).json();
  const index=doc.cells.findIndex((c: {source: string[]})=>c.source.join('').includes(phrase));
  expect(index).toBeGreaterThanOrEqual(0);
  const cell=page.locator(`.jp-CodeCell[data-windowed-list-index="${index}"]`);
  await page.locator('.jp-Notebook').hover();await page.mouse.wheel(0,-100000);
  await expect.poll(async()=> { if(await cell.count()) return true; await page.mouse.wheel(0,1000); return false; }).toBe(true);
  await cell.scrollIntoViewIfNeeded();return cell;
}

test('the integrated Unit 1 quiz gives feedback and case reflections record in the same notebook', async ({page})=>{
  test.setTimeout(300000);await page.setViewportSize({width:1050,height:850});
  await page.goto('/lab/index.html?path=notebooks/u01-n01-data-to-decision.ipynb');
  await expect(page.locator('#al-engine-learning')).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toHaveCount(1,{timeout:180000});
  await page.getByRole('menuitem',{name:'Run',exact:true}).click();
  await page.getByRole('menuitem',{name:'Run All Cells',exact:true}).click();
  const quiz=await reveal(page,'# Run this cell to choose answers for Unit 1.');
  await expect(quiz.locator('input[type="radio"]')).not.toHaveCount(0);
  await expect(quiz.getByText('Choose one',{exact:true})).toHaveCount(0);
  await quiz.getByRole('button',{name:'Submit for feedback',exact:true}).click();
  await expect(quiz).toContainText('Choose an answer, then submit again.');
  const cards=quiz.locator('.course-quiz-card');
  for(let i=0;i<await cards.count();i++) {
    const card=cards.nth(i);
    const inputs=card.locator('input[type="radio"], input[type="checkbox"]');
    await inputs.first().check();
  }
  await quiz.getByRole('button',{name:'Submit for feedback',exact:true}).click();
  await expect(quiz).toContainText(/Correct|Incorrect/);
  const reflection=await reveal(page,"_reflection_section('exercise:u01-n01'");
  await expect(reflection.locator('textarea')).toHaveCount(1);
  await reflection.locator('textarea').first().fill('I need the reporting period and the district sources.');
  await reflection.getByRole('button',{name:'Record',exact:true}).click();
  await expect(reflection).toContainText('Recorded in this browser.');
  const downloadEvent = page.waitForEvent('download');
  await page.locator('#al-engine-learning').getByRole('button', {name:'Download reflections', exact:true}).click();
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toBe('recorded-reflections.txt');
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream!) chunks.push(Buffer.from(chunk));
  const text = Buffer.concat(chunks).toString('utf8');
  expect(text).toContain('I need the reporting period and the district sources.');
  expect(text).toContain('Which district change supports your chosen action');
  expect(text).toContain('Recorded:');
  expect(text).toContain('does not provide automatic restoration');
  await page.locator('#al-engine-learning').getByRole('button', {name:'Reset',exact:true}).click();
  const dialog = page.getByRole('dialog');
  await expect(dialog).toContainText('recorded reflections');
  await expect(dialog).toContainText('Download reflections');
  await dialog.getByRole('button', {name:'Cancel',exact:true}).click();
  await page.reload();await expect(page.locator('#al-engine-learning')).toBeVisible();
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('al-engine:learner-record:v0.1')!));
  expect(saved.reflections['exercise:u01-n01'][0].answer).toContain('reporting period');
  expect(saved.observations).toHaveLength(0);
});

for (const scenario of ['wording', 'meaning', 'legacy']) {
 const differentMeaning = scenario === 'meaning';
 const legacy = scenario === 'legacy';
 test(`reflection update preserves ${legacy ? 'legacy answer migration' : differentMeaning ? 'a different question version without inheriting its answer' : 'stable identity across wording edits and prior writing'}`, async ({page}) => {
  test.setTimeout(300000);
  const audience = JSON.parse(readFileSync('app-assets/adaptive-learning/catalog.json','utf8')).audiences[0].iri;
  const prompt = JSON.parse(readFileSync('scripts/reflection_questions.json','utf8'))['exercise:u01-n01'][0].prompt;
  await page.addInitScript(({differentMeaning, legacy, prompt, audience}) => {
   localStorage.setItem('al-engine:learner-record:v0.1',JSON.stringify({schema:'al-learner-record/0.1',learner:'urn:uuid:11111111-1111-4111-8111-111111111111',audience,guidance:{},observations:[],reflections:{
    'exercise:u01-n01':[
     {...(legacy ? {} : {id:'q1',version:differentMeaning ? 2 : 1}),prompt:legacy ? prompt : 'Earlier wording kept for review?',answer:'My earlier recorded reasoning.',savedAt:'2026-10-21T12:00:00Z'},
     {prompt:'Retired legacy question?',answer:'Retired answer remains available.',savedAt:'2026-10-20T12:00:00Z'}]
   }}));
  },{differentMeaning,legacy,prompt,audience});
  await page.goto('/lab/index.html?path=notebooks/u01-n01-data-to-decision.ipynb');
  await expect(page.locator('#al-engine-learning')).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toHaveCount(1,{timeout:180000});
  await page.getByRole('menuitem',{name:'Run',exact:true}).click();
  await page.getByRole('menuitem',{name:'Run All Cells',exact:true}).click();
  const cell=await reveal(page,"_reflection_section('exercise:u01-n01'");
  const answer=cell.locator('textarea');
  await expect(answer).toHaveValue(differentMeaning ? '' : 'My earlier recorded reasoning.');
  await expect(cell).toContainText('Earlier responses remain');
  await answer.fill('My updated reasoning after review.');
  await cell.getByRole('button',{name:'Record',exact:true}).click();
  await expect(cell).toContainText('Recorded in this browser.');
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('al-engine:learner-record:v0.1')!).reflections['exercise:u01-n01']);
  const serialized=JSON.stringify(saved);
  expect(serialized).toContain('My earlier recorded reasoning.');
  expect(serialized).toContain('Retired answer remains available.');
  expect(serialized).toContain('My updated reasoning after review.');
  expect(saved).toHaveLength(differentMeaning ? 3 : 2);
  const event=page.waitForEvent('download');
  await page.locator('#al-engine-learning').getByRole('button',{name:'Download reflections',exact:true}).click();
  const stream=await (await event).createReadStream();const chunks:Buffer[]=[];
  for await(const chunk of stream!)chunks.push(Buffer.from(chunk));
  const text=Buffer.concat(chunks).toString('utf8');
  expect(text).toContain('My earlier recorded reasoning.');expect(text).toContain('My updated reasoning after review.');
  expect(text).toContain('Retired answer remains available.');
 });
}
