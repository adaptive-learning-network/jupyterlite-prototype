// Live, read-only notebook output. No Python execution or exported file needed.
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { NotebookActions } from '@jupyterlab/notebook';
import { Widget } from '@lumino/widgets';
import { assess, Catalog, OUTCOME, STATUS } from '../engine';
import { LearnerStore } from './store';

const MIME = 'application/vnd.al.learner-record+json';
type Context = { catalog: Catalog; store: LearnerStore };

function element(tag: string, text = ''): HTMLElement {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}

class RecordView extends Widget {
  private context?: Context;

  constructor(private readonly ready: Promise<Context>) {
    super();
    this.addClass('al-RecordView');
    this.node.setAttribute('aria-label', 'Your learning record');
  }

  async renderModel(): Promise<void> {
    try {
      if (!this.context) {
        this.context = await this.ready;
        if (this.isDisposed) return;
        this.context.store.changed.connect(this.render, this);
      }
      this.render();
    } catch {
      this.node.replaceChildren(element('p', 'Your record could not be displayed. Reload this page to try again.'));
    }
  }

  dispose(): void {
    this.context?.store.changed.disconnect(this.render, this);
    super.dispose();
  }

  private render(): void {
    if (this.isDisposed || !this.context) return;
    const { catalog, store } = this.context;
    const record = store.record;
    const assessment = assess(catalog, record);
    const label = (iri?: string) => catalog.activities.find(a => a.iri === iri)?.title ??
      catalog.capabilities.find(c => c.iri === iri)?.label ??
      catalog.levels.find(l => l.iri === iri)?.label ?? 'Not assessed';
    const states: Record<string, string> = {
      [STATUS.demonstrated]: 'Demonstrated',
      [STATUS.notAssessed]: 'Not assessed',
      [STATUS.developmentOpportunity]: 'Keep practising',
      [STATUS.reportedNeedsConfirmation]: 'Self-reported; needs confirmation'
    };
    const outcomes: Record<string, string> = {
      [OUTCOME.correct]: 'Correct', [OUTCOME.incorrect]: 'Not yet correct',
      [OUTCOME.incomplete]: 'Incomplete', [OUTCOME.completed]: 'Completed'
    };
    const refresh = element('button', 'Refresh');
    refresh.className = 'jp-Button';
    refresh.onclick = () => this.render();
    this.node.replaceChildren(refresh,
      element('p', `${record.observations.length} recorded attempts. This view updates as you practise.`));
    if (!store.persistent) this.node.append(element('p', 'Browser storage is unavailable. This record lasts only for this page. Export evidence copies scored progress; Download reflections copies recorded writing. Download notebook edits separately.'));
    const table = (title: string, headers: string[], rows: string[][], empty: string) => {
      const section = element('section');
      section.append(element('h2', title));
      if (!rows.length) section.append(element('p', empty));
      else {
        const scroll = element('div');
        scroll.className = 'al-record-table';
        scroll.tabIndex = 0;
        const grid = document.createElement('table');
        const head = grid.createTHead().insertRow();
        for (const text of headers) {
          const th = document.createElement('th');
          th.scope = 'col'; th.textContent = text; head.append(th);
        }
        const body = grid.createTBody();
        for (const row of rows) {
          const tr = body.insertRow();
          for (const text of row) tr.insertCell().textContent = text;
        }
        scroll.append(grid); section.append(scroll);
      }
      this.node.append(section);
    };
    table('Your attempts', ['When', 'Activity', 'Result', 'Hints used', 'Mode', 'Case', 'Complete submission'],
      [...record.observations].reverse().map(o => [new Date(o.at).toLocaleString(), label(o.activity), outcomes[o.outcome] ?? 'Recorded', String(o.guidanceLevel), o.attempt?.mode ?? 'Earlier task', o.attempt?.taskId ?? '', o.attempt ? String(o.attempt.submissions) : '']),
      'No attempts recorded yet. Submit an exercise answer, then return here.');
    this.node.append(element('p', 'Progress reflects the exercises attempted and the help used. A correct guided attempt does not by itself show independent proficiency.'));
    table('Your progress', ['Capability', 'Current estimate', 'Status'], assessment.gaps.map(gap => {
      const estimate = assessment.estimates.find(e => e.capability === gap.capability);
      const task = assessment.taskProgress.find(p => p.capability === gap.capability);
      return [label(gap.capability), task?.label ?? label(estimate?.level), task ? 'Performance on the displayed tasks; no proficiency level assigned' : states[gap.status] ?? 'Not assessed'];
    }), 'No progress estimates yet.');
    table('Suggested next activities', ['Priority', 'Activity'],
      assessment.recommendations.map(r => [String(r.rank), label(r.activity)]), 'No activities suggested at present.');
    table('Classification feedback', ['Case', 'Table', 'Your classification', 'Result'], [...record.observations].reverse().flatMap(o => (o.criteria ?? []).map(r => [o.attempt?.taskId ?? '', r.id.toUpperCase(), r.selection === 'case' ? 'Case-based' : r.selection === 'aggregate' ? 'Aggregate' : 'Not selected', r.outcome])), 'No table classifications recorded yet.');
    table('Your recorded reflections', ['Question', 'Your response', 'Recorded'],
      Object.values(record.reflections ?? {}).flat().flatMap(r => [[r.prompt, r.answer, new Date(r.savedAt).toLocaleString()], ...(r.history ?? []).map(h => [h.prompt + ' (earlier response)', h.answer, new Date(h.savedAt).toLocaleString()])]),
      'No reflections recorded yet. Use Record beside a reflection question to keep your response here.');
  }
}

export function enableLearningRecord(registry: IRenderMimeRegistry, ready: Promise<Context>): void {
  NotebookActions.executed.connect((_, { cell }) => {
    const meta = cell.model.getMetadata('al') as { view?: string } | undefined;
    if (meta?.view === 'learner-record') cell.inputHidden = true;
  });
  registry.addFactory({
    safe: true, mimeTypes: [MIME],
    // Ignore MIME payloads: display only this browser learner's store, as text.
    createRenderer: () => new RecordView(ready)
  }, 0);
}
