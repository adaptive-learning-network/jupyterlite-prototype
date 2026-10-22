// Pure formative task policy. No proficiency scale is inferred from these tasks.
import { CatalogActivity, LearnerRecord, Observation, PracticeTransferPolicy, TaskAttempt, TaskProgress } from './types';
import { OUTCOME } from './vocab';

export function validTaskObservation(activity: CatalogActivity, observation: Observation): boolean {
  const policy = activity.assessment, attempt = observation.attempt;
  const task = policy?.tasks.find(t => t.id === attempt?.taskId);
  if (!policy || !attempt || !task || !Number.isInteger(attempt.submissions) || attempt.submissions < 0 || !Number.isInteger(attempt.guidanceLevel) || attempt.guidanceLevel < 0 || attempt.guidanceLevel !== observation.guidanceLevel || attempt.version !== policy.version || attempt.mode !== task.mode || attempt.activity !== activity.iri) return false;
  const results = observation.criteria ?? [];
  return results.length === task.tables.length && new Set(results.map(r => r.id)).size === results.length &&
    task.tables.every(t => results.some(r => r.id === t.id && ['correct', 'incorrect', 'incomplete'].includes(r.outcome)));
}

export function qualifyingTransfer(activity: CatalogActivity, observation: Observation): boolean {
  return validTaskObservation(activity, observation) && observation.outcome === OUTCOME.correct &&
    observation.attempt!.mode === 'reassessment' && observation.attempt!.submissions === 1 &&
    observation.guidanceLevel === 0 && observation.attempt!.guidanceLevel === 0 &&
    observation.criteria!.every(r => r.outcome === 'correct');
}

export function taskProgress(activity: CatalogActivity, observations: Observation[]): TaskProgress {
  const valid = observations.filter(o => o.activity === activity.iri && validTaskObservation(activity, o));
  const last = valid.at(-1);
  const demonstrated = valid.some(o => qualifyingTransfer(activity, o));
  const lastSuccess = valid.map(o => qualifyingTransfer(activity, o)).lastIndexOf(true);
  const recheck = demonstrated && valid.slice(lastSuccess + 1).some(o => o.outcome === OUTCOME.incorrect);
  let label = 'Not assessed on the current task version';
  if (demonstrated) label = recheck ? 'Recheck recommended' : 'Demonstrated on a different case';
  else if (last?.attempt?.mode === 'reassessment') label = last.outcome === OUTCOME.correct
    ? 'New case completed after feedback; try another case' : 'Reassessment in progress';
  else if (last) label = last.outcome === OUTCOME.correct
    ? last.guidanceLevel > 0 || last.attempt!.submissions > 1 ? 'Practice completed with assistance' : 'Practice completed without recorded hints'
    : 'Practice in progress';
  const task = activity.assessment?.tasks.find(t => t.id === last?.attempt?.taskId);
  const suggestions = last?.outcome === OUTCOME.incorrect ? [...new Set(last.criteria!.filter(r => r.outcome === 'incorrect').map(r => {
    const table = task!.tables.find(t => t.id === r.id)!;
    return activity.assessment!.remediations[table.rowUnit === 'group' ? 'aggregate' : 'case'];
  }))] : [];
  return { activity: activity.iri, capability: activity.capabilities[0], label, demonstrated: demonstrated && !recheck, recheck, suggestions };
}

/** The host supplies the ID/time. Previously displayed cases are never fresh again. */
export function beginTask(record: LearnerRecord, activity: CatalogActivity, mode: TaskAttempt['mode'], id: string, at: string): TaskAttempt {
  const policy: PracticeTransferPolicy = activity.assessment!;
  const history = (record.taskAttempts ?? []).filter(a => a.activity === activity.iri && a.version === policy.version);
  if (mode === 'reassessment' && !record.observations.some(o => o.activity === activity.iri && validTaskObservation(activity, o) && o.attempt!.mode === 'practice' && o.outcome !== OUTCOME.incomplete)) {
    throw new Error('Submit the practice tables before trying another case.');
  }
  const task = policy.tasks.find(t => t.mode === mode && (mode === 'practice' || !history.some(a => a.taskId === t.id)));
  if (!task) throw new Error('You have seen all three new cases. You can return to practice and review your feedback. A further independent check needs a new case from the course team.');
  return { id, activity: activity.iri, taskId: task.id, version: policy.version, mode,
    guidanceLevel: mode === 'practice' ? Math.max(record.guidance[activity.iri] ?? 0, ...history.filter(a => a.mode === 'practice').map(a => a.guidanceLevel), 0) : 0,
    submissions: 0, startedAt: at };
}
