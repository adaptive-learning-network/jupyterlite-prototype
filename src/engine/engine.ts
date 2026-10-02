// The adaptive-learning engine: a pure, deterministic function from a
// validated catalog and a learner record to evidence, estimates, gaps, and
// recommendations. No DOM, storage, network, clock, or randomness.
//
// Policy (prototype-0.1, declared in the catalog):
//   - an observation becomes evidence when an evidence rule of its activity
//     accepts its action and outcome;
//   - evidence above the rule's guidance ceiling is excluded (guidance-exceeded);
//   - repeated evidence from one activity is one dependence group; only the
//     earliest admissible assertion counts, later ones are excluded (dependent);
//   - admissible evidence supports the policy's ceiling level for its stage, and
//     the estimate is the highest supported level;
//   - incorrect or incomplete attempts are never negative evidence.

import { stableId } from './ids';
import {
  Assessment,
  Catalog,
  CapabilityEstimate,
  EngineInputError,
  EvidenceAssertion,
  GapAssessment,
  LearnerRecord,
  Recommendation
} from './types';
import { EXCLUSION, GAP, OUTCOME, REASON, RECOMMENDATION_KIND, STAGE, STATUS, UNCERTAINTY } from './vocab';

export const ENGINE_VERSION = 'al-engine/0.1.0';
export const MAX_RECOMMENDATIONS = 3;

/** Uncertainty by the strongest stage behind an estimate. Prototype default. */
const UNCERTAINTY_BY_STAGE: Readonly<Record<string, string>> = {
  [STAGE.selfReport]: UNCERTAINTY.high,
  [STAGE.completion]: UNCERTAINTY.high,
  [STAGE.knowledgeCheck]: UNCERTAINTY.moderate,
  [STAGE.simulation]: UNCERTAINTY.moderate,
  [STAGE.reviewedPractice]: UNCERTAINTY.low
};

export function assess(catalog: Catalog, record: LearnerRecord): Assessment {
  validateInputs(catalog, record);

  const levelOrdinal = new Map(catalog.levels.map(l => [l.iri, l.ordinal]));
  const rulesByActivity = new Map<string, Catalog['rules']>();
  for (const rule of catalog.rules) {
    rulesByActivity.set(rule.activity, [...(rulesByActivity.get(rule.activity) ?? []), rule]);
  }

  // 1. Observation -> evidence assertion (with exclusions).
  const observations = [...record.observations].sort((a, b) => a.at.localeCompare(b.at) || a.iri.localeCompare(b.iri));
  const evidence: EvidenceAssertion[] = [];
  const usedGroups = new Set<string>();
  for (const obs of observations) {
    for (const rule of rulesByActivity.get(obs.activity) ?? []) {
      if (obs.action !== rule.requiredAction || !rule.acceptedOutcomes.includes(obs.outcome)) continue;
      const assertion: EvidenceAssertion = {
        iri: stableId(record.learner, 'evidence', obs.iri, rule.iri),
        observation: obs.iri,
        rule: rule.iri,
        capability: rule.capability,
        stage: rule.stage,
        dependenceGroup: obs.activity
      };
      const groupKey = `${rule.capability} ${obs.activity}`;
      if (obs.guidanceLevel > rule.maximumGuidance) {
        assertion.exclusion = EXCLUSION.guidanceExceeded;
      } else if (usedGroups.has(groupKey)) {
        assertion.exclusion = EXCLUSION.dependent;
      } else {
        usedGroups.add(groupKey);
      }
      evidence.push(assertion);
    }
  }

  // 2. Evidence -> capability estimate.
  const estimates: CapabilityEstimate[] = [];
  const estimateByCapability = new Map<string, CapabilityEstimate>();
  for (const capability of catalog.capabilities) {
    const forCapability = evidence.filter(e => e.capability === capability.iri);
    if (forCapability.length === 0) continue;
    const admissible = forCapability.filter(e => !e.exclusion);
    let level: string | undefined;
    let strongestStage: string | undefined;
    for (const e of admissible) {
      const supported = catalog.policy.ceilings[e.stage];
      if (supported && (!level || levelOrdinal.get(supported)! > levelOrdinal.get(level)!)) {
        level = supported;
        strongestStage = e.stage;
      }
    }
    const estimate: CapabilityEstimate = {
      iri: stableId(record.learner, 'estimate', capability.iri),
      capability: capability.iri,
      level,
      uncertainty: strongestStage ? UNCERTAINTY_BY_STAGE[strongestStage] ?? UNCERTAINTY.high : UNCERTAINTY.high,
      derivedFrom: admissible.map(e => e.iri),
      excluded: forCapability.filter(e => e.exclusion).map(e => ({ evidence: e.iri, reason: e.exclusion! }))
    };
    estimates.push(estimate);
    estimateByCapability.set(capability.iri, estimate);
  }

  // 3. Estimate x target -> gap assessment.
  const gaps: GapAssessment[] = [];
  const gapByCapability = new Map<string, GapAssessment>();
  for (const capability of catalog.capabilities) {
    const target = catalog.targets.find(t => t.capability === capability.iri && t.audiences.includes(record.audience));
    if (!target) continue;
    const estimate = estimateByCapability.get(capability.iri);
    let state: string = GAP.unknown;
    let status: string = STATUS.notAssessed;
    if (estimate?.level) {
      const achieved = levelOrdinal.get(estimate.level)! >= levelOrdinal.get(target.level)!;
      const observed = evidence.some(e => estimate.derivedFrom.includes(e.iri) && e.stage !== STAGE.selfReport);
      state = achieved ? GAP.achieved : GAP.belowTarget;
      status = !achieved ? STATUS.developmentOpportunity : observed ? STATUS.demonstrated : STATUS.reportedNeedsConfirmation;
    }
    const gap: GapAssessment = {
      iri: stableId(record.learner, 'gap', capability.iri, target.iri),
      capability: capability.iri,
      target: target.iri,
      estimate: estimate?.iri,
      state,
      status,
      critical: target.critical,
      gateBlocked: target.critical && (state !== GAP.achieved || status === STATUS.reportedNeedsConfirmation)
    };
    gaps.push(gap);
    gapByCapability.set(capability.iri, gap);
  }

  // 4. Gaps -> bounded, prerequisite-aware recommendations.
  const isAchieved = (cap: string) => gapByCapability.get(cap)?.state === GAP.achieved;
  const attempted = (cap: string) =>
    observations.some(o => o.outcome !== OUTCOME.correct && catalog.activities.some(a => a.iri === o.activity && a.capabilities.includes(cap)));
  const candidates = catalog.capabilities
    .filter(c => {
      const gap = gapByCapability.get(c.iri);
      if (!gap) return false;
      const open = gap.state !== GAP.achieved || gap.status === STATUS.reportedNeedsConfirmation;
      return open && c.prerequisites.every(isAchieved);
    })
    .sort((a, b) => Number(gapByCapability.get(b.iri)!.critical) - Number(gapByCapability.get(a.iri)!.critical) || a.ordinal - b.ordinal);

  const recommendations: Recommendation[] = [];
  for (const capability of candidates) {
    if (recommendations.length >= MAX_RECOMMENDATIONS) break;
    const activity = catalog.activities.find(a => a.capabilities.includes(capability.iri));
    if (!activity) continue;
    const gap = gapByCapability.get(capability.iri)!;
    const reasons: string[] = [];
    if (gap.state === GAP.unknown) reasons.push(REASON.notAssessed);
    if (gap.state === GAP.belowTarget) reasons.push(REASON.belowTarget);
    if (gap.status === STATUS.reportedNeedsConfirmation) reasons.push(REASON.confirmSelfReport);
    if (gap.state !== GAP.achieved && (attempted(capability.iri) || estimateByCapability.get(capability.iri)?.excluded.length)) {
      reasons.push(REASON.insufficientIndependentEvidence);
    }
    if (capability.prerequisites.length > 0) reasons.push(REASON.prerequisitesMet);
    if (gap.critical) reasons.push(REASON.criticalGate);
    recommendations.push({
      iri: stableId(record.learner, 'recommendation', capability.iri, activity.iri),
      rank: recommendations.length + 1,
      activity: activity.iri,
      capability: capability.iri,
      gap: gap.iri,
      kind: RECOMMENDATION_KIND.practice,
      reasons,
      estimate: estimateByCapability.get(capability.iri)?.iri
    });
  }

  return { engineVersion: ENGINE_VERSION, policyVersion: catalog.policy.version, evidence, estimates, gaps, recommendations };
}

function validateInputs(catalog: Catalog, record: LearnerRecord): void {
  if (catalog.schema !== 'al-catalog-projection/0.1') throw new EngineInputError('CATALOG_SCHEMA', 'unsupported catalog projection');
  if (record.schema !== 'al-learner-record/0.1') throw new EngineInputError('RECORD_SCHEMA', 'unsupported learner record');
  if (!/^urn:uuid:[0-9a-f-]{36}$/.test(record.learner)) throw new EngineInputError('LEARNER_IRI', 'learner must be an opaque urn:uuid');
  if (!catalog.audiences.some(a => a.iri === record.audience)) throw new EngineInputError('UNKNOWN_AUDIENCE', record.audience);
  const activities = new Set(catalog.activities.map(a => a.iri));
  const seen = new Set<string>();
  for (const obs of record.observations) {
    if (seen.has(obs.iri)) throw new EngineInputError('DUPLICATE_OBSERVATION', obs.iri);
    seen.add(obs.iri);
    if (!activities.has(obs.activity)) throw new EngineInputError('UNKNOWN_ACTIVITY', obs.activity);
    if (!Number.isInteger(obs.guidanceLevel) || obs.guidanceLevel < 0) throw new EngineInputError('GUIDANCE_LEVEL', obs.iri);
  }
  // Prerequisite graph must be acyclic.
  const prereqs = new Map(catalog.capabilities.map(c => [c.iri, c.prerequisites]));
  const visiting = new Set<string>();
  const done = new Set<string>();
  const visit = (cap: string): void => {
    if (done.has(cap)) return;
    if (visiting.has(cap)) throw new EngineInputError('PREREQUISITE_CYCLE', cap);
    visiting.add(cap);
    (prereqs.get(cap) ?? []).forEach(visit);
    visiting.delete(cap);
    done.add(cap);
  };
  catalog.capabilities.forEach(c => visit(c.iri));
}
