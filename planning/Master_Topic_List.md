# Engineering Standards — Master Topic List

Running tracker for the whole standards effort, across both process and language standards: what exists, what is open, who owes a decision, and what was deliberately parked. Every open thread lives here — if it is not in this file it will be forgotten.

Update this file in the same commit as the change that affects it.

---

## Format contract

Read this before editing, so the file stays mechanically scannable.

- **Every item has a permanent ID.** IDs are never reused and never renumbered, even after an item is done. A done row stays in the table so the decision history is readable.
- **ID prefixes by kind:**
  - `T-nn` — **Topic.** A subject with no section written yet.
  - `D-nn` — **Decision.** Needs a human to choose. Cannot be resolved by drafting.
  - `F-nn` — **Finding.** A defect in material already written.
  - `FW-nn` — **Forward note.** Something deliberately parked because the section that should hold it does not exist yet. These are the easiest to lose; they are why this file exists.
  - `X-nn` — **Deferred.** Out of scope on purpose, with the reason recorded.
  - `R-nn` — **Resolved.** A settled question, kept so it is not re-litigated.
- **Status vocabulary is fixed:** `open` · `in progress` · `done` · `blocked` · `deferred`.
- **"Lands in"** names the section or file the item resolves into. `—` means not yet decided.
- Anything needing a human decision gets `D-nn`, even if it also appears as part of a topic.

---

## Section status

Sections are prefixed by domain: `P` for process (any language), `C` for C++. The prefix is part of the number, so `P1.3.1` and `C3.1.4` are self-describing and new sections append inside their domain without renumbering anything.

| | Section | File | Status |
|---|---|---|---|
| **P1** | Git Workflow | `standards/process/P1-git-workflow.md` | done |
| **P2** | Versioning | `standards/process/P2-versioning.md` | done |
| **P3** | Classification & Markings | `standards/process/P3-classification-and-markings.md` | done |
| **C1** | Naming Conventions | `standards/cpp/C1-naming-conventions.md` | done |
| **C2** | Documentation (Doxygen) | `standards/cpp/C2-documentation-doxygen.md` | done |
| **C3** | Code Style | `standards/cpp/C3-code-style.md` | done |
| — | Constants Registry | `standards/constants.md` | done |
| — | Enforcement Summary | `standards/enforcement-summary.md` | done — extend as sections land |
| — | References | `standards/references.md` | done |
| — | Index / front door | `README.md` | done — the only file at the repository root |
| — | Project Profile | `project/PROJECT_PROFILE.md` | done |
| A–D | Appendices | `standards/cpp/`, `standards/process/` | done |

Section numbering is preserved from the original single-file guide, so every cross-reference (`P1.2.3`, `C3.1.4`, `the Enforcement Summary`) still resolves. New sections take numbers 8 and up. the Enforcement Summary keeps its number and sits last in reading order.

---

## T — Topics not yet written

Working method: propose rule headings first, agree the list, then draft prose for what survives.

| ID | Topic | Lands in | Status |
|---|---|---|---|
| T-01 | CMake structure — the last of the original five categories | C4 (CMake) | open |
| T-02 | Toolchain & compiler config — C++23 feature subset, MSVC/GCC parity, warnings-as-errors flags | C5 (toolchain) | open |
| T-03 | Core/GUI architectural boundary — the Qt-free `core` rule | C6 (architecture) | open |
| T-04 | GUI architecture pattern, including Qt signal/slot naming | C6 (architecture) | open |
| T-05 | API stability / deprecation policy for `core` | C6 (architecture) | open |
| T-06 | Module & code ownership map | C6 (architecture) | open |
| T-07 | Third-party library rules — Qt, HDF5, Vulkan, DuckDB, CLI11, zlib/zip | C7 (third-party) | open |
| T-08 | Dependency & vulnerability management | C7 (third-party) | open |
| T-09 | Testing standards — GoogleTest/QTest boundary | C8 (testing) | open |
| T-10 | Sanitizers in testing | C8 (testing) | open |
| T-11 | Logging strategy | C9 (logging) | open |
| T-12 | User-facing error message conventions | C10 (error messages) | open |
| T-13 | Threading & concurrency model | C11 (threading) | open |
| T-14 | Static analysis tooling scope beyond clang-tidy | C12 (static analysis) | open |
| T-15 | Performance & benchmarking practices | C13 (performance) | open |
| T-16 | Secrets management | P4 (security) | open |
| T-17 | Data/file format versioning | C14 (data formats) | open |
| T-18 | Application settings & config persistence | C14 (data formats) | open |
| T-19 | Packaging & installer standards | P5 (packaging) | open |
| T-20 | Crash reporting & telemetry | P6 (telemetry) | open |
| T-21 | Accessibility (a11y) | C15 (a11y/i18n) | open |
| T-22 | Internationalization / localization | C15 (a11y/i18n) | open |
| T-23 | Developer onboarding | P7 (onboarding) | open |
| T-24 | User documentation — README, CLI `--help`, in-app help, where user docs live | P8 (user docs) | open |

Landing places above are indicative, not committed. What is settled is the domain each topic belongs to — process or C++ — since that decides which folder it lands in and therefore its prefix.

---

## D — Decisions needing a human

Nothing here can be resolved by drafting. Each blocks or reshapes the work named in "Lands in".

| ID | Decision | Lands in | Status |
|---|---|---|---|
| D-01 | **Does MISRA C++:2023 apply to the contract?** If yes it conflicts head-on with C3.3.1 on exceptions, and C3 and the Enforcement Summary need rework before further polish. Largest single open question. | C3, the Enforcement Summary | open |
| D-02 | Qt licensing: is a commercial licence held? If not, does the shipping configuration satisfy LGPLv3's relinking requirement? Not a developer decision — needs whoever owns licence compliance. Packaging depends on the answer. | § 11, § 20 | open |
| D-03 | C3.2.2 complexity metric. The rule names a McCabe ceiling of 10; no clang-tidy check computes McCabe. Appendix C substitutes `BranchThreshold` + cognitive complexity as a documented approximation. Ratify that, or adopt a real McCabe tool (`lizard`) in CI. | C3.2.2, App. C | open |
| D-04 | JSON library: glaze vs nlohmann. | C7 (third-party) | open |
| D-05 | Logging library. | C9 (logging) | open |
| D-06 | Whether to add a **"Deviations from cited standards" appendix** recording where this guide knowingly departs from Google / LLVM / Core Guidelines (see F-36). Recommended: yes — it is cheaper than changing any rule and removes the ambiguity. | new appendix | open |
| D-07 | Stale/abandoned branch policy — wanted at all? Flagged in the original list as "unclear if this is even wanted". | § P1.5 | open |
| D-08 | Blank-line conventions within a file, beyond what clang-format enforces — wanted at all? | § C3.5 | open |
| D-09 | Member variable decoration: keep C1.9's no-`m_`/no-trailing-underscore rule, or adopt Google's `foo_`. | C1.9 | **done** — keep C1.9 as written |
| D-10 | Confirm the scope column in the Constants Registry | the Constants Registry | **done** — review process and cadence are `org`; classification is `org`; layout, scopes and library list are `project` |
| D-11 | C-49: replace the `Hdf5Reader` running example with a domain-neutral one, or keep it? 35 rules affected — the largest single edit in the generalization. | §P1, 3, 5, 6 | **done** — replaced with `RecordReader`/`ReadError`/`FileHandle`; matches C-49 in the Constants Registry |
| D-12 | C-47: poison-pill rule | P2 | **done** — moved verbatim to `project/PROJECT_PROFILE.md`; section number 2.5 retired, not reassigned |
| D-13 | `assert()` restricted to profiled hot paths only (C3.3.3) vs CERT/Core Guidelines' broader recommended usage — genuinely worth reconsidering, not just documenting as a deviation. | C3.3.3 | open |

---

## F — Findings against written material

From the standards review. Done rows retained deliberately.

| ID | Finding | Lands in | Status |
|---|---|---|---|
| F-01 | C3.2.2 cited a clang-tidy option that does not exist | C3.2.2 | done — see D-03 for the open half |
| F-02 | C3 GOOD examples used the trailing-underscore form C1.9 bans | C3 | done |
| F-03 | P1.2.2 and P1.3.1 stated different commit-type vocabularies | P1.2.2 | done |
| F-04 | C3.5.8's include-order example contradicted clang-format's actual sort | C3.5.8, App. B | done |
| F-05 | P2.4.2 named an unverified git-cliff flag | P2.4.2 | done — see FW-02 |
| F-06 | P1 called the workflow GitHub Flow while describing GitLab Flow | P1 | done |
| F-07 | "PR" used throughout a GitLab project that has no pull requests | all | done |
| F-08 | C1.9 had no answer for constructor-parameter/member shadowing | C1.20 | done |
| F-09 | C3.1.26 illustrated self-assignment with `new`/`delete`, which C3.4.1 bans | C3.1.26 | done |
| F-10 | No `.gitattributes` / line-ending rule | P1.6.3 | done |
| F-11 | Code fences all tagged `cpp`; 15 contained git, gitignore, gitattributes, Doxygen, YAML or TOML | all | done |
| F-12 | Heading levels skip `h2 → h4` and `h1 → h4` in 21 places (markdownlint MD001) | all | done |
| F-13 | Sections 3/4/5 use two-level numbering; 1/2/6 use three-level | C1, 4, 5 | done — unnumbered group headings, so no rule was renumbered |
| F-14 | C2.3.1 and C2.3.2 render as siblings of C2.3, not children | C2 | done |
| F-15 | Appendix B lists `IncludeCategories` in priority order 2, 3, 1 — correct but reads as an error | App. B | done — reordered 1/2/3, with a note that clang-format takes the first match |
| F-16 | No copyright/licence header rule; no SPDX identifier. Google and LLVM both require one | P3 | open |
| F-17 | `// UNCLASSIFIED` is a classification statement, not a CUI marking. Check against 32 CFR 2002 / ISOO CUI Marking Handbook / DoDI 5200.48 | P3 | open |
| F-18 | No `.editorconfig` — covers files clang-format does not touch | § P1.6 | open |
| F-19 | `CHANGELOG.md` is mandated by P2.4.1 with no format standard named. Keep a Changelog 1.1.0 is the de-facto choice and what git-cliff targets | P2 | open |
| F-20 | `#pragma once` is never explicitly prohibited — only implied by C1.3 and C1.14 | C1 | open |
| F-21 | Enforcement Summary covers ~45 of 106 rules. The "unlisted = Advisory" default is sound, but nothing checks that every claimed hard gate appears in the table | the Enforcement Summary | open |
| F-22 | No deviation/waiver process — what a developer does when a rule genuinely must be broken, who approves, how it is recorded in code | new rule | open |
| F-23 | 29 of 106 rules have no RATIONALE, 22 no GOOD, 27 no BAD, with no stated policy on when they are optional | all | open |
| F-24 | Commit types and scopes overlap (`ci`, `build`, `docs`, `test` are both), permitting `ci(ci):` | P1.3.1 | open |
| F-25 | No normative keyword convention — "must", "should", "is", "never" used interchangeably. RFC 2119 / BCP 14 is the standard fix | all | open |
| F-26 | Exception class naming convention (`InvalidRecordException` vs `RecordError`) still undelivered | C1 | open |
| F-27 | `std::move` guidance — explicit call vs relying on RVO/implicit move | § C3.1 | open |
| F-28 | Fixed-width integer types vs `int`/`size_t` — no stated preference, and this codebase parses binary formats | § C3.1 | open |
| F-29 | Uniform/brace initialization style not addressed | § C3.1 | open |
| F-30 | Structured bindings not addressed | § C3.1 | open |
| F-31 | Guide was written as a product document, not a standard | all | done — option B applied: example de-domained, 2.5 and the data-sensitivity answer moved to `project/PROJECT_PROFILE.md`, org-wide tooling kept |
| F-32 | Constant values duplicated between rules and the registry/profile | all | done — turned out much smaller than framed: 39 of 48 constants are `org` scope, so abstracting prose to role names would have cost readability for an edit made once every few years. Fixed the two genuine duplications (C-14 in P1.3.1, C-27 in P1.8.1), adopted a cite-the-constant convention, and added `tools/check_constants.py` to make drift detectable |
| F-33 | No index or title page; the document set did not state its own scope | `README.md` | done |
| F-34 | `CPP_Code_Standards_and_Styling_Guide.md` was left in place after the split and never updated, so it still carried the GitHub Flow misnomer, 49 `Hdf5Reader` mentions, 57 `Manual PR checklist` labels, the nonexistent `CyclomaticComplexityThreshold`, rule 2.5 and the product name — a stale duplicate of the entire guide | repo root | done — deleted; recoverable at `729b9de` |
| F-35 | Four documents sat at the repository root, so a newcomer had no single obvious starting point | repo layout | done — `standards/`, `project/`, `planning/`, `tools/`; only `README.md` remains at the root |
| F-36 | Five style choices deviate from cited external standards without being documented as deliberate: UPPER_SNAKE constants (C1.11) vs Google's `kFoo`; CamelCase enumerators (C1.6) vs Google's `kFoo`; `size_t` for indices (C3.1.20) vs Core Guidelines ES.107; `noexcept` on move/swap only (C3.1.16) vs Core Guidelines F.6; Allman brace style, 4-space indent, 100-column limit (C3.5) vs the Google/LLVM house styles those guides actually use | new appendix (see D-06) | open |
| F-37 | Four rules govern something with no external standard to check against, and were never labeled as a deliberate house convention: the umbrella-branch fast-forward exception (P1.2.3) has no external precedent; the poison-pill rebuild (now in `project/PROJECT_PROFILE.md`) never got the suggested explicit failure-mode checklist language; `@brief` third-person mood (C2) is not labeled as a house convention; local-constant camelBack (C1.12) is accepted as permanently advisory but never stated as such | P1.2.3, C2, C1.12, `project/PROJECT_PROFILE.md` | open |
| F-38 | "Start here" in README still points at nearly all of P1, C1 and C3 (~72 of 106 rules) as first reading for a new developer — the original complaint from the first README round, restated after the retitle rather than narrowed | `README.md` | open |
| F-39 | Commit `f6fd366` (forward-reference cleanup: C1.14, C3.1.20, P1.6.2, P1.8.1, P2.1.1, P3.1, C2.2, the Constants Registry, the Enforcement Summary — 9 files) had no tracker entry | all | done — recorded after the fact |

---

## FW — Forward notes

Parked because the section that should hold them does not exist yet. Check this table when writing the named section.

| ID | Note | Check when writing |
|---|---|---|
| FW-01 | **Source encoding is UTF-8 without BOM, and the build must pass `/utf-8`.** Without it MSVC reads source as the active code page and emits C4819 on any non-ASCII character — a build error under this project's warnings-as-errors. Split out of P1.6.3, which covers only the repository side. | § 9 Toolchain |
| FW-02 | git-cliff's first-parent flag spelling is unverified — P2.4.2 now states the requirement rather than the flag. Confirm against the installed version. | P2 revisit / CI work |
| FW-03 | MSVC C4458 behaviour is inferred, not tested — no MSVC available in the drafting environment. C1.20's enforcement claim rests on it. GCC `-Wshadow` and Clang `-Wshadow-all` were verified directly. | C1.20 / § 9 |
| FW-04 | Clang's plain `-Wshadow` does **not** flag constructor-parameter shadowing; `-Wshadow-all` or `-Wshadow-field-in-constructor` is required. Matters when a Clang toolchain is added. | § 9 Toolchain |
| FW-05 | Appendix D's Jira base URL is a placeholder. Set it before the first release cut or every changelog ticket link 404s. | P2 / first release |
| FW-06 | P1.6.2's process for adding to `test_data/` is still undocumented — approval step, size limits, manifest. | § P1.6 / § 12 Testing |
| FW-07 | Appendix C's `ConstexprVariableCase` is deliberately unset: clang-tidy resolves a constexpr local against both it and `LocalConstantCase` with undocumented precedence, so C1.12 stays advisory. Revisit if upstream clarifies. | § 16 Static analysis |
| FW-08 | After committing `.gitattributes`, run `git add --renormalize .` once as its own chore commit. | on adopting P1.6.3 |

---

## X — Deferred on purpose

| ID | Item | Reason |
|---|---|---|
| X-01 | Standing up GitLab CI | Discussed and deliberately deferred. Converts most "Manual MR checklist" rows in the Enforcement Summary into real gates. |
| X-02 | Docker container creation | Deferred. |
| X-03 | Dedicated Linux building and testing | Deferred. Blocks UBSan/TSan and all cross-toolchain verification. |

---

## R — Resolved, recorded so it is not re-litigated

| ID | Question | Answer |
|---|---|---|
| R-01 | Does this tool handle PHI/PII? | No. Only CUI/export-control applies. Recorded in 4.2. |
| R-02 | Which git workflow is this? | GitLab Flow with a production branch — not GitHub Flow. Corrected in P1. |
| R-03 | Does `this->member` clear the C4458 shadowing error? | No. The diagnostic fires at the parameter declaration, not the use. Verified with GCC and Clang. Recorded in 3.20. |
| R-04 | Does the pre-1.0 MINOR/PATCH derivation in P2.1.1 conflict with SemVer? | No — SemVer §4 leaves 0.y.z undefined, so this is the guide's own addition, correctly scoped. No action needed. |
| R-05 | Is this standard scoped to "this organization" or "this team"? | This organization — confirmed explicitly. |
| R-06 | Should the standard carry its own "known gaps" appendix inside `standards/`, or is `planning/Master_Topic_List.md` the single tracker? | Tracker only. No appendix. |
| R-07 | Should sections split into `process/` (any language) and `cpp/` (C++-specific) folders, with P/C domain-prefixed numbering? | Yes — implemented across `standards/process/` and `standards/cpp/`, 377 cross-references rewritten. **Reopened**: the full document review starting now includes this decision. |
| R-08 | Is this a C++-only standard or a multi-domain (process + language) standard? | Multi-domain — retitled "Engineering Standards," framed as process applying to any language plus one folder per language. **Reopened**: included in the full document review starting now. |

---

## Reference standards

C++ Core Guidelines, Google C++ Style Guide, LLVM Coding Standards, and SEI CERT C++ are the standing cross-reference set for Code Style and Naming. Qt's own conventions get added once GUI topics are covered. MISRA C++:2023 is unresolved — see D-01.

See `standards/references.md` for the full list with links.

---

## Recovering reverted work

An earlier pass drafted several unwritten sections, then reverted them so the decisions inside could be made deliberately rather than inherited. Not all of it survives, and the difference matters:

**Recoverable** — committed in `a879925`, retrievable with `git show a879925:standards/<file>`:

| File | Covers |
|---|---|
| `standards/08-cmake-and-build-system.md` | T-01 |
| `standards/09-toolchain-and-compiler.md` | T-02 |
| `standards/10-architecture-and-boundaries.md` | T-03, T-04, T-05, T-06 |
| `standards/11-third-party-libraries.md` | T-07, T-08 |

That commit's versions of P1, C1 and C3 also contain draft rules for F-26 (exception class naming), F-27 (`std::move`), F-28 (fixed-width integers), F-29 (brace initialization), F-30 (structured bindings), D-07 (stale branches) and D-08 (blank lines). Diff against the current files to extract them.

**Gone** — drafted but never committed, so no copy exists: testing (T-09, T-10) and logging (T-11). If those are wanted they get written from scratch.

Treat everything recoverable as a rough draft carrying unratified decisions, not as reviewed material.
