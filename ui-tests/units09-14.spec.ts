import { expect, Page, test } from '@playwright/test';
import { readFileSync } from 'node:fs';

const EX = 'https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#';
const catalog = JSON.parse(readFileSync('app-assets/adaptive-learning/catalog.json', 'utf8'));
const scenarios = JSON.parse(readFileSync('test/fixtures/units09-14-scenarios.json', 'utf8')) as {
  unit: number; id: string; path: string;
  controls: {key: string; label: string; kind: string; options: [string, string][] | null}[];
  correct: Record<string, string | number | string[]>;
}[];

async function currentOutcomes(page: Page, id: string) {
  return page.evaluate(activity => {
    const record = JSON.parse(localStorage.getItem('al-engine:learner-record:v0.1')!);
    return record.observations.filter((o: {activity: string}) => o.activity === activity)
      .map((o: {outcome: string}) => o.outcome.split('#').at(-1));
  }, EX + 'act-' + id);
}

for (const scenario of scenarios) {
  test(`Unit ${scenario.unit}: choices, retries, recommendation, reflection and reload`, async ({ page }, testInfo) => {
    test.setTimeout(300_000);
    // Seed completed prerequisites, never the activity under test. This keeps
    // the harness about the workflow rather than answering the previous units.
    const prior = catalog.activities.filter((a: {iri: string; ordinal: number; rules: string[]}) =>
      a.rules.length && a.ordinal < scenario.unit + 6);
    await page.addInitScript(({ prior, audience }) => {
      const key = 'al-engine:learner-record:v0.1';
      if (localStorage.getItem(key)) return;
      localStorage.setItem(key, JSON.stringify({ schema: 'al-learner-record/0.1', learner: 'urn:uuid:11111111-1111-4111-8111-111111111111',
        audience, guidance: {}, observations: prior.map((a: {iri: string}) => ({
          iri: `urn:uuid:${crypto.randomUUID()}`, activity: a.iri, object: a.iri + '-exercise',
          action: 'https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#OutputValidated',
          outcome: 'https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#Correct',
          guidanceLevel: 0, language: 'python', at: '2026-10-15T12:00:00Z'
        })) }));
    }, { prior, audience: catalog.audiences[0].iri });
    await page.setViewportSize({ width: 1050, height: 850 });
    expect((await page.request.get('/files/' + scenario.path)).ok()).toBe(true);
    await page.goto(`/lab/index.html?path=${scenario.path}`);
    const panel = page.locator('#al-engine-learning');
    await expect(panel).toBeVisible();
    await expect(panel.locator('.al-rec').filter({ hasText: `Unit ${scenario.unit}:` })).toHaveCount(1);
    await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]')).toHaveCount(1, { timeout: 180_000 });
    const comic = page.locator('.jp-Notebook img').first();
    await expect.poll(() => comic.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0), { timeout: 30_000 }).toBe(true);
    expect(await page.locator('.jp-Notebook img').count()).toBeGreaterThanOrEqual(scenario.unit === 5 ? 1 : 2);
    await expect.poll(() => page.locator('.jp-Notebook img').evaluateAll(images =>
      images.every(img => (img as HTMLImageElement).complete && (img as HTMLImageElement).naturalWidth > 0)), { timeout: 30_000 }).toBe(true);
    await page.screenshot({ path: testInfo.outputPath('intro.png') });
    // Run All also exposes the reflection controls. The first exercise attempt
    // is intentionally untouched, so it must be recorded as incomplete.
    await page.getByRole('menuitem', { name: 'Run', exact: true }).click();
    await page.getByRole('menuitem', { name: 'Run All Cells', exact: true }).click();
    await expect.poll(() => currentOutcomes(page, scenario.id), { timeout: 180_000 }).toEqual(['Incomplete']);

    // Scroll back to the setup output; JupyterLab virtualizes off-screen cells.
    await page.locator('.jp-Notebook').hover();
    await page.mouse.wheel(0, -10000);
    const setup = page.locator('.jp-CodeCell').filter({ hasText: '# Run once to inspect the data and display the controls.' });
    async function revealSetup() {
      await page.locator('.jp-Notebook').hover();
      await page.mouse.wheel(0, -10000);
      await expect.poll(async () => {
        if (await setup.count()) return true;
        await page.mouse.wheel(0, 400);
        return false;
      }).toBe(true);
      await setup.scrollIntoViewIfNeeded();
    }
    await revealSetup();
    await expect(setup.getByRole('listbox').or(setup.getByRole('combobox')).or(setup.getByRole('spinbutton'))).not.toHaveCount(0);
    async function choose(correct: boolean) {
      await revealSetup();
      for (const control of scenario.controls) {
        let value = scenario.correct[control.key];
        // Make exactly the first criterion wrong; keep all fields answered.
        if (!correct && control === scenario.controls[0]) {
          value = typeof value === 'number' ? value + 1 : Array.isArray(value)
            ? [control.options!.slice().reverse().find(([, id]) => !(value as string[]).includes(id))?.[1] ?? control.options![0][1]]
            : control.options!.find(([, id]) => id !== value)![1];
        }
        const input = setup.getByLabel(control.label, { exact: true });
        if (control.kind === 'integer') await input.fill(String(value));
        else {
          // ipywidgets uses display labels as native option values, and puts
          // nonbreaking spaces in option text. Map semantic IDs to native values.
          const values = Array.isArray(value) ? value : [String(value)];
          await input.selectOption(values.map(value => ({ value: control.options!.find(([, id]) => id === value)![0] })));
        }
      }
    }
    async function check() {
      const exercise = page.locator('.jp-CodeCell').filter({ hasText: '# Check my work: run after making your choices above.' });
      await exercise.click();
      await expect(exercise).toHaveClass(/jp-mod-active/);
      await page.keyboard.press('Shift+Enter');
    }
    await choose(false);
    await page.screenshot({ path: testInfo.outputPath('controls.png') });
    await check();
    await expect.poll(() => currentOutcomes(page, scenario.id)).toEqual(['Incomplete', 'Incorrect']);
    const exerciseOutput = page.locator('.jp-CodeCell').filter({ hasText: '# Check my work: run after making your choices above.' }).locator('.jp-OutputArea');
    if (scenario.unit === 5) {
      await expect(exerciseOutput).toContainText('Role access denied for:');
      await expect(exerciseOutput).not.toContainText('Training contact A');
    }
    if (scenario.unit === 7) await expect(exerciseOutput.getByRole('cell', { name: 'True', exact: true })).toHaveCount(3);
    await check();
    await expect.poll(() => currentOutcomes(page, scenario.id)).toEqual(['Incomplete', 'Incorrect', 'Incorrect']);
    await choose(true);
    await check();
    await expect.poll(() => currentOutcomes(page, scenario.id)).toEqual(['Incomplete', 'Incorrect', 'Incorrect', 'Correct']);
    if (scenario.unit === 7) {
      await expect(exerciseOutput.getByRole('cell', { name: 'True', exact: true })).toHaveCount(1);
      await expect(exerciseOutput.getByRole('cell', { name: 'False', exact: true })).toHaveCount(5);
    }
    await expect(panel.locator('.al-gap.al-achieved').filter({ hasText: catalog.capabilities.find((c: {iri: string}) => c.iri === EX + 'cap-' + scenario.id).label })).toHaveCount(1);
    if (scenario.unit < 14) await expect(panel.locator('.al-rec').filter({ hasText: `Unit ${scenario.unit + 1}:` })).toHaveCount(1);

    await page.locator('.jp-Notebook').hover();
    await page.mouse.wheel(0, 10000);
    const sourceNotebook = await (await page.request.get('/files/' + scenario.path)).json();
    const reflectionIndex = sourceNotebook.cells.findIndex((c: {id: string}) => c.id === 'reflection-fields');
    expect(reflectionIndex).toBeGreaterThanOrEqual(0);
    const reflection = page.locator(`.jp-CodeCell[data-windowed-list-index="${reflectionIndex}"]`);
    await page.mouse.wheel(0, -100000);
    await expect.poll(async () => {
      if (await reflection.count()) return true;
      await page.mouse.wheel(0, 800);
      return false;
    }).toBe(true);
    await reflection.scrollIntoViewIfNeeded();
    await expect(reflection.locator('textarea')).toHaveCount(2);
    await reflection.locator('textarea').first().fill(`My decision for unit ${scenario.unit}.`);
    await reflection.getByRole('button', { name: 'Record', exact: true }).click();
    await expect(reflection).toContainText('Recorded in this browser.');
    await page.screenshot({ path: testInfo.outputPath('result-and-reflection.png') });
    await page.reload();
    await expect(panel).toBeVisible();
    await expect.poll(() => currentOutcomes(page, scenario.id)).toEqual(['Incomplete', 'Incorrect', 'Incorrect', 'Correct']);
    const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('al-engine:learner-record:v0.1')!));
    expect(saved.reflections['exercise:' + scenario.id][0].answer).toBe(`My decision for unit ${scenario.unit}.`);
  });
}
