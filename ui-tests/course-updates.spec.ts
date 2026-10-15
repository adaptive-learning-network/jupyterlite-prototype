import { expect, test } from '@playwright/test';
test.use({serviceWorkers:'block'});
test('local review replaces a supplied copy while learner mode retains saved work',async({page})=>{
 let review=false;
 await page.route('**/jupyter-lite.json',async route=>{
  const response=await route.fetch();const config=await response.json();
  config['jupyter-config-data']={...config['jupyter-config-data'],alCourseReviewMode:review};
  await route.fulfill({response,json:config});
 });
 const path='notebooks/u00-n00-start-here.ipynb';
 const doc=await(await page.request.get('/files/'+path)).json();
 const title=doc.cells[0].source.join('').match(/^# (.+)$/m)![1];
 await page.goto(`/lab/index.html?path=${path}`);
 await expect(page.locator('#al-engine-learning')).toBeVisible();
 const record=await page.evaluate(()=>localStorage.getItem('al-engine:learner-record:v0.1'));
 async function edit(index:number,text:string){
  const cell=page.locator(`.jp-Cell[data-windowed-list-index="${index}"]`);
  await cell.scrollIntoViewIfNeeded();await cell.dblclick();await cell.locator('.cm-content').click();
  await page.keyboard.press('ControlOrMeta+a');await page.keyboard.insertText(text);
  await page.keyboard.press('Shift+Enter');await page.keyboard.press('ControlOrMeta+s');
  await expect(page.locator('.jp-mod-dirty')).toHaveCount(0);
 }
 await edit(0,'# Outdated review copy');
 await page.evaluate(path=>localStorage.setItem(`al-engine:course-copy:${path}`,'old-version'),path);
 review=true;await page.reload();
 await expect(page.locator('.jp-Notebook h1')).toContainText(title);
 expect(await page.evaluate(()=>localStorage.getItem('al-engine:learner-record:v0.1'))).toBe(record);
 review=false;await edit(2,'## My reflection\n\nLearner notes retained across updates.');
 await page.evaluate(path=>localStorage.setItem(`al-engine:course-copy:${path}`,'old-version'),path);
 await page.reload();await expect(page.locator('.jp-Notebook')).toContainText('Learner notes retained across updates.');
});
