// Observes exercise cells. When the learner runs a cell carrying `al` metadata,
// the observer runs that exercise's check in the same Jupyter kernel, in the
// kernel's language, and records one al:Observation. Learner-entered values
// never leave the Jupyter kernel; only the outcome code is read.

import { Kernel, KernelMessage } from '@jupyterlab/services';
import { INotebookTracker, NotebookActions, NotebookPanel } from '@jupyterlab/notebook';
import { ISignal, Signal } from '@lumino/signaling';

import { ACTION, Catalog, Observation, OUTCOME_BY_CODE } from '../engine';
import { LearnerStore } from './store';

export const SENTINEL = 'AL_OBSERVATION ';

/** Cell metadata written by scripts/make_exercises.py. */
export interface ExerciseMetadata {
  activity: string;
  object: string;
  check: string;
  hints: string[];
  submission?: string;
  computation?: boolean;
}

const CHECK_EXTENSION: Readonly<Record<string, string>> = { python: 'py', r: 'R' };

export function exerciseMetadata(value: unknown): ExerciseMetadata | null {
  if (!value || typeof value !== 'object') return null;
  const m = value as Partial<ExerciseMetadata>;
  if (typeof m.activity !== 'string' || typeof m.object !== 'string' || typeof m.check !== 'string') return null;
  return { activity: m.activity, object: m.object, check: m.check, hints: Array.isArray(m.hints) ? m.hints.map(String) : [], submission: m.submission, computation: m.computation === true };
}

export async function kernelLanguage(kernel: Kernel.IKernelConnection): Promise<string> {
  const info = await kernel.info;
  return (info.language_info?.name ?? '').toLowerCase();
}

export interface ObserverEvent {
  observation?: Observation;
  /** Present when no observation could be recorded. */
  problem?: string;
}

export class ExerciseObserver {
  private readonly _observed = new Signal<this, ObserverEvent>(this);

  constructor(
    private readonly catalog: Catalog,
    private readonly store: LearnerStore,
    private readonly tracker: INotebookTracker,
    private readonly loadCheck: (path: string) => Promise<string>
  ) {
    NotebookActions.executed.connect(this.onExecuted, this);
    const attach = (panel: NotebookPanel) => {
      const connect = () => {
        const kernel = panel.sessionContext.session?.kernel;
        if (!kernel) return;
        kernel.registerCommTarget('al.submit', (comm, message) => {
          const cellId = message.content.data.cell;
          comm.onMsg = () => {
            const cell = panel.content.model?.cells;
            const source = cell && Array.from(cell).find(item => item.id === cellId);
            const meta = exerciseMetadata(source?.getMetadata('al'));
            if (!meta || meta.submission !== 'widget') {
              comm.send({ error: 'This submission is not linked to an exercise.' });
              return;
            }
            // Return immediately so Jupyter can process the check's IOPub replies.
            void this.observe(meta, kernel).then(event => {
              this._observed.emit(event);
              comm.send(event.observation ? { outcome: event.observation.outcome.split('#').pop()! } : { error: event.problem ?? 'Could not record this attempt.' });
            }).catch(error => {
              const problem = `Could not record this attempt: ${String(error)}. Please submit again.`;
              this._observed.emit({ problem });
              comm.send({ error: problem });
            });
          };
          comm.send({ ready: true });
        });
      };
      panel.sessionContext.kernelChanged.connect(connect);
      void panel.sessionContext.ready.then(connect);
      connect();
    };
    tracker.forEach(attach);
    tracker.widgetAdded.connect((_, panel) => attach(panel));
  }

  get observed(): ISignal<this, ObserverEvent> {
    return this._observed;
  }

  dispose(): void {
    NotebookActions.executed.disconnect(this.onExecuted, this);
  }

  private onExecuted(_: unknown, args: { notebook: unknown; cell: { inputHidden?: boolean; model: { getMetadata(key: string): unknown } } }): void {
    const meta = exerciseMetadata(args.cell.model.getMetadata('al'));
    if (!meta) return;
    if (meta.submission === 'widget') {
      // Executing a collapsed cell can expand it and change source_hidden.
      // Widget submission cells are infrastructure, so restore the collapsed view.
      if (!meta.computation) args.cell.inputHidden = true;
      return;
    }
    const panel = this.tracker.find(p => p.content === args.notebook);
    const kernel = panel?.sessionContext.session?.kernel;
    if (!kernel) return;
    void this.observe(meta, kernel).then(
      event => this._observed.emit(event),
      error => this._observed.emit({ problem: String(error) })
    );
  }

  private async observe(meta: ExerciseMetadata, kernel: Kernel.IKernelConnection): Promise<ObserverEvent> {
    if (!this.catalog.activities.some(a => a.iri === meta.activity)) {
      return { problem: `Exercise activity is not in the catalog: ${meta.activity}` };
    }
    const language = await kernelLanguage(kernel);
    const extension = CHECK_EXTENSION[language];
    if (!extension) return { problem: `No checks for Jupyter kernel language "${language}"` };

    const code = await this.loadCheck(`${meta.check}.${extension}`);
    const outcomeCode = await runCheck(kernel, code, language);
    const outcome = outcomeCode ? OUTCOME_BY_CODE[outcomeCode] : undefined;
    if (!outcome) return { problem: 'The exercise check did not report a result.' };

    const observation = this.store.addObservation({
      activity: meta.activity,
      object: meta.object,
      action: ACTION.outputValidated,
      outcome,
      at: new Date().toISOString(),
      language
    });
    return { observation };
  }
}

/** Execute check code without adding it to history; return the reported outcome code. */
export async function runCheck(kernel: Kernel.IKernelConnection, code: string, language: string): Promise<string | null> {
  let text = '';
  // Checks read the live answer variables, but their imports and helper
  // definitions must not replace the notebook's own functions. In particular,
  // a check from an already-open older course build may use an earlier schema.
  const checkCode = language === 'python' ? `exec(${JSON.stringify(code)}, dict(globals()))` : code;
  const future = kernel.requestExecute({ code: checkCode, silent: false, store_history: false, allow_stdin: false, stop_on_error: false });
  future.onIOPub = (msg: KernelMessage.IIOPubMessage) => {
    if (KernelMessage.isStreamMsg(msg)) text += msg.content.text;
  };
  await future.done;
  const line = text.split('\n').find(l => l.startsWith(SENTINEL));
  if (!line) return null;
  try {
    const parsed = JSON.parse(line.slice(SENTINEL.length)) as { outcome?: unknown };
    return typeof parsed.outcome === 'string' ? parsed.outcome : null;
  } catch {
    return null;
  }
}
