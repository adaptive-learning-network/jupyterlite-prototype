// Observes exercise cells. When the learner runs a cell carrying `al` metadata,
// the observer runs that exercise's check in the same Jupyter kernel, in the
// kernel's language, and records one al:Observation. Learner-entered values
// stay in the Jupyter kernel except bounded classification choices in the pilot.

import { Kernel, KernelMessage } from '@jupyterlab/services';
import { INotebookTracker, NotebookActions, NotebookPanel } from '@jupyterlab/notebook';
import { ISignal, Signal } from '@lumino/signaling';

import { ACTION, assess, Catalog, CriterionResult, Observation, OUTCOME_BY_CODE } from '../engine';
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
        kernel.registerCommTarget('al.practice', (comm, message) => {
          const cellId = message.content.data.cell;
          const source = panel.content.model && Array.from(panel.content.model.cells).find(cell => cell.id === cellId);
          const meta = exerciseMetadata(source?.getMetadata('al'));
          const activity = this.catalog.activities.find(a => a.iri === meta?.activity);
          if (!meta || !activity?.assessment || meta.submission !== 'widget' || message.content.data.version !== activity.assessment.version) {
            comm.send({ error: 'These controls do not match the current task version. Open the current supplied notebook before reassessment.' }); return;
          }
          let currentId: string | undefined;
          let busy = false;
          const state = () => {
            const attempt = this.store.activeTask(activity)!;
            currentId = attempt.id;
            const progress = assess(this.catalog, this.store.record).taskProgress.find(p => p.activity === activity.iri)!;
            const last = [...this.store.record.observations].reverse().find(o => o.attempt?.id === attempt.id);
            return { attempt: { ...attempt }, progress: { ...progress }, lastCriteria: (last?.criteria ?? []).map(r => ({...r})), ready: true };
          };
          comm.onMsg = message => {
            if (busy) { comm.send({ error: 'A task request is already being processed.' }); return; }
            busy = true;
            void (async () => {
              const request = message.content.data;
              const active = this.store.activeTask(activity);
              if (request.action === 'resume') {
                if (!active) this.store.beginTask(activity, 'practice');
              } else if (request.action === 'begin' && (request.mode === 'practice' || request.mode === 'reassessment')) {
                if (currentId && active?.id !== currentId) throw new Error('This task changed in another session. Run the controls cell again.');
                this.store.beginTask(activity, request.mode);
              } else if (request.action === 'hint') {
                const attempt = this.store.taskHint(activity, currentId!);
                comm.send({ ...state(), hint: meta.hints[Math.min(attempt.guidanceLevel, meta.hints.length) - 1] }); return;
              } else if (request.action === 'submit') {
                if (!active || active.id !== currentId) throw new Error('Run the controls cell again to reconnect this task.');
                const detail = await runCheckResult(kernel, await this.loadCheck(`${meta.check}.py`), 'python');
                const task = activity.assessment!.tasks.find(t => t.id === active.taskId)!;
                const results = detail?.criteria;
                if (detail?.taskId !== active.taskId || !Array.isArray(results) || results.length !== task.tables.length ||
                    new Set(results.map(r => r.id)).size !== results.length ||
                    !task.tables.every(t => results.some(r => r.id === t.id && ['correct', 'incorrect', 'incomplete'].includes(r.outcome) && (r.selection === null || r.selection === 'case' || r.selection === 'aggregate')))) {
                  throw new Error('The submitted tables do not match the current task. Run the controls cell again.');
                }
                const code = results.some(r => r.outcome === 'incomplete') ? 'incomplete' : results.every(r => r.outcome === 'correct') ? 'correct' : 'incorrect';
                if (detail.outcome !== code) throw new Error('The task check returned inconsistent criteria.');
                const observation = this.store.submitTask(activity, currentId!, OUTCOME_BY_CODE[code], code === 'incomplete' ? results.map(r => ({id: r.id, outcome: 'incomplete' as const, selection: r.selection})) : results, 'python');
                this._observed.emit({ observation });
                comm.send({ ...state(), outcome: code, criteria: code === 'incomplete' ? results.map(r => ({ id: r.id, outcome: r.outcome === 'incomplete' ? 'incomplete' : 'answered' })) : results }); return;
              } else throw new Error('Unknown task request.');
              comm.send(state());
            })().catch(error => comm.send({ error: String(error) })).finally(() => { busy = false; });
          };
          comm.send({ connected: true });
        });
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
  return (await runCheckResult(kernel, code, language))?.outcome ?? null;
}

interface CheckResult { outcome: string; taskId?: string; criteria?: CriterionResult[]; }
export async function runCheckResult(kernel: Kernel.IKernelConnection, code: string, language: string): Promise<CheckResult | null> {
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
    const parsed = JSON.parse(line.slice(SENTINEL.length)) as CheckResult;
    return typeof parsed.outcome === 'string' ? parsed : null;
  } catch {
    return null;
  }
}
