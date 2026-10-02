// Observes exercise cells. When the learner runs a cell carrying `al` metadata,
// the observer runs that exercise's check in the same Jupyter kernel, in the
// kernel's language, and records one al:Observation. Learner-entered values
// never leave the Jupyter kernel; only the outcome code is read.

import { Contents, Kernel, KernelMessage } from '@jupyterlab/services';
import { INotebookTracker, NotebookActions } from '@jupyterlab/notebook';
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
}

const CHECK_EXTENSION: Readonly<Record<string, string>> = { python: 'py', r: 'R' };

export function exerciseMetadata(value: unknown): ExerciseMetadata | null {
  if (!value || typeof value !== 'object') return null;
  const m = value as Partial<ExerciseMetadata>;
  if (typeof m.activity !== 'string' || typeof m.object !== 'string' || typeof m.check !== 'string') return null;
  return { activity: m.activity, object: m.object, check: m.check, hints: Array.isArray(m.hints) ? m.hints.map(String) : [] };
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
    private readonly contents: Contents.IManager
  ) {
    NotebookActions.executed.connect(this.onExecuted, this);
  }

  get observed(): ISignal<this, ObserverEvent> {
    return this._observed;
  }

  dispose(): void {
    NotebookActions.executed.disconnect(this.onExecuted, this);
  }

  private onExecuted(_: unknown, args: { notebook: unknown; cell: { model: { getMetadata(key: string): unknown } } }): void {
    const meta = exerciseMetadata(args.cell.model.getMetadata('al'));
    if (!meta) return;
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

    const file = await this.contents.get(`${meta.check}.${extension}`, { content: true, format: 'text' });
    const code = String(file.content);
    const outcomeCode = await runCheck(kernel, code);
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
export async function runCheck(kernel: Kernel.IKernelConnection, code: string): Promise<string | null> {
  let text = '';
  const future = kernel.requestExecute({ code, silent: false, store_history: false, allow_stdin: false, stop_on_error: false });
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
