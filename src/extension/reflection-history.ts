import { ReflectionEntry } from '../engine/types';
export interface ReflectionAnswer {
  id?: string; version?: number; prompt: string; answer: string; legacyPrompts?: string[];
}
/** Preserve removed questions, earlier versions, and earlier recorded wording/answers. */
export function mergeReflections(previous: ReflectionEntry[], answers: ReflectionAnswer[], savedAt: string): ReflectionEntry[] {
  const merged: ReflectionEntry[] = previous.map(entry => ({ ...entry, history: entry.history?.map(item => ({ ...item })) }));
  for (const answer of answers) {
    const index = merged.findIndex(entry => answer.id
      ? (entry.id === answer.id && entry.version === answer.version) ||
        (answer.version === 1 && !entry.id && (answer.legacyPrompts ?? [answer.prompt]).includes(entry.prompt))
      : !entry.id && entry.prompt === answer.prompt);
    const old = index < 0 ? undefined : merged[index];
    const history = [...(old?.history ?? [])];
    if (old && (old.answer !== answer.answer || old.prompt !== answer.prompt)) {
      history.push({ prompt: old.prompt, answer: old.answer, savedAt: old.savedAt });
    }
    const next: ReflectionEntry = { id: answer.id, version: answer.version,
      prompt: answer.prompt, answer: answer.answer, savedAt, ...(history.length ? { history } : {}) };
    if (index < 0) merged.push(next); else merged[index] = next;
  }
  return merged;
}
