import { LearnerRecord } from '../engine';

/** A readable local copy, not a restoration format or the RDF evidence graph. */
export function reflectionText(record: LearnerRecord): string {
  const lines = ['Recorded reflections', '',
    'Includes explicitly recorded answers and their save times.',
    'Excludes unrecorded changes, notebook edits, and scored attempts.',
    'This text file does not provide automatic restoration.', ''];
  let count = 0;
  for (const [section, entries] of Object.entries(record.reflections ?? {})) {
    lines.push(`Section: ${section}`, '');
    for (const entry of entries) {
      lines.push(`${++count}. ${entry.prompt}`, ...(entry.id ? [`Question: ${entry.id}; version: ${entry.version}`] : []), `Recorded: ${entry.savedAt}`, '', entry.answer, '', '---', '');
      for (const prior of entry.history ?? []) {
        lines.push('Earlier recorded response', prior.prompt, `Recorded: ${prior.savedAt}`, '', prior.answer, '', '---', '');
      }
    }
  }
  if (!count) lines.push('No reflections have been recorded yet.');
  return lines.join('\n') + '\n';
}
