import { expect, Page, test } from '@playwright/test';

// Each test gets a fresh browser context. These scenarios operate the real
// JupyterLite notebook and Learning panel without asking a tester to solve it.
const NOTEBOOK = 'exercises/python/07-dhis2-query.ipynb';

const answer = [
  'units = api.get("/api/organisationUnits")["organisationUnits"]',
  'org_unit = next(u["id"] for u in units if u["displayName"] == "Kambia District")',
  'elements = api.get("/api/dataElements")["dataElements"]',
  'onset_element = next(d["id"] for d in elements if d["displayName"] == "Date of rash onset")',
  'events = api.get("/api/tracker/events", {"program": "P_MEASLES", "orgUnit": org_unit})["events"]',
  'onsets = [v["value"] for e in events for v in e["dataValues"] if v["dataElement"] == onset_element]',
  'n_cases = len(events)',
  'n_missing_onset = sum(not value for value in onsets)',
  'first_onset = min(value for value in onsets if value)',
  'last_onset = max(value for value in onsets if value)'
].join('\n');

const panel = (page: Page) => page.locator('#al-engine-learning');
const recommendation = (page: Page, title: string) => panel(page).locator('.al-rec').filter({ hasText: title });
const achieved = (page: Page, capability: string) => panel(page).locator('.al-gap.al-achieved').filter({ hasText: capability });

async function openPilot(page: Page): Promise<void> {
  await page.goto(`/lab/index.html?path=${NOTEBOOK}`);
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook .jp-Cell').nth(2)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  await runCell(page, 1);
}

async function runCell(page: Page, index: number, source?: string): Promise<void> {
  const cell = page.locator('.jp-Notebook .jp-Cell').nth(index);
  await cell.locator('.cm-content').click();
  if (source !== undefined) {
    await page.keyboard.press('ControlOrMeta+a');
    await page.keyboard.type(source);
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

test('DHIS2: multiple retries are recorded and change the recommendation only after success', async ({ page }) => {
  await openPilot(page);
  await expect(recommendation(page, 'Explore the immunisation register')).toHaveCount(1);

  await runCell(page, 2);
  await expectObservation(page, 1, 'Not finished yet');
  await expect.poll(() => recordedOutcomes(page)).toEqual(['Incomplete']);

  await runCell(page, 2, answer.replace('n_missing_onset = sum(not value for value in onsets)', 'n_missing_onset = 0'));
  await expectObservation(page, 2, 'Not yet correct');
  await expect.poll(() => recordedOutcomes(page)).toEqual(['Incomplete', 'Incorrect']);
  await expect(recommendation(page, 'Explore the immunisation register')).toContainText('not yet demonstrated');
  await expect(achieved(page, 'Explore a dataset with software')).toHaveCount(0);

  await runCell(page, 2, answer.replace(
    'last_onset = max(value for value in onsets if value)',
    'last_onset = min(value for value in onsets if value)'
  ));
  await expectObservation(page, 3, 'Not yet correct');
  await expect.poll(() => recordedOutcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Incorrect']);
  await expect(recommendation(page, 'Explore the immunisation register')).toHaveCount(1);

  await runCell(page, 2, answer);
  await expectObservation(page, 4, 'Correct. Recorded as evidence.');
  await expect.poll(() => recordedOutcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Incorrect', 'Correct']);
  await expect(achieved(page, 'Explore a dataset with software')).toHaveCount(1);
  await expect(recommendation(page, 'Filter the records you need')).toHaveCount(1);
  await expect(recommendation(page, 'Explore the immunisation register')).toHaveCount(0);

  await page.reload();
  await expect(panel(page)).toBeVisible();
  await expect.poll(() => recordedOutcomes(page)).toEqual(['Incomplete', 'Incorrect', 'Incorrect', 'Correct']);
  await expect(recommendation(page, 'Filter the records you need')).toHaveCount(1);
});

test('DHIS2: repeated correct attempts record observations but count as one exercise', async ({ page }) => {
  await openPilot(page);
  await runCell(page, 2, answer);
  await expectObservation(page, 1, 'Correct. Recorded as evidence.');
  await expect(achieved(page, 'Explore a dataset with software')).toHaveCount(1);

  await runCell(page, 2, answer);
  await expectObservation(page, 2, 'Correct. Recorded as evidence.');
  await expect(achieved(page, 'Explore a dataset with software')).toHaveCount(1);
});

test('DHIS2: three hints leave a correct attempt outside capability evidence', async ({ page }) => {
  await openPilot(page);
  for (let level = 1; level <= 3; level++) {
    const hint = panel(page).locator('.al-hint-button');
    await hint.click();
    if (level === 3) {
      await page.getByRole('dialog', { name: 'This hint is close to the answer' })
        .getByRole('button', { name: 'Show hint' }).click();
    }
    await expect(panel(page).locator('.al-hint').last()).toContainText(`Hint ${level}`);
  }

  await runCell(page, 2, answer);
  await expectObservation(page, 1, 'Correct. Recorded, but with this much help it does not count as evidence.');
  await expect(achieved(page, 'Explore a dataset with software')).toHaveCount(0);
  await expect(recommendation(page, 'Explore the immunisation register')).toContainText('not yet demonstrated');
});

test('final notebook displays an exported learner graph without adding an observation', async ({ page }) => {
  await page.goto('/lab/index.html?path=exercises/python/08-my-learning-record.ipynb');
  await expect(panel(page)).toBeVisible();
  await expect(page.locator('.jp-Notebook .jp-Cell').nth(2)).toBeVisible();
  await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]'))
    .toBeVisible({ timeout: 180_000 });
  await runCell(page, 1);
  await runCell(page, 2);
  await expect(page.locator('.jp-OutputArea').last()).toContainText('No learner-record*.nq file was found');

  const graph = [
    '<urn:al:graph:11111111-1111-4111-8111-111111111111:evidence> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#LearningGraph> <urn:al:graph:11111111-1111-4111-8111-111111111111:derived> .',
    '<urn:uuid:22222222-2222-4222-8222-222222222222> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#Observation> <urn:al:graph:11111111-1111-4111-8111-111111111111:evidence> .',
    '<urn:uuid:22222222-2222-4222-8222-222222222222> <https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#outcome> <https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#Correct> <urn:al:graph:11111111-1111-4111-8111-111111111111:evidence> .'
  ].join('\n') + '\n';
  await runCell(page, 2, [
    'from pathlib import Path',
    `Path("learner-record-demo.nq").write_text(${JSON.stringify(graph)}, encoding="utf-8")`,
    'from IPython.display import Markdown, display',
    'display(Markdown(render_report([(path.name, path.read_text(encoding="utf-8")) for path in find_exports()])))'
  ].join('\n'));
  await expect(page.locator('.jp-OutputArea').last()).toContainText('Your learning record');
  await expect(page.locator('.jp-OutputArea').last()).toContainText('Correct');
  await expect(panel(page).locator('.al-footer')).toContainText('0 observations');
});
