# Capability packs

Status: proposed design. Not yet implemented.

## 1. Purpose

A **capability pack** is a versioned, reviewable, downloadable unit of adaptive
learning content for one domain, such as public health informatics or GIS for
epidemiologists. Learners and programmes install packs from a **pack catalog**
into a JupyterLite site. The adaptive-learning engine then guides learners
through the pack's exercises and case simulations.

Packs let a programme adopt courses one at a time, update them independently,
and share common foundations (audiences, proficiency scale, characters,
scenario world) across courses.

The first catalog serves Field Epidemiology Training Programs (FETP):

| Pack | Status |
| --- | --- |
| FETP core (shared foundation) | Planned, required by the other FETP packs |
| Public health informatics | First content pack (15 units) |
| GIS for epidemiologists | Future pack |

## 2. Terms

| Term | Meaning |
| --- | --- |
| Capability pack | Repository plus released archive: `al:` catalog data, exercise and case specs, generated notebooks and checks, synthetic data, and a manifest |
| Pack release | One immutable version of a pack: archive, manifest, checksums |
| Pack catalog | Reviewed index of packs and their releases, published as JSON and as DCAT RDF |
| Core pack | A pack containing shared definitions that other packs depend on; it has no exercises of its own |
| Adaptive-learning engine | The deterministic component that turns observations into evidence, estimates, gaps, and recommendations (`src/engine/`) |
| Jupyter kernel | A language runtime (Python via Pyodide, R via xeus-r) where learners run exercises |

## 3. Repositories

```text
adaptive-learning-ontology   al: upper ontology, SHACL shapes; defines the pack vocabulary (section 8)
jupyterlite-prototype        engine, JupyterLite extension, site build; becomes the pack runtime and pack tooling
<program>-catalog            pack catalog for one programme (e.g. fetp-catalog)
<program>-core               shared foundation and programme ontology for that programme's packs
<program>-pack-<domain>      one repository per content pack
```

A pack repository holds **content only**. Tooling (catalog projection, exercise
generation, validation, archive building) is provided by a pinned version of
the pack tooling from this repository (section 11).

## 4. Ontology layers

Each course and each unit has its own ontology module. Modules connect to `al:`
through a programme ontology held in the programme's core pack:

```text
al:  →  fetp: (fetp-core)  →  course ontology (one per pack)  →  unit modules (one per unit)
```

Unit modules use the course namespace, so moving content between units never
changes term IRIs. The FETP scoping document in `fetp-core`
(`docs/ontology-scope.md`) defines each layer, the `al:` additions for course and
unit structure, and the shapes every course and unit module must satisfy.

## 5. Pack repository layout

```text
pack.yml                     pack metadata (section 6)
README.md  LICENSE  LICENSE-CODE  CONTRIBUTING.md
.github/workflows/           validate → generate → test → preview → release
.github/CODEOWNERS           unit owners review their units

catalog/                     al: source of truth (TriG), validated by the al-core shapes
  framework.trig             capabilities and prerequisites
  targets.trig               per-audience targets and critical gates
  policy.trig                estimator policy and stage ceilings (or inherited from core)

units/unit-NN-slug/
  unit.ttl                   unit ontology module (course namespace)
  unit.yml                   title, aim, learning objectives → capability IRIs, estimated time, status
  exercises/*.yml            one spec → Python and R notebooks plus checks
  cases/*.yml                case-simulation scenes, decisions, data releases
  knowledge-check.yml        structured items (pre/post tests; no free-text scoring)

case-study/                  this pack's episodes of the programme's shared scenario
data/generators/             seeded, deterministic synthetic-data generators
sources/                     sources.tsv and manifest.json only; original materials are fetched, not committed
tools/  tests/  docs/
content/                     GENERATED (gitignored): notebooks, checks, catalog projection, data
```

Authors edit specs. Notebooks, checks, and catalog projections are generated, so
the Python and R versions cannot drift and a release is reproducible from its tag.

## 6. `pack.yml`

```yaml
id: fetp-pack-informatics            # stable, lowercase, never reused
version: 1.2.0                       # semver; see section 7
title: Public health informatics for field epidemiologists
program: fetp
namespace: https://adaptive-learning-network.github.io/packs/fetp-informatics/ns#
license: { content: CC-BY-4.0, code: Apache-2.0 }
languages: [python, r]               # Jupyter kernel languages with exercises
requires:
  engine: ">=0.2 <0.3"
  ontology: ">=0.1 <0.2"             # al: release the catalog data conforms to
  packs:
    fetp-core: "^1.0"
audiences: [fetp-frontline, fetp-intermediate, fetp-advanced]   # defined in core
units: 15
```

## 7. Versioning and compatibility

- **Namespaces are stable across versions.** Capability, activity, and target
  IRIs never contain the version, so learner records survive updates. The
  version appears in `owl:versionIRI` and in the release.
- **Semantic versioning is defined by learner impact:**

  | Change | Version |
  | --- | --- |
  | Remove or re-meaning a capability; change a target level or critical gate; remove an activity | major |
  | Add capabilities, activities, units, languages, or cases | minor |
  | Fix text, hints, or data without changing what is assessed | patch |

- **Compatibility is checked at install time** against the engine version, the
  `al:` ontology version, and dependency ranges. An incompatible pack is not
  activated.
- **Updates are explicit.** The learner sees what changes before updating.
  Evidence keeps the activity and rule IRIs it was recorded under. When a major
  update retires a capability, estimates are recomputed under the new catalog,
  and evidence for retired capabilities is kept but shown as historical.

## 8. Ontology: pack vocabulary in `al:`

A small module in the `al:` ontology. It reuses DCAT 3 and SPDX checksums
instead of defining new structures.

| Term | Definition |
| --- | --- |
| `al:CapabilityPack` ⊑ `dcat:Dataset` | A pack across all its versions |
| pack release | `dcat:Dataset` with `dcat:version`, linked by `dcat:hasVersion`, `dcat:isVersionOf` |
| release archive | `dcat:Distribution` with `dcat:downloadURL`, `dcat:mediaType application/zip`, `spdx:checksum` |
| `al:PackCatalog` ⊑ `dcat:Catalog` | A programme's catalog; `dcat:dataset` lists packs |
| `al:requiresPack` | Release → pack, with a version range (`al:versionRange`) |
| `dcterms:conformsTo` | Release → the `al:` ontology release it conforms to |
| `al:providesFramework` | Release → the `al:CapabilityFramework`(s) it contains |

SHACL shapes for releases require a version, a checksum, a licence, an
ontology conformance link, and acyclic `al:requiresPack`.

## 9. Pack catalog

The catalog repository publishes, through GitHub Pages:

- `catalog.json`: the projection the runtime reads (packs, releases, URLs,
  checksums, requirements);
- `catalog.ttl`: the same content as DCAT RDF, validated by the pack shapes;
- a human-readable index page.

**Registration.** A pack release workflow opens a pull request on the catalog
repository adding the new release. Catalog maintainers review it before merging:

- licence and source permissions are recorded;
- catalog data conforms to the `al:` shapes, and the pack's tests passed in CI;
- check code was reviewed (section 10);
- datasets are synthetic, or real de-identified data has documented approval;
- version bump matches the change (section 7).

## 10. Trust and safety

- **Packs are mostly data.** The exception is exercise check code (Python or R),
  which runs in the learner's own Jupyter kernel inside the browser sandbox. It
  may read only the learner's variables and print one outcome line. It must not
  use the network, the file system beyond the pack, or credentials. Reviewers
  check this at registration.
- **Archives are verified.** The runtime verifies every file's SHA-256 against
  the release manifest, and the release archive's checksum against the catalog,
  before activating anything.
- **No learner data in packs.** Learner records stay in the learner's browser
  and are exported only by the learner.
- **Data in packs is synthetic by default.** Real de-identified datasets need the
  data owner's approval, a licence, and a privacy review, and may be limited to
  non-public catalogs.
- **Original course materials are not redistributed.** Pack repositories keep
  source references and checksums; licensed originals stay with their owners.
- **Self-checks are formative.** Evidence from learner-run checks is capped by
  the policy's stage ceilings (simulation at most).

## 11. Tooling and release pipeline

The generators currently in this repository (`scripts/build_catalog.py`,
`scripts/make_exercises.py`, `scripts/validate_export.py`) become a pack-tooling
command, versioned with the engine:

```text
al-pack validate   pack.yml, specs, catalog TriG against al: shapes, dependency resolution
al-pack generate   notebooks and checks (Python, R) from specs; catalog projection
al-pack test       check parity across languages; engine scenarios; export SHACL validation
al-pack preview    JupyterLite site with this pack and its dependencies preinstalled
al-pack release    archive + pack-manifest.json (per-file SHA-256) for a tag
```

A pack repository's CI runs validate → generate → test → preview on every pull
request. On a version tag it builds the archive, attaches it to a GitHub Release,
and opens the catalog registration pull request.

## 12. Runtime changes in this repository

1. **Multiple catalogs.** The engine loads the union of installed packs'
   catalog projections. Cross-pack prerequisites resolve through IRIs.
2. **Pack installer.** A catalog browser in the learning panel lists packs. Install
   runs: download, verify checksums, check compatibility, install dependencies,
   unpack to `packs/<id>/<version>/` in JupyterLite contents, then register the
   catalog. Uninstall removes content but keeps the learner record.
3. **One learner record across packs.** Observations reference activity IRIs from
   any installed pack. Exports include the installed pack versions.
4. **Pack tooling extracted** as described in section 11.

## 13. Phased plan

1. Add the pack vocabulary, and the course and unit structure terms, to the `al:` ontology.
2. Extract the pack tooling from this repository's scripts.
3. Create the FETP catalog and `fetp-core` (programme ontology, shapes). Restructure the informatics
   course folder as the first content pack.
4. Add multi-catalog loading and the pack installer to the engine and extension.
5. Convert the first units, starting with those best suited to hands-on
   exercises.
6. Pilot with synthetic learners, then a facilitated cohort.

## 14. Open decisions

1. Repository names: `fetp-catalog`, `fetp-core`, `fetp-pack-informatics`,
   `fetp-pack-gis`.
2. Visibility and licences for pack content; whether the FETP catalog is public.
3. Real de-identified case-study datasets: allowed in which catalogs, and under
   what approval.
4. Whether the core pack also carries the shared scenario world (fictional
   country, health information system, surveillance data), or that becomes a
   separate scenario pack.
5. How a pack represents facilitated, in-person activities (discussion, group
   work) alongside notebooks: as `al:LearningActivity` with facilitator-reviewed
   evidence, or as non-assessed agenda items.
6. Whether pre-tests feed the engine as knowledge-check evidence, or only set the
   starting recommendations.
