// Contracts between the catalog projection, the learner record, and the
// adaptive-learning engine. All identifiers are IRIs.

export interface CatalogLevel {
  iri: string;
  notation: string;
  label: string;
  ordinal: number;
}

export interface CatalogCapability {
  iri: string;
  notation: string;
  label: string;
  ordinal: number;
  prerequisites: string[];
}

export interface CatalogTarget {
  iri: string;
  audiences: string[];
  capability: string;
  level: string;
  critical: boolean;
}

export interface CatalogActivity {
  iri: string;
  title: string;
  ordinal: number;
  kind: string;
  capabilities: string[];
  /** Jupyter kernel language name (lower case) -> notebook path. */
  notebooks: Record<string, string>;
  rules: string[];
  /** External location, e.g. a quiz form launched from the learning panel. */
  url?: string;
}

export interface CatalogRule {
  iri: string;
  activity: string;
  criterion: string;
  capability: string;
  stage: string;
  requiredAction: string;
  acceptedOutcomes: string[];
  maximumGuidance: number;
}

/** Projection produced by scripts/build_catalog.py from the validated TriG. */
export interface Catalog {
  schema: 'al-catalog-projection/0.1';
  sourceDigest: string;
  framework: { iri: string; title: string; scale: string };
  levels: CatalogLevel[];
  capabilities: CatalogCapability[];
  audiences: { iri: string; label: string }[];
  targets: CatalogTarget[];
  activities: CatalogActivity[];
  rules: CatalogRule[];
  policy: { iri: string; version: string; ceilings: Record<string, string> };
}

/** What the application observed. Never contains learner-entered values. */
export interface Observation {
  iri: string;
  activity: string;
  /** Stable identifier of what was acted on (an exercise cell). */
  object: string;
  action: string;
  outcome: string;
  guidanceLevel: number;
  /** ISO 8601 timestamp supplied by the host, never read inside the engine. */
  at: string;
  /** Jupyter kernel language the exercise ran in; informational. */
  language?: string;
}

/** Consented link to an external identity: issuer and opaque subject only. */
export interface IdentityBinding {
  iri: string;
  issuer: string;
  subject: string;
  boundAt: string;
  /** Most recent successful verification with the issuer. */
  verifiedAt: string;
  consent: { iri: string; purpose: string; revision: string; consentedAt: string };
}

export interface LearnerRecord {
  schema: 'al-learner-record/0.1';
  learner: string;
  audience: string;
  observations: Observation[];
  /** Highest facilitation-ladder level revealed per activity. */
  guidance: Record<string, number>;
  /** Present only after the learner consents to link an external identity. */
  identity?: IdentityBinding;
}

export interface EvidenceAssertion {
  iri: string;
  observation: string;
  rule: string;
  capability: string;
  stage: string;
  dependenceGroup: string;
  /** Present when the assertion was considered but not used. */
  exclusion?: string;
}

export interface CapabilityEstimate {
  iri: string;
  capability: string;
  /** Absent when no admissible evidence remains. */
  level?: string;
  uncertainty: string;
  derivedFrom: string[];
  excluded: { evidence: string; reason: string }[];
}

export interface GapAssessment {
  iri: string;
  capability: string;
  target: string;
  estimate?: string;
  state: string;
  status: string;
  critical: boolean;
  gateBlocked: boolean;
}

export interface Recommendation {
  iri: string;
  rank: number;
  activity: string;
  capability: string;
  gap: string;
  kind: string;
  reasons: string[];
  estimate?: string;
}

export interface Assessment {
  engineVersion: string;
  policyVersion: string;
  evidence: EvidenceAssertion[];
  estimates: CapabilityEstimate[];
  gaps: GapAssessment[];
  recommendations: Recommendation[];
}

export class EngineInputError extends Error {
  constructor(readonly code: string, message: string) {
    super(`${code}: ${message}`);
    this.name = 'EngineInputError';
  }
}
