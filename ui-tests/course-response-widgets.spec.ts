import { expect, test } from '@playwright/test';

async function expectChoicesDoNotOverlap(cell: import('@playwright/test').Locator) {
  const violations = await cell.locator('.course-quiz-card').evaluateAll((cards) =>
    cards.flatMap((card, cardIndex) => {
      const labels = [...card.querySelectorAll('.widget-radio-box label, .widget-checkbox .widget-label-basic')];
      return labels.flatMap((label, index) => {
        const text = label.querySelector('span') ?? label.firstChild;
        if (!text) return [`card ${cardIndex + 1}, option ${index + 1}: no text`];
        const range = document.createRange();
        range.selectNodeContents(text);
        const textBottom = Math.max(...[...range.getClientRects()].map((rect) => rect.bottom));
        const labelBottom = label.getBoundingClientRect().bottom;
        const nextTop = labels[index + 1]?.getBoundingClientRect().top ?? Infinity;
        return label.getBoundingClientRect().width > 0 &&
          labelBottom + 1 >= textBottom && nextTop + 1 >= textBottom
          ? [] : [`card ${cardIndex + 1}, option ${index + 1}: text overlaps next option`];
      });
    }));
  expect(violations).toEqual([]);
}

test('practice quiz presents choices as controls without scoring them', async ({ page }) => {
  await page.setViewportSize({ width: 1050, height: 850 });
  await page.goto('/lab/index.html?path=readings/ucsf/u00-n02-version3-form-library.ipynb');
  await expect(page.locator('.jp-Notebook')).toContainText('Unit 1 · Practice quiz');
  await expect(page.locator('.jp-Notebook')).not.toContainText('Quiz U01-N03');
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toHaveCount(1, { timeout: 180_000 });
  const quiz = page.locator('.jp-Notebook .jp-Cell').nth(2);
  await quiz.click();
  await page.keyboard.press('Shift+Enter');
  await expect(quiz.getByRole('radio')).toHaveCount(12, { timeout: 180_000 });
  await expect(quiz.getByRole('radio', { name: 'Choose one' })).toHaveCount(0);
  await expect(quiz.getByRole('radio', { checked: true })).toHaveCount(0);
  await expect(quiz.getByRole('checkbox')).toHaveCount(5);
  await expectChoicesDoNotOverlap(quiz);
  await quiz.getByRole('button', { name: 'Submit for feedback' }).click();
  await expect(quiz.locator('.jp-OutputArea').last()).toContainText('1. Choose an answer, then submit again.');
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
  const unit2 = page.locator('.jp-Notebook .jp-Cell').nth(6);
  await unit2.click();
  await page.keyboard.press('Shift+Enter');
  await expect(unit2.getByRole('button', { name: 'Submit for feedback' })).toBeVisible({ timeout: 180_000 });
  await expect(unit2.getByRole('radio', { name: 'Choose one' })).toHaveCount(0);
  await expect(unit2.getByRole('radio', { checked: true })).toHaveCount(0);
  await expectChoicesDoNotOverlap(unit2);
  for (const index of [10, 12, 14]) {
    const laterQuiz = page.locator('.jp-Notebook .jp-Cell').nth(index);
    await laterQuiz.click();
    await page.keyboard.press('Shift+Enter');
    const submit = laterQuiz.getByRole('button', { name: 'Submit for feedback' });
    await expect(submit).toBeVisible({ timeout: 180_000 });
    await expect(laterQuiz.getByRole('radio', { name: 'Choose one' })).toHaveCount(0);
    await expect(laterQuiz.getByRole('radio', { checked: true })).toHaveCount(0);
    await expectChoicesDoNotOverlap(laterQuiz);
    const firstChoice = laterQuiz.getByRole(index === 14 ? 'radio' : 'checkbox').first();
    await firstChoice.check();
    await submit.click();
    await expect(laterQuiz.locator('.jp-OutputArea').last()).toContainText('provisional practice feedback');
  }
  await quiz.getByRole('button', { name: 'Submit for feedback' }).click();
  await expect(quiz.locator('.jp-OutputArea').last()).toContainText('Unit 1 provisional practice feedback');
  const record = await page.evaluate(() => localStorage.getItem('al-engine:learner-record:v0.1'));
  expect(record ? JSON.parse(record).observations.length : 0).toBe(0);
});

test('case-study prompts each have a written response field', async ({ page }) => {
  await page.goto('/lab/index.html?path=readings/ucsf/u00-n02-version3-form-library.ipynb');
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  for (const [index, count] of [[4, 4], [8, 10]] as const) {
    const caseStudy = page.locator('.jp-Notebook .jp-Cell').nth(index);
    await caseStudy.click();
    await page.keyboard.press('Shift+Enter');
    await expect(caseStudy.locator('.jp-OutputArea textarea')).toHaveCount(count, { timeout: 180_000 });
    await caseStudy.locator('.jp-OutputArea textarea').first().fill('Check the case data and reporting context.');
    await expect(caseStudy.locator('.jp-OutputArea textarea').first()).toHaveValue('Check the case data and reporting context.');
  }
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

test('reading knowledge checks and case assignments provide entry fields', async ({ page }) => {
  for (const [filename, count] of [['u02-n02-knowledge-check', 3], ['u02-n08-assignment-2', 4]] as const) {
    await page.goto(`/lab/index.html?path=readings/ucsf/${filename}.ipynb`);
    await expect(page.locator('.jp-NotebookPanel:visible .jp-Notebook-ExecutionIndicator[data-status="idle"]'))
      .toHaveCount(1, { timeout: 180_000 });
    await expect(page.locator('.jp-Notebook:visible')).not.toContainText('Enter your response here.');
    const fields = page.locator('.jp-Notebook:visible .jp-Cell').nth(3);
    await fields.click();
    await page.keyboard.press('Shift+Enter');
    await expect(fields.locator('.jp-OutputArea textarea')).toHaveCount(count, { timeout: 180_000 });
  }
});
