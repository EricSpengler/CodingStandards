# Project Profile — CRNA PA Data Extraction & Visual Analysis

The standards in `standards/` are written to be shared across projects. This file holds everything true of **this** project and not necessarily of any other: the values behind the `project`- and `product`-scoped constants in the Constants Registry, and the rules that exist because of this product's requirements rather than because of good C++ practice.

A new project forks this file and rewrites it. It does not fork the standard.

Constant IDs below refer to [`standards/constants.md`](../standards/constants.md), relative to the repository root.

---

## Identity

| Constant | Value |
|---|---|
| C-46 Product name | CRNA PA Data Extraction & Visual Analysis |
| C-27 Supported platforms | Windows only today. No Linux development environment exists yet; see the deferred items on the master topic list |

## Code layout

| Constant | Value |
|---|---|
| C-28 Top-level source directories | `core`, `gui` |
| C-14 Commit scope vocabulary | core, gui, cmake, ci, docs, tests, build |
| C-30 Test fixture directory | `test_data/` |
| C-31 Namespace documentation file | `docs/namespaces.h` |

## Dependencies

| Constant | Value |
|---|---|
| C-32 Third-party include prefixes | Qt, hdf5, H5, vulkan, zip, zlib, duckdb, CLI, glaze, nlohmann |

These are the prefixes that populate the third-party group in `IncludeCategories` (Appendix B) and the `HeaderFilterRegex` exclusion in Appendix C. The standard describes the *grouping*; this list is what makes it executable here.

Libraries in use: Qt 6 (GUI), HDF5 (primary data format), Vulkan (visualization), DuckDB (analytical queries), zlib (compression), CLI11 (command-line parsing). The JSON library is undecided — see D-04 on the master topic list.

## Data sensitivity determination

Required by rule 4.2.

**This tool does not process PHI, PII, or other personally-regulated data.** CUI and export control, per P3.1, are the only sensitivity classifications that apply to this codebase and the data it handles.

Confirmed with the team rather than inferred from the project name. If a future feature ingests personal data this determination changes, and the standard does not currently contain the data-handling topic that would then be needed — file-at-rest encryption, logging restrictions around sensitive fields, retention policy.

| Constant | Value |
|---|---|
| C-45 Export-control point of contact | *unassigned — needs a name* |

---

## Product-specific release requirements

The following was rule 2.5 in the standard. It is a product licensing and distribution requirement, not a coding standard, so it lives here. The text is unchanged from the version that was in `standards/process/P2-versioning.md`; references to other rules still point at the standard.

## P2.5 Poison-pill reset rebuild

### P2.5.1 Day-14 rebuild fallback when nothing is releasable

**RULE**  The tool has a poison-pill license mechanism: builds expire and shut down 21 days after being built, by design, to force users onto current versions during testing. Every sprint close-out (day 14, biweekly) produces a build. If the sprint's commits don't warrant a version bump per P2.1, no new tag or changelog entry is created — instead, release at its current tip is rebuilt and repackaged as-is (same source, same version tag, fresh build/package output only) purely to reset the license expiry timer.

**RATIONALE**  Anchoring the rebuild trigger to the existing sprint close-out means there's no separate calendar to watch — “did we ship a build this sprint” is already a natural checkpoint the team hits every two weeks, and a build always goes out at day 14 regardless of which case applies, so the 21-day timer never has a chance to lapse.

**ENFORCEMENT**  Manual MR checklist / sprint close-out ritual.

---

## Open items specific to this project

- **D-02 — Qt licensing.** Qt's open-source licensing is LGPLv3, which carries obligations around dynamic linking and a recipient's ability to relink against a modified Qt. Whether a commercial licence is held, and if not how the shipped installer satisfies LGPLv3, needs a determination on record from whoever owns licence compliance. Packaging decisions depend on the answer. Nothing here is legal advice.
- **D-04 — JSON library**, glaze versus nlohmann.
- **C-45** — the export-control point of contact named in P3.1 is currently unnamed.
- **FW-05** — the Jira base URL in `cliff.toml` (Appendix D) is a placeholder and must be set before the first release cut, or every changelog ticket link 404s.
