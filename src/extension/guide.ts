// Notebook guide: gives facilitation-ladder help for the current exercise.
//
// The guide explains and hints; it never decides pathways, writes answers into
// the notebook, or executes code. Every level it reveals is recorded, and the
// next observation for that activity carries that guidance level, so evidence
// rules can discount heavily guided attempts.
//
// StaticHintGuide serves the hints authored in the exercise cell metadata. A
// local-model guide (in-browser or localhost) can implement the same interface
// and must respect the same ladder.

export interface ExerciseContext {
  activity: string;
  title: string;
  /** Authored hints, index 0 = ladder level 1. */
  hints: string[];
  /** Jupyter kernel language of the open notebook. */
  language: string;
}

export interface GuideReply {
  level: number;
  text: string;
}

export interface INotebookGuide {
  readonly id: string;
  readonly label: string;
  /** Highest ladder level this guide can provide for the exercise. */
  maxLevel(exercise: ExerciseContext): number;
  /** Help at exactly `level`; callers request levels in order. */
  help(exercise: ExerciseContext, level: number): Promise<GuideReply>;
}

export class StaticHintGuide implements INotebookGuide {
  readonly id = 'static-hints';
  readonly label = 'Authored hints';

  maxLevel(exercise: ExerciseContext): number {
    return exercise.hints.length;
  }

  async help(exercise: ExerciseContext, level: number): Promise<GuideReply> {
    const text = exercise.hints[level - 1];
    if (text === undefined) throw new Error(`No hint at level ${level}`);
    return { level, text };
  }
}
