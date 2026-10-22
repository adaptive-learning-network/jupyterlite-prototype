import { expect, test } from '@playwright/test';

test('one course path contains the lesson, local visuals and slide previews', async ({ page }) => {
  const external: string[] = [];
  page.on('request', request => { if (/drive\.google|docs\.google|scribehow|urlblock\.php/.test(request.url())) external.push(request.url()); });
  expect((await page.request.get('/files/notebooks/u01-n01-data-to-decision.ipynb')).ok()).toBe(true);
  expect((await page.request.get('/files/readings/ucsf/u01-n02-lesson.ipynb')).status()).toBe(404);
  expect((await page.request.get('/files/exercises/python/02-explore-dataset.ipynb')).status()).toBe(404);
  await page.goto('/lab/index.html?path=notebooks/u01-n01-data-to-decision.ipynb');
  await expect(page.locator('#al-engine-learning')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Unit 1–2 readings', exact: true })).toHaveCount(0);
  await expect(page.getByRole('heading',{name:'From data to a public health decision',exact:true})).toBeVisible();
  const concepts=page.locator('.jp-MarkdownCell').filter({hasText:'Explore the concepts further'});
  await page.locator('.jp-Notebook').hover();
  await expect.poll(async()=> { if(await concepts.count()) return true; await page.mouse.wheel(0,500); return false; }).toBe(true);
  await concepts.scrollIntoViewIfNeeded();
  await concepts.locator('summary').click();
  for (const alt of ['Laila faces data overload', 'What public health informatics does', 'From data to wisdom']) {
    const visual=concepts.locator(`img[alt="${alt}"]`);
    await expect(visual).toHaveCount(1);
    await expect.poll(() => visual.evaluate((el: HTMLImageElement) => el.complete && el.naturalWidth>0)).toBe(true);
    expect(await visual.getAttribute('src')).not.toMatch(/https?:\/\//);
  }
  await page.locator('.jp-Notebook').hover();
  await page.mouse.wheel(0,-100000);
  const slides=page.locator('.jp-MarkdownCell').filter({hasText:'Unit 1 PDF pages 1'}).first();
  await expect.poll(async()=> { if(await slides.count()) return true; await page.mouse.wheel(0,1000); return false; }).toBe(true);
  await slides.locator('summary').first().click();
  const pdf=slides.getByRole('link',{name:'Open this PDF page'}).first();
  await expect(pdf).toHaveAttribute('href',/files\/notebooks\/assets\/unit-1-version-2-slides\.pdf/);
  expect((await page.request.get((await pdf.getAttribute('href'))!)).ok()).toBe(true);
  expect(external).toEqual([]);
});
