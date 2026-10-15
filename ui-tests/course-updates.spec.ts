import { expect, test } from '@playwright/test';

test.use({ serviceWorkers: 'block' });

test('local review replaces an old lesson while learner mode retains saved work', async ({ page }) => {
  let review = false;
  await page.route('**/jupyter-lite.json', async route => {
    const response = await route.fetch();
    const config = await response.json();
    config['jupyter-config-data'] = { ...config['jupyter-config-data'], alCourseReviewMode: review };
    await route.fulfill({ response, json: config });
  });
  const path = 'readings/ucsf/u01-n02-lesson.ipynb';
  await page.goto(`/lab/index.html?path=${path}`);
  await expect(page.locator('#al-engine-learning')).toBeVisible();
  await expect(page.locator('.jp-Notebook .jp-Cell')).toHaveCount(6);
  const record = await page.evaluate(() => localStorage.getItem('al-engine:learner-record:v0.1'));

  async function editMarkdown(index: number, text: string) {
    const cell = page.locator(`.jp-Notebook .jp-Cell[data-windowed-list-index="${index}"]`);
  await cell.scrollIntoViewIfNeeded();
    await cell.dblclick();
    await cell.locator('.cm-content').click();
    await page.keyboard.press('ControlOrMeta+a');
    await page.keyboard.insertText(text);
    await page.keyboard.press('Shift+Enter');
    await page.keyboard.press('ControlOrMeta+s');
    await expect(page.locator('.jp-mod-dirty')).toHaveCount(0);
  }

  await editMarkdown(1, '## 1.2 Unit Slides\n\nSource media: old explanation. Original PDF link.');
  await editMarkdown(2, '## Local response section\n\nEnter your response here.');
  await page.evaluate(path => localStorage.setItem(`al-engine:course-copy:${path}`, 'old-version'), path);
  review = true;
  await page.reload();
  await expect(page.locator('.jp-Notebook')).not.toContainText('Source media:');
  await expect(page.locator('.jp-Notebook')).toContainText("Reflect on Laila's report");
  await expect(page.locator('.jp-Notebook').getByRole('link', { name: 'Explore the Unit 1 slides' })).toBeVisible();
  const fields = page.locator('.jp-Notebook .jp-Cell').nth(3);
  await expect(fields).toHaveClass(/jp-CodeCell/);
  expect(await page.evaluate(() => localStorage.getItem('al-engine:learner-record:v0.1'))).toBe(record);

  review = false;
  await editMarkdown(2, '## My reflection\n\nLearner notes retained across updates.');
  await page.evaluate(path => localStorage.setItem(`al-engine:course-copy:${path}`, 'old-version'), path);
  await page.reload();
  await expect(page.locator('.jp-Notebook')).toContainText('Learner notes retained across updates.');
});
