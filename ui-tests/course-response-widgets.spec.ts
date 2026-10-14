import { expect, test } from '@playwright/test';

test('practice quiz presents choices as controls without scoring them', async ({ page }) => {
  await page.goto('/lab/index.html?path=readings/ucsf/u00-n02-version3-form-library.ipynb');
  await expect(page.locator('.jp-Notebook')).toContainText('Unit 1 · Practice quiz');
  await expect(page.locator('.jp-Notebook')).not.toContainText('Quiz U01-N03');
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  const quiz = page.locator('.jp-Notebook .jp-Cell').nth(2);
  await quiz.click();
  await page.keyboard.press('Shift+Enter');
  await expect(quiz.getByRole('radio')).toHaveCount(15, { timeout: 180_000 });
  await expect(quiz.getByRole('checkbox')).toHaveCount(5);
  await quiz.getByRole('radio', { name: 'They replace epidemiologists with AI.' }).check();
  await quiz.getByRole('checkbox', { name: 'A skilled workforce' }).check();
  await quiz.getByRole('button', { name: 'Submit for feedback' }).click();
  await expect(quiz.locator('.jp-OutputArea').last()).toContainText('1. Incorrect.');
  await expect(quiz.locator('.jp-OutputArea').last()).toContainText('2. Incorrect.');
  await quiz.getByRole('radio', { name: 'They improve data collection, quality, and analysis for faster interpretation.' }).check();
  await quiz.getByRole('checkbox', { name: 'Organization-wide informatics vision, policy, and governance' }).check();
  await quiz.getByRole('checkbox', { name: 'Effective, interoperable information systems' }).check();
  await quiz.getByRole('button', { name: 'Submit for feedback' }).click();
  await expect(quiz.locator('.jp-OutputArea').last()).toContainText('1. Correct.');
  await expect(quiz.locator('.jp-OutputArea').last()).toContainText('2. Correct.');
  const unit2 = page.locator('.jp-Notebook .jp-Cell').nth(5);
  await unit2.click();
  await page.keyboard.press('Shift+Enter');
  await expect(unit2.getByRole('button', { name: 'Submit for feedback' })).toBeVisible({ timeout: 180_000 });
  for (const index of [8, 10, 12]) {
    const laterQuiz = page.locator('.jp-Notebook .jp-Cell').nth(index);
    await laterQuiz.click();
    await page.keyboard.press('Shift+Enter');
    const submit = laterQuiz.getByRole('button', { name: 'Submit for feedback' });
    await expect(submit).toBeVisible({ timeout: 180_000 });
    const firstChoice = laterQuiz.getByRole(index === 12 ? 'radio' : 'checkbox').nth(index === 12 ? 1 : 0);
    await firstChoice.check();
    await submit.click();
    await expect(laterQuiz.locator('.jp-OutputArea').last()).toContainText('provisional practice feedback');
  }
  await quiz.getByRole('button', { name: 'Submit for feedback' }).click();
  await expect(quiz.locator('.jp-OutputArea').last()).toContainText('Unit 1 provisional practice feedback');
  const record = await page.evaluate(() => localStorage.getItem('al-engine:learner-record:v0.1'));
  expect(record ? JSON.parse(record).observations.length : 0).toBe(0);
});

test('Unit 1 lesson offers text fields for local reflection', async ({ page }) => {
  await page.goto('/lab/index.html?path=readings/ucsf/u01-n02-lesson.ipynb');
  await expect(page.locator('.jp-Notebook')).toContainText("Reflect on Laila's report");
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  const reflection = page.locator('.jp-Notebook .jp-Cell').nth(3);
  await reflection.click();
  await page.keyboard.press('Shift+Enter');
  await expect(reflection.locator('.jp-OutputArea textarea')).toHaveCount(2, { timeout: 180_000 });
  await reflection.locator('.jp-OutputArea textarea').first().fill('Check completeness before acting.');
  await reflection.getByRole('button', { name: 'Show my reflection' }).click();
  await expect(reflection).toContainText('Check completeness before acting.');
});
