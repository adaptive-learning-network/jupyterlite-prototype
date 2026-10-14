import { expect, test } from '@playwright/test';

test('Unit 1 lesson loads its visual without an external course server', async ({ page }) => {
  const externalCourseRequests: string[] = [];
  page.on('request', request => {
    if (/drive\.google\.com|docs\.google\.com|scribehow\.com|youtube\.com|urlblock\.php/.test(request.url())) {
      externalCourseRequests.push(request.url());
    }
  });

  await page.goto('/lab/index.html?path=readings/ucsf/u01-n02-lesson.ipynb');
  await expect(page.locator('.jp-Notebook h1').filter({ hasText: 'From data to decisions' })).toBeVisible();
  const overload = page.locator('.jp-Notebook img[alt="Laila faces data overload"]');
  await expect(overload).toBeVisible();
  await expect.poll(() => overload.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0))
    .toBe(true);
  expect(externalCourseRequests).toEqual([]);
});
