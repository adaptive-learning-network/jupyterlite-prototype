"""Read this prototype's learner N-Quads export for a local teaching view.

This deliberately handles only the N-Quads shape emitted by src/engine/export.ts.
It uses the Python standard library so the generated notebook works in Pyodide.
"""

from pathlib import Path
import re

LINE = re.compile(r'^<([^>]*)> <([^>]*)> (<[^>]*>|"(?:\\.|[^"\\])*"(?:\^\^<[^>]*>)?) <([^>]*)> \.$')
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
AL = "https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#"


def short(value):
    """Shorten an IRI or literal for the learner-facing tables."""
    if value.startswith('"'):
        return value.split('"', 2)[1]
    return value.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def parse_export(text):
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        match = LINE.fullmatch(line)
        if not match:
            raise ValueError(f"Line {number} is not in this prototype's N-Quads export format")
        subject, predicate, raw_object, graph = match.groups()
        obj = raw_object[1:-1] if raw_object.startswith("<") else raw_object
        rows.append((subject, predicate, obj, graph, line))
    if not any(p == RDF_TYPE and o == AL + "LearningGraph" for _, p, o, _, _ in rows):
        raise ValueError("No learner graph descriptor found; use Learning panel > Export record")
    return rows


def subjects(rows, kind):
    return {s for s, p, o, _, _ in rows if p == RDF_TYPE and o == AL + kind}


def property_of(rows, subject, name):
    values = [o for s, p, o, _, _ in rows if s == subject and p.endswith("#" + name)]
    return short(values[0]) if values else "—"


def graph_counts(rows):
    return {kind: len(subjects(rows, kind)) for kind in (
        "Observation", "EvidenceAssertion", "CapabilityEstimate", "GapAssessment", "Recommendation"
    )}


def table(headers, rows):
    if not rows:
        return "_None in this snapshot._\n"
    safe = lambda value: str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|").replace("\n", " ")
    return "| " + " | ".join(headers) + " |\n| " + " | ".join("---" for _ in headers) + " |\n" + "\n".join(
        "| " + " | ".join(safe(value) for value in row) + " |" for row in rows
    ) + "\n"


def render_report(snapshots):
    """Return Markdown for ordered (filename, N-Quads text) snapshots."""
    if not snapshots:
        return "No learner-record*.nq file was found. Export from the Learning panel and upload it beside this notebook."
    parsed = [(name, parse_export(text)) for name, text in snapshots]
    latest = parsed[-1][1]
    lines = ["# Your learning record", "", "These are snapshots you exported from the Learning panel. Viewing them does not change your record.", ""]
    lines += ["## Graph at each export", ""]
    lines.append(table(["Export", "Observations", "Evidence assertions", "Estimates", "Gaps", "Recommendations"], [
        (name, *graph_counts(rows).values()) for name, rows in parsed
    ]))

    lines += ["## Attempts in the latest export", "", "Each attempt stays in the browser-local learner record, including unfinished and incorrect attempts.", ""]
    lines.append(table(["When", "Activity", "Outcome", "Hints used"], [
        (property_of(latest, s, "generatedAtTime"), property_of(latest, s, "activity"),
         property_of(latest, s, "outcome"), property_of(latest, s, "guidanceLevel"))
        for s in sorted(subjects(latest, "Observation"), key=lambda s: property_of(latest, s, "generatedAtTime"))
    ]))

    lines += ["## Current interpretation", "", "Correct attempts can create evidence assertions. Hints and repeats can exclude those assertions from the estimate. The estimate, gap, and recommendation statements are recalculated from the record.", ""]
    lines.append(table(["Capability", "Estimated level"], [
        (property_of(latest, s, "capability"), property_of(latest, s, "estimatedLevel"))
        for s in sorted(subjects(latest, "CapabilityEstimate"))
    ]))
    lines.append(table(["Capability", "Gap state", "Profile status"], [
        (property_of(latest, s, "capability"), property_of(latest, s, "gapState"), property_of(latest, s, "profileStatus"))
        for s in sorted(subjects(latest, "GapAssessment"))
    ]))
    lines.append(table(["Rank", "Recommended activity", "Reason"], [
        (property_of(latest, s, "rank"), property_of(latest, s, "recommendsActivity"),
         ", ".join(sorted(short(o) for subj, p, o, _, _ in latest if subj == s and p.endswith("#reasonCode"))))
        for s in sorted(subjects(latest, "Recommendation"), key=lambda s: int(property_of(latest, s, "rank")))
    ]))

    if len(parsed) > 1:
        lines += ["## What changed between exports", "", "The evidence graph grows with attempts. The derived graph is recalculated, so statements can be added or removed when a recommendation changes. Each export also has a new assessment receipt.", ""]
        for (before_name, before), (after_name, after) in zip(parsed, parsed[1:]):
            old = {line for *_, line in before}
            new = {line for *_, line in after}
            added_obs = subjects(after, "Observation") - subjects(before, "Observation")
            lines += [f"### {before_name} → {after_name}", "",
                      f"New attempts: **{len(added_obs)}**; N-Quads added: **{len(new - old)}**; N-Quads removed: **{len(old - new)}**.", ""]
            lines.append(table(["New attempt", "Outcome"], [
                (property_of(after, s, "activity"), property_of(after, s, "outcome")) for s in sorted(added_obs)
            ]))
            old_rec = {property_of(before, s, "recommendsActivity") for s in subjects(before, "Recommendation")}
            new_rec = {property_of(after, s, "recommendsActivity") for s in subjects(after, "Recommendation")}
            lines += ["Recommendations added: " + (", ".join(sorted(new_rec - old_rec)) or "none") + ".",
                      "Recommendations removed: " + (", ".join(sorted(old_rec - new_rec)) or "none") + ".", ""]

    lines += ["## Reading the graph", "", "`Observation → EvidenceAssertion → CapabilityEstimate → GapAssessment → Recommendation`", "",
              "An incorrect or unfinished observation remains in the record without creating evidence. A correct observation may create evidence, subject to the hint limit and repeat rule. The exported `.nq` file contains the complete graph, including the assessment receipt."]
    return "\n".join(lines)


def find_exports():
    """Look for exports uploaded beside this notebook."""
    return sorted(Path.cwd().glob("learner-record*.nq"))
