import { expect, test, Page } from '@playwright/test';

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
  const reflection=await reveal(page,"_reflection_section('form:unit-1'");
  await expect(reflection.locator('textarea')).toHaveCount(4);
  await reflection.locator('textarea').first().fill('I need the reporting period and the district sources.');
  await reflection.getByRole('button',{name:'Record',exact:true}).click();
  await expect(reflection).toContainText('Recorded in this browser.');
  await page.reload();await expect(page.locator('#al-engine-learning')).toBeVisible();
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('al-engine:learner-record:v0.1')!));
  expect(saved.reflections['form:unit-1'][0].answer).toContain('reporting period');
});
