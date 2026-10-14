import { expect, test } from '@playwright/test';

test('Unit 1 lesson loads every course visual locally', async ({ page }) => {
  const externalCourseRequests: string[] = [];
  page.on('request', request => {
    if (/drive\.google\.com|docs\.google\.com|scribehow\.com|youtube\.com|urlblock\.php/.test(request.url())) {
      externalCourseRequests.push(request.url());
    }
  });

  await page.goto('/lab/index.html?path=readings/ucsf/u01-n02-lesson.ipynb');
  await expect(page.locator('.jp-Notebook h1').filter({ hasText: 'From data to decisions' })).toBeVisible();
  for (const alt of [
    'Laila faces data overload',
    'What public health informatics does',
    'How informaticians support a health system',
    'From data to wisdom',
    'The public health surveillance cycle',
    'Creating value from surveillance data'
  ]) {
    const visual = page.locator(`.jp-Notebook img[alt="${alt}"]`);
    await expect(visual).toHaveCount(1);
    await expect.poll(() => visual.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0))
      .toBe(true);
    expect(await visual.getAttribute('src')).not.toMatch(/^https?:/);
  }
  await expect(page.locator('.jp-Notebook')).not.toContainText('Open source illustration');
  await expect(page.locator('.jp-Notebook h2').filter({ hasText: 'References' })).toHaveCount(1);
  await expect(page.locator('.jp-Notebook')).not.toContainText('Source and visual attribution');
  expect(externalCourseRequests).toEqual([]);
});
