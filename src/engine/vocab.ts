// IRIs of al: terms used by the adaptive-learning engine. The engine works on
// IRIs throughout; labels are presentation only.

export const AL = 'https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#';

export const al = (local: string): string => AL + local;

export const STAGE = {
  selfReport: al('SelfReport'),
  completion: al('Completion'),
  knowledgeCheck: al('KnowledgeCheck'),
  simulation: al('Simulation'),
  reviewedPractice: al('ReviewedPractice')
} as const;

export const ACTION = {
  outputValidated: al('OutputValidated')
} as const;

export const OUTCOME = {
  correct: al('Correct'),
  incorrect: al('Incorrect'),
  incomplete: al('Incomplete'),
  completed: al('Completed')
} as const;

/** Outcome codes printed by exercise checks, mapped to al: concepts. */
export const OUTCOME_BY_CODE: Readonly<Record<string, string>> = {
  correct: OUTCOME.correct,
  incorrect: OUTCOME.incorrect,
  incomplete: OUTCOME.incomplete
};

export const GAP = {
  achieved: al('Achieved'),
  belowTarget: al('BelowTarget'),
  unknown: al('Unknown')
} as const;

export const STATUS = {
  demonstrated: al('Demonstrated'),
  reportedNeedsConfirmation: al('ReportedNeedsConfirmation'),
  developmentOpportunity: al('DevelopmentOpportunity'),
  notAssessed: al('NotAssessed')
} as const;

export const UNCERTAINTY = {
  high: al('HighUncertainty'),
  moderate: al('ModerateUncertainty'),
  low: al('LowUncertainty')
} as const;

export const EXCLUSION = {
  dependent: al('DependentEvidence'),
  guidanceExceeded: al('GuidanceExceeded')
} as const;

export const REASON = {
  belowTarget: al('ReasonBelowTarget'),
  notAssessed: al('ReasonNotAssessed'),
  insufficientIndependentEvidence: al('ReasonInsufficientIndependentEvidence'),
  confirmSelfReport: al('ReasonConfirmSelfReport'),
  criticalGate: al('ReasonCriticalGate'),
  prerequisitesMet: al('ReasonPrerequisitesMet')
} as const;

export const RECOMMENDATION_KIND = {
  practice: al('PracticeRecommendation')
} as const;
