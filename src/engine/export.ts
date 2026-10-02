// Export a learner record and its assessment as al: N-Quads: an evidence graph
// (learner, observations, evidence) and a derived graph (estimates, gaps,
// recommendations, receipt), each described as a learner-private al:LearningGraph.
// The export must conform to the al-core SHACL shapes.

import { canonicalJson, sha256Hex, stableId } from './ids';
import { Assessment, Catalog, LearnerRecord } from './types';
import { al } from './vocab';

const RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type';
const PROV = 'http://www.w3.org/ns/prov#';
const XSD = 'http://www.w3.org/2001/XMLSchema#';

type Term = { iri: string } | { literal: string; datatype?: string };

const iri = (value: string): Term => ({ iri: value });
const lit = (value: string | number | boolean, datatype: string): Term => ({ literal: String(value), datatype });

function term(t: Term): string {
  if ('iri' in t) return `<${t.iri}>`;
  const escaped = t.literal.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '\\r');
  return t.datatype ? `"${escaped}"^^<${t.datatype}>` : `"${escaped}"`;
}

export interface ExportOptions {
  /** Timestamp for the receipt, supplied by the host after computation. */
  generatedAt: string;
}

export async function exportNQuads(catalog: Catalog, record: LearnerRecord, assessment: Assessment, options: ExportOptions): Promise<string> {
  const evidenceGraph = `urn:al:graph:${record.learner.slice('urn:uuid:'.length)}:evidence`;
  const derivedGraph = `urn:al:graph:${record.learner.slice('urn:uuid:'.length)}:derived`;
  const lines: string[] = [];
  const add = (graph: string, s: string, p: string, o: Term) => lines.push(`<${s}> <${p}> ${term(o)} <${graph}> .`);

  // Learner and observations (evidence graph).
  add(evidenceGraph, record.learner, RDF_TYPE, iri(al('Learner')));
  add(evidenceGraph, record.learner, al('hasAudience'), iri(record.audience));
  for (const obs of record.observations) {
    add(evidenceGraph, obs.iri, RDF_TYPE, iri(al('Observation')));
    add(evidenceGraph, obs.iri, al('learner'), iri(record.learner));
    add(evidenceGraph, obs.iri, al('activity'), iri(obs.activity));
    add(evidenceGraph, obs.iri, al('observedObject'), iri(obs.object));
    add(evidenceGraph, obs.iri, al('observedAction'), iri(obs.action));
    add(evidenceGraph, obs.iri, al('outcome'), iri(obs.outcome));
    add(evidenceGraph, obs.iri, al('guidanceLevel'), lit(obs.guidanceLevel, XSD + 'integer'));
    add(evidenceGraph, obs.iri, PROV + 'generatedAtTime', lit(obs.at, XSD + 'dateTime'));
  }
  for (const e of assessment.evidence) {
    add(evidenceGraph, e.iri, RDF_TYPE, iri(al('EvidenceAssertion')));
    add(evidenceGraph, e.iri, al('learner'), iri(record.learner));
    add(evidenceGraph, e.iri, al('capability'), iri(e.capability));
    add(evidenceGraph, e.iri, al('evidenceStage'), iri(e.stage));
    add(evidenceGraph, e.iri, al('appliesRule'), iri(e.rule));
    add(evidenceGraph, e.iri, al('dependenceGroup'), lit(e.dependenceGroup, XSD + 'string'));
    add(evidenceGraph, e.iri, PROV + 'wasDerivedFrom', iri(e.observation));
  }

  // Estimates, gaps, recommendations (derived graph).
  for (const est of assessment.estimates) {
    add(derivedGraph, est.iri, RDF_TYPE, iri(al('CapabilityEstimate')));
    add(derivedGraph, est.iri, al('learner'), iri(record.learner));
    add(derivedGraph, est.iri, al('capability'), iri(est.capability));
    if (est.level) add(derivedGraph, est.iri, al('estimatedLevel'), iri(est.level));
    add(derivedGraph, est.iri, al('uncertainty'), iri(est.uncertainty));
    add(derivedGraph, est.iri, al('underPolicy'), iri(catalog.policy.iri));
    est.derivedFrom.forEach(e => add(derivedGraph, est.iri, PROV + 'wasDerivedFrom', iri(e)));
    for (const x of est.excluded) {
      const exclusion = stableId(est.iri, 'exclusion', x.evidence);
      add(derivedGraph, est.iri, al('hasExclusion'), iri(exclusion));
      add(derivedGraph, exclusion, RDF_TYPE, iri(al('EvidenceExclusion')));
      add(derivedGraph, exclusion, al('excludedEvidence'), iri(x.evidence));
      add(derivedGraph, exclusion, al('exclusionReason'), iri(x.reason));
    }
  }
  for (const gap of assessment.gaps) {
    add(derivedGraph, gap.iri, RDF_TYPE, iri(al('GapAssessment')));
    add(derivedGraph, gap.iri, al('learner'), iri(record.learner));
    add(derivedGraph, gap.iri, al('capability'), iri(gap.capability));
    add(derivedGraph, gap.iri, al('againstTarget'), iri(gap.target));
    if (gap.estimate) add(derivedGraph, gap.iri, al('assessesEstimate'), iri(gap.estimate));
    add(derivedGraph, gap.iri, al('gapState'), iri(gap.state));
    add(derivedGraph, gap.iri, al('profileStatus'), iri(gap.status));
    add(derivedGraph, gap.iri, al('criticalGateBlocked'), lit(gap.gateBlocked, XSD + 'boolean'));
  }
  const pathway = stableId(record.learner, 'pathway');
  if (assessment.recommendations.length) add(derivedGraph, pathway, RDF_TYPE, iri(al('Pathway')));
  for (const rec of assessment.recommendations) {
    add(derivedGraph, rec.iri, RDF_TYPE, iri(al('Recommendation')));
    add(derivedGraph, rec.iri, al('learner'), iri(record.learner));
    add(derivedGraph, rec.iri, al('inPathway'), iri(pathway));
    add(derivedGraph, rec.iri, al('rank'), lit(rec.rank, XSD + 'integer'));
    add(derivedGraph, rec.iri, al('recommendsActivity'), iri(rec.activity));
    add(derivedGraph, rec.iri, al('recommendationKind'), iri(rec.kind));
    add(derivedGraph, rec.iri, al('respondsToGap'), iri(rec.gap));
    rec.reasons.forEach(r => add(derivedGraph, rec.iri, al('reasonCode'), iri(r)));
    if (rec.estimate) add(derivedGraph, rec.iri, PROV + 'wasDerivedFrom', iri(rec.estimate));
  }

  // Receipt and graph descriptors.
  const inputDigest = await sha256Hex(canonicalJson({ catalog: catalog.sourceDigest, record }));
  const resultDigest = await sha256Hex(canonicalJson(assessment));
  const receipt = stableId(record.learner, 'receipt', inputDigest, resultDigest);
  add(derivedGraph, receipt, RDF_TYPE, iri(al('Receipt')));
  add(derivedGraph, receipt, al('engineVersion'), lit(assessment.engineVersion, XSD + 'string'));
  add(derivedGraph, receipt, al('operation'), lit('assess', XSD + 'string'));
  add(derivedGraph, receipt, al('policyVersion'), lit(assessment.policyVersion, XSD + 'string'));
  add(derivedGraph, receipt, al('inputDigest'), lit(inputDigest, XSD + 'string'));
  add(derivedGraph, receipt, al('resultDigest'), lit(resultDigest, XSD + 'string'));
  add(derivedGraph, receipt, al('terminalStatus'), iri(al('Succeeded')));
  add(derivedGraph, receipt, PROV + 'generatedAtTime', lit(options.generatedAt, XSD + 'dateTime'));

  for (const [graph, role, lifecycle] of [
    [evidenceGraph, 'EvidenceGraph', 'AppendOnly'],
    [derivedGraph, 'DerivedGraph', 'Recomputable']
  ] as const) {
    add(derivedGraph, graph, RDF_TYPE, iri(al('LearningGraph')));
    add(derivedGraph, graph, al('graphRole'), iri(al(role)));
    add(derivedGraph, graph, al('lifecycle'), iri(al(lifecycle)));
    add(derivedGraph, graph, al('privacyClass'), iri(al('LearnerPrivate')));
    add(derivedGraph, graph, al('graphOf'), iri(record.learner));
  }

  return lines.join('\n') + '\n';
}
