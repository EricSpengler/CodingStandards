# C++ Standards & Styling Guide — Master Topic List

Running tracker for the whole standards effort: what exists, what is open, who owes a decision, and what was deliberately parked. Every open thread lives here — if it is not in this file it will be forgotten.

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

| # | Section | File | Status |
|---|---|---|---|
| 0 | Constants Registry | `standards/00-constants.md` | done — 49 constants, scope column settled |
| 1 | Git Workflow | `standards/01-git-workflow.md` | done |
| 2 | Versioning | `standards/02-versioning.md` | done |
| 3 | Naming Conventions | `standards/03-naming-conventions.md` | done |
| 4 | Classification & Export Control | `standards/04-classification-and-export-control.md` | done |
| 5 | Documentation (Doxygen) | `standards/05-documentation-doxygen.md` | done |
| 6 | Code Style | `standards/06-code-style.md` | done |
| 7 | Enforcement Summary | `standards/07-enforcement-summary.md` | done — extend as sections land |
| — | Index / front door | `README.md` | done |
| — | Project Profile | `PROJECT_PROFILE.md` | done — holds every `project`- and `product`-scoped value |
| A | Example Doxyfile | `standards/appendix-a-doxyfile.md` | done |
| B | Example .clang-format | `standards/appendix-b-clang-format.md` | done |
| C | Example .clang-tidy | `standards/appendix-c-clang-tidy.md` | done |
| D | Example cliff.toml | `standards/appendix-d-cliff-toml.md` | done |

Section numbering is preserved from the original single-file guide, so every cross-reference (`1.2.3`, `6.1.4`, `Section 7`) still resolves. New sections take numbers 8 and up. Section 7 keeps its number and sits last in reading order.

---

## T — Topics not yet written

Working method: propose rule headings first, agree the list, then draft prose for what survives.

| ID | Topic | Lands in | Status |
|---|---|---|---|
| T-01 | CMake structure — the last of the original five categories | § 8 | open |
| T-02 | Toolchain & compiler config — C++23 feature subset, MSVC/GCC parity, warnings-as-errors flags | § 9 | open |
| T-03 | Core/GUI architectural boundary — the Qt-free `core` rule | § 10 | open |
| T-04 | GUI architecture pattern, including Qt signal/slot naming | § 10 | open |
| T-05 | API stability / deprecation policy for `core` | § 10 | open |
| T-06 | Module & code ownership map | § 10 | open |
| T-07 | Third-party library rules — Qt, HDF5, Vulkan, DuckDB, CLI11, zlib/zip | § 11 | open |
| T-08 | Dependency & vulnerability management | § 11 | open |
| T-09 | Testing standards — GoogleTest/QTest boundary | § 12 | open |
| T-10 | Sanitizers in testing | § 12 | open |
| T-11 | Logging strategy | § 13 | open |
| T-12 | User-facing error message conventions | § 14 | open |
| T-13 | Threading & concurrency model | § 15 | open |
| T-14 | Static analysis tooling scope beyond clang-tidy | § 16 | open |
| T-15 | Performance & benchmarking practices | § 17 | open |
| T-16 | Secrets management | § 18 | open |
| T-17 | Data/file format versioning | § 19 | open |
| T-18 | Application settings & config persistence | § 19 | open |
| T-19 | Packaging & installer standards | § 20 | open |
| T-20 | Crash reporting & telemetry | § 21 | open |
| T-21 | Accessibility (a11y) | § 22 | open |
| T-22 | Internationalization / localization | § 22 | open |
| T-23 | Developer onboarding | § 23 | open |
| T-24 | User documentation — README, CLI `--help`, in-app help, where user docs live | § 24 | open |

Section numbers 8–24 above are the intended landing places, not a committed structure. They move if the shape changes.

---

## D — Decisions needing a human

Nothing here can be resolved by drafting. Each blocks or reshapes the work named in "Lands in".

| ID | Decision | Lands in | Status |
|---|---|---|---|
| D-01 | **Does MISRA C++:2023 apply to the contract?** If yes it conflicts head-on with 6.3.1 on exceptions, and Sections 6 and 7 need rework before further polish. Largest single open question. | § 6, § 7 | open |
| D-02 | Qt licensing: is a commercial licence held? If not, does the shipping configuration satisfy LGPLv3's relinking requirement? Not a developer decision — needs whoever owns licence compliance. Packaging depends on the answer. | § 11, § 20 | open |
| D-03 | 6.2.2 complexity metric. The rule names a McCabe ceiling of 10; no clang-tidy check computes McCabe. Appendix C substitutes `BranchThreshold` + cognitive complexity as a documented approximation. Ratify that, or adopt a real McCabe tool (`lizard`) in CI. | 6.2.2, App. C | open |
| D-04 | JSON library: glaze vs nlohmann. | § 11 | open |
| D-05 | Logging library. | § 13 | open |
| D-06 | Whether to add a **"Deviations from cited standards" appendix** recording where this guide knowingly departs from Google / LLVM / Core Guidelines (see F-10 … F-15). Recommended: yes — it is cheaper than changing any rule and removes the ambiguity. | new appendix | open |
| D-07 | Stale/abandoned branch policy — wanted at all? Flagged in the original list as "unclear if this is even wanted". | § 1.5 | open |
| D-08 | Blank-line conventions within a file, beyond what clang-format enforces — wanted at all? | § 6.5 | open |
| D-09 | Member variable decoration: keep 3.9's no-`m_`/no-trailing-underscore rule, or adopt Google's `foo_`. | 3.9 | **done** — keep 3.9 as written |
| D-10 | Confirm the scope column in § 0 | § 0 | **done** — review process and cadence are `org`; classification is `org`; layout, scopes and library list are `project` |
| D-11 | C-49: replace the `Hdf5Reader` running example with a domain-neutral one, or keep it? 35 rules affected — the largest single edit in the generalization. | §§ 1, 3, 5, 6 | open |
| D-12 | C-47: poison-pill rule | § 2 | **done** — moved verbatim to `PROJECT_PROFILE.md`; section number 2.5 retired, not reassigned |

---

## F — Findings against written material

From the standards review. Done rows retained deliberately.

| ID | Finding | Lands in | Status |
|---|---|---|---|
| F-01 | 6.2.2 cited a clang-tidy option that does not exist | 6.2.2 | done — see D-03 for the open half |
| F-02 | Section 6 GOOD examples used the trailing-underscore form 3.9 bans | § 6 | done |
| F-03 | 1.2.2 and 1.3.1 stated different commit-type vocabularies | 1.2.2 | done |
| F-04 | 6.5.8's include-order example contradicted clang-format's actual sort | 6.5.8, App. B | done |
| F-05 | 2.4.2 named an unverified git-cliff flag | 2.4.2 | done — see FW-02 |
| F-06 | Section 1 called the workflow GitHub Flow while describing GitLab Flow | § 1 | done |
| F-07 | "PR" used throughout a GitLab project that has no pull requests | all | done |
| F-08 | 3.9 had no answer for constructor-parameter/member shadowing | 3.20 | done |
| F-09 | 6.1.26 illustrated self-assignment with `new`/`delete`, which 6.4.1 bans | 6.1.26 | done |
| F-10 | No `.gitattributes` / line-ending rule | 1.6.3 | done |
| F-11 | Code fences all tagged `cpp`; 15 contained git, gitignore, gitattributes, Doxygen, YAML or TOML | all | done |
| F-12 | Heading levels skip `h2 → h4` and `h1 → h4` in 21 places (markdownlint MD001) | all | done |
| F-13 | Sections 3/4/5 use two-level numbering; 1/2/6 use three-level | § 3, 4, 5 | done — unnumbered group headings, so no rule was renumbered |
| F-14 | 5.3.1 and 5.3.2 render as siblings of 5.3, not children | § 5 | done |
| F-15 | Appendix B lists `IncludeCategories` in priority order 2, 3, 1 — correct but reads as an error | App. B | done — reordered 1/2/3, with a note that clang-format takes the first match |
| F-16 | No copyright/licence header rule; no SPDX identifier. Google and LLVM both require one | § 4 | open |
| F-17 | `// UNCLASSIFIED` is a classification statement, not a CUI marking. Check against 32 CFR 2002 / ISOO CUI Marking Handbook / DoDI 5200.48 | § 4 | open |
| F-18 | No `.editorconfig` — covers files clang-format does not touch | § 1.6 | open |
| F-19 | `CHANGELOG.md` is mandated by 2.4.1 with no format standard named. Keep a Changelog 1.1.0 is the de-facto choice and what git-cliff targets | § 2 | open |
| F-20 | `#pragma once` is never explicitly prohibited — only implied by 3.3 and 3.14 | § 3 | open |
| F-21 | Enforcement Summary covers ~45 of 106 rules. The "unlisted = Advisory" default is sound, but nothing checks that every claimed hard gate appears in the table | § 7 | open |
| F-22 | No deviation/waiver process — what a developer does when a rule genuinely must be broken, who approves, how it is recorded in code | new rule | open |
| F-23 | 29 of 106 rules have no RATIONALE, 22 no GOOD, 27 no BAD, with no stated policy on when they are optional | all | open |
| F-24 | Commit types and scopes overlap (`ci`, `build`, `docs`, `test` are both), permitting `ci(ci):` | 1.3.1 | open |
| F-25 | No normative keyword convention — "must", "should", "is", "never" used interchangeably. RFC 2119 / BCP 14 is the standard fix | all | open |
| F-26 | Exception class naming convention (`InvalidRecordException` vs `RecordError`) still undelivered | § 3 | open |
| F-27 | `std::move` guidance — explicit call vs relying on RVO/implicit move | § 6.1 | open |
| F-28 | Fixed-width integer types vs `int`/`size_t` — no stated preference, and this codebase parses binary formats | § 6.1 | open |
| F-29 | Uniform/brace initialization style not addressed | § 6.1 | open |
| F-30 | Structured bindings not addressed | § 6.1 | open |
| F-31 | Guide was written as a product document, not a standard | all | done — option B applied: example de-domained, 2.5 and the data-sensitivity answer moved to `PROJECT_PROFILE.md`, org-wide tooling kept |
| F-32 | Constant values duplicated between rules and the registry/profile | all | done — turned out much smaller than framed: 39 of 48 constants are `org` scope, so abstracting prose to role names would have cost readability for an edit made once every few years. Fixed the two genuine duplications (C-14 in 1.3.1, C-27 in 1.8.1), adopted a cite-the-constant convention, and added `tools/check_constants.py` to make drift detectable |
| F-33 | No index or title page; the document set did not state its own scope | `README.md` | done |
| F-34 | `CPP_Code_Standards_and_Styling_Guide.md` was left in place after the split and never updated, so it still carried the GitHub Flow misnomer, 49 `Hdf5Reader` mentions, 57 `Manual PR checklist` labels, the nonexistent `CyclomaticComplexityThreshold`, rule 2.5 and the product name — a stale duplicate of the entire guide | repo root | done — deleted; recoverable at `729b9de` |

---

## FW — Forward notes

Parked because the section that should hold them does not exist yet. Check this table when writing the named section.

| ID | Note | Check when writing |
|---|---|---|
| FW-01 | **Source encoding is UTF-8 without BOM, and the build must pass `/utf-8`.** Without it MSVC reads source as the active code page and emits C4819 on any non-ASCII character — a build error under this project's warnings-as-errors. Split out of 1.6.3, which covers only the repository side. | § 9 Toolchain |
| FW-02 | git-cliff's first-parent flag spelling is unverified — 2.4.2 now states the requirement rather than the flag. Confirm against the installed version. | § 2 revisit / CI work |
| FW-03 | MSVC C4458 behaviour is inferred, not tested — no MSVC available in the drafting environment. 3.20's enforcement claim rests on it. GCC `-Wshadow` and Clang `-Wshadow-all` were verified directly. | 3.20 / § 9 |
| FW-04 | Clang's plain `-Wshadow` does **not** flag constructor-parameter shadowing; `-Wshadow-all` or `-Wshadow-field-in-constructor` is required. Matters when a Clang toolchain is added. | § 9 Toolchain |
| FW-05 | Appendix D's Jira base URL is a placeholder. Set it before the first release cut or every changelog ticket link 404s. | § 2 / first release |
| FW-06 | 1.6.2's process for adding to `test_data/` is still undocumented — approval step, size limits, manifest. | § 1.6 / § 12 Testing |
| FW-07 | Appendix C's `ConstexprVariableCase` is deliberately unset: clang-tidy resolves a constexpr local against both it and `LocalConstantCase` with undocumented precedence, so 3.12 stays advisory. Revisit if upstream clarifies. | § 16 Static analysis |
| FW-08 | After committing `.gitattributes`, run `git add --renormalize .` once as its own chore commit. | on adopting 1.6.3 |

---

## X — Deferred on purpose

| ID | Item | Reason |
|---|---|---|
| X-01 | Standing up GitLab CI | Discussed and deliberately deferred. Converts most "Manual MR checklist" rows in § 7 into real gates. |
| X-02 | Docker container creation | Deferred. |
| X-03 | Dedicated Linux building and testing | Deferred. Blocks UBSan/TSan and all cross-toolchain verification. |

---

## R — Resolved, recorded so it is not re-litigated

| ID | Question | Answer |
|---|---|---|
| R-01 | Does this tool handle PHI/PII? | No. Only CUI/export-control applies. Recorded in 4.2. |
| R-02 | Which git workflow is this? | GitLab Flow with a production branch — not GitHub Flow. Corrected in § 1. |
| R-03 | Does `this->member` clear the C4458 shadowing error? | No. The diagnostic fires at the parameter declaration, not the use. Verified with GCC and Clang. Recorded in 3.20. |

---

## Reference standards

C++ Core Guidelines, Google C++ Style Guide, LLVM Coding Standards, and SEI CERT C++ are the standing cross-reference set for Code Style and Naming. Qt's own conventions get added once GUI topics are covered. MISRA C++:2023 is unresolved — see D-01.

See `References.md` for the full list with links.

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

That commit's versions of Sections 1, 3 and 6 also contain draft rules for F-26 (exception class naming), F-27 (`std::move`), F-28 (fixed-width integers), F-29 (brace initialization), F-30 (structured bindings), D-07 (stale branches) and D-08 (blank lines). Diff against the current files to extract them.

**Gone** — drafted but never committed, so no copy exists: testing (T-09, T-10) and logging (T-11). If those are wanted they get written from scratch.

Treat everything recoverable as a rough draft carrying unratified decisions, not as reviewed material.
