# C++ Coding Standards

A shared C++ standard: how code in this organization is written, reviewed, versioned, documented, and shipped. It is written to be used by more than one project — anything true of only one project lives in that project's own profile, not here.

Every rule states what to do, why, what conforming and non-conforming code looks like, and what actually enforces it. Where nothing enforces a rule but a human reading a diff, it says so plainly.

---

## Start here

New to the codebase? Read **Sections 1, 3 and 6** first — workflow, naming, code style. That is most of what you need to open your first merge request. The rest is reference.

Reviewing a merge request? **Section 7** is the enforcement map: it tells you which rules a tool would have caught and which are yours to check by eye.

Changing a value rather than a rule — a branch name, a line limit, a library? Start at **Section 0**, not at the rule.

---

## Repository layout

One file at the root — this one. Everything else is filed by what it is.

```
README.md            you are here: scope, index, how to read a rule
standards/           the standard itself: sections, appendices, references
project/             per-project values -- forked, not shared
planning/            the working tracker: open topics, decisions, findings
tools/               scripts that check the standard against itself
```

The split that matters is `standards/` versus `project/`. The standard is shared and changes rarely; the profile is rewritten by every project that adopts the standard. If you are about to add something to `standards/` that is true of only one project, it belongs in `project/` instead.

## The documents

| | Document | What it is | Rules |
|---|---|---|---|
| **0** | [Constants Registry](standards/00-constants.md) | Every value in the guide that is a choice rather than a principle, each with a permanent id and the list of rules that depend on it | — |
| **1** | [Git Workflow](standards/01-git-workflow.md) | Branching, commit format, merging, repository hygiene, the review process | 22 |
| **2** | [Versioning](standards/02-versioning.md) | Version scheme, release cadence, the release procedure, changelog generation | 4 |
| **3** | [Naming Conventions](standards/03-naming-conventions.md) | Files, namespaces, types, functions, variables, constants, macros | 20 |
| **4** | [Classification & Export Control](standards/04-classification-and-export-control.md) | The file header every tracked source file carries, and the data-sensitivity determination each project records | 2 |
| **5** | [Documentation](standards/05-documentation-doxygen.md) | Doxygen style, required tags, coverage, where documentation lives | 6 |
| **6** | [Code Style](standards/06-code-style.md) | Language feature policy, complexity limits, error handling, memory and ownership, formatting | 50 |
| **7** | [Enforcement Summary](standards/07-enforcement-summary.md) | Every hard rule mapped to what actually enforces it | — |

### Appendices — the config files the rules refer to

| | Appendix | Governs |
|---|---|---|
| **A** | [Example Doxyfile](standards/appendix-a-doxyfile.md) | Section 5 |
| **B** | [Example .clang-format](standards/appendix-b-clang-format.md) | 6.5 formatting |
| **C** | [Example .clang-tidy](standards/appendix-c-clang-tidy.md) | Section 3 naming, Section 6 style and complexity |
| **D** | [Example cliff.toml](standards/appendix-d-cliff-toml.md) | 2.4 changelog generation |
| — | [References](standards/references.md) | External standards this guide draws on, with links |

### Supporting files

| File | Purpose |
|---|---|
| [`project/PROJECT_PROFILE.md`](project/PROJECT_PROFILE.md) | **Everything specific to one project.** Source layout, commit scopes, third-party libraries, the data-sensitivity determination, product-specific release requirements. A new project forks this file and rewrites it — it does not fork the standard. |
| [`planning/Master_Topic_List.md`](planning/Master_Topic_List.md) | The working tracker: topics not yet written, decisions awaiting a human, findings against written material, and notes parked for sections that do not exist yet. If something is open, it is in here. |
| [`tools/check_constants.py`](tools/check_constants.py) | Verifies Section 0 against the rules. Exits non-zero, so it can gate a merge once CI exists. |

---

## How to read a rule

Every numbered rule uses the same five parts. Only two are always present.

| Part | Meaning |
|---|---|
| **RULE** | What to do. Always present. |
| **RATIONALE** | Why. Present wherever the reasoning is not self-evident — this is the part that lets you tell whether a rule still applies to a case it did not anticipate. |
| **GOOD** / **BAD** | Conforming and non-conforming code. `BAD` blocks always say *why* they are bad, inline. |
| **ENFORCEMENT** | What actually catches a violation. Always present. |

**Read the ENFORCEMENT line literally.** It distinguishes three very different things:

- **actual gate** — a tool rejects it. The compiler, a repository setting, `clang-format`.
- **Manual MR checklist** — tool-checkable in principle, but only actually checked because a reviewer runs it by hand during the review in 1.8. **These are not gates.**
- **Advisory — code review** — a human reading the diff, or nothing at all.

There is no CI pipeline today. That single fact is why the middle category exists and why it is so large; standing it up is the highest-value change available to this guide, and it is tracked as `X-01`.

---

## Proposing a change

A change to the standard is an ordinary merge request against this repository, following the same rules the standard describes.

- **Changing a rule** — edit the rule. If it has an entry in Section 7, update that too.
- **Changing a value** (branch name, a limit, a library) — edit its row in Section 0 first, then visit every rule its **Used in** column names. Run `python3 tools/check_constants.py` before pushing.
- **Adding a rule** — add it at the end of its section and take the next number. Numbers are never reused or reassigned, so an existing reference is never ambiguous. Section 2.5 is deliberately unused for this reason.
- **Anything unresolved** — record it in `planning/Master_Topic_List.md` rather than leaving it in a commit message. That file exists so open threads have somewhere to live.

---

## Status

Seven sections are written, holding **106 rules**. The tracker records what is not:

| | Count |
|---|---|
| Topics with no section written yet | 24 |
| Decisions awaiting a human | 9 |
| Open findings against written material | 16 |

The largest single open question is whether **MISRA C++:2023** applies contractually — it conflicts directly with the error-handling strategy in 6.3, so it would reshape Sections 6 and 7. That is `D-01`.

The guide describes itself as covering the topics it covers. Sections that do not exist are absent, not implied.
