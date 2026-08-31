# Engineering Standards

**v0.1.0 — Draft.** Not yet ratified. The major version stays at 0 until it is; see [Versioning this document](#versioning-this-document).

How code in this organization is written, reviewed, versioned, documented, and shipped.

The standard is in two halves. **Process** applies to any language — how work is branched, committed, reviewed, versioned and marked. **Language standards** cover one language each.

It is also written to be used by more than one project: anything true of only one project lives in that project's own profile, not here.

Every rule states what to do, why, what conforming and non-conforming code looks like, and what actually enforces it. Where nothing enforces a rule but a human reading a diff, it says so plainly.

---

## Start here

**New here?** Read **P1** (git workflow), then the standard for the language you are writing — **C1** and **C3** if that is C++. Between them that is most of what you need to open your first merge request. Everything else is reference.

**Reviewing a merge request?** The **[Enforcement Summary](standards/enforcement-summary.md)** is the map: it tells you which rules a tool would already have caught and which are yours to check by eye.

**Changing a value rather than a rule** — a branch name, a line limit, a library? Start at the **[Constants Registry](standards/constants.md)**, not at the rule that mentions it.

---

## Repository layout

One file at the root — this one. Everything else is filed by what it is.

```
README.md              you are here: scope, index, how to read a rule
standards/
  process/             any language: git, versioning, file markings
  cpp/                 C++: naming, documentation, code style
                       (one folder per language -- add python/ etc. beside it)
  constants.md         every value that is a choice rather than a principle
  enforcement-summary.md   what actually gates each rule
  references.md        external standards this guide draws on
project/               per-project values -- forked, not shared
planning/              the working tracker: open topics, decisions, findings
tools/                 scripts that check the standard against itself
```

**Sections are prefixed, and the prefix is part of the number.** `P` is process; a language gets its own letter, `C` for C++ — so `P1.3.1` is a commit-message rule and `C3.1.4` is a C++ language rule, and you can tell which without looking either up. New sections append inside their own prefix, so nothing is ever renumbered, and a new language claims an unused letter.

Two splits matter. **Process versus language**: a team writing Python adopts `process/` unchanged and writes a `python/` folder — they never touch `cpp/`. **`standards/` versus `project/`**: the standard is shared and changes rarely, the profile is rewritten by every project that adopts it. If you are about to add something to the standard that is true of only one project, or of only one language, it belongs elsewhere.

## The documents

### Process — applies to any language

| | Document | What it is | Rules |
|---|---|---|---|
| **P1** | [Git Workflow](standards/process/P1-git-workflow.md) | Branching, commit format, merging, repository hygiene, the review process | 22 |
| **P2** | [Versioning](standards/process/P2-versioning.md) | Version scheme, release cadence, the release procedure, changelog generation | 4 |
| **P3** | [Classification & Markings](standards/process/P3-classification-and-markings.md) | The marking every tracked source file carries, and the data-sensitivity determination each project records | 2 |

### C++ — one language standard of potentially several

| | Document | What it is | Rules |
|---|---|---|---|
| **C1** | [Naming Conventions](standards/cpp/C1-naming-conventions.md) | Files, namespaces, types, functions, variables, constants, macros | 20 |
| **C2** | [Documentation](standards/cpp/C2-documentation-doxygen.md) | Doxygen style, required tags, coverage, where documentation lives | 6 |
| **C3** | [Code Style](standards/cpp/C3-code-style.md) | Language feature policy, complexity limits, error handling, memory and ownership, formatting | 50 |

### Across both

| Document | What it is |
|---|---|
| [Constants Registry](standards/constants.md) | Every value in the guide that is a choice rather than a principle, each with a permanent id and the rules that depend on it |
| [Enforcement Summary](standards/enforcement-summary.md) | Every hard rule mapped to what actually enforces it |
| [References](standards/references.md) | External standards this guide draws on, with links |

### Appendices — the config files the rules refer to

| | Appendix | Governs | Domain |
|---|---|---|---|
| **A** | [Example Doxyfile](standards/cpp/appendix-a-doxyfile.md) | C2 documentation | C++ |
| **B** | [Example .clang-format](standards/cpp/appendix-b-clang-format.md) | C3.5 formatting | C++ |
| **C** | [Example .clang-tidy](standards/cpp/appendix-c-clang-tidy.md) | C1 naming, C3 style and complexity | C++ |
| **D** | [Example cliff.toml](standards/process/appendix-d-cliff-toml.md) | P2.4 changelog generation | Process |

### Supporting files

| File | Purpose |
|---|---|
| [`project/PROJECT_PROFILE.md`](project/PROJECT_PROFILE.md) | **Everything specific to one project.** Source layout, commit scopes, third-party libraries, the data-sensitivity determination, product-specific release requirements. A new project forks this file and rewrites it — it does not fork the standard. |
| [`planning/Master_Topic_List.md`](planning/Master_Topic_List.md) | The working tracker: topics not yet written, decisions awaiting a human, findings against written material, and notes parked for sections that do not exist yet. If something is open, it is in here. |
| [`tools/check_constants.py`](tools/check_constants.py) | Verifies the Constants Registry against the rules. Exits non-zero, so it is usable by hand or as a merge gate. |

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

- **Changing a rule** — edit the rule. If it has an entry in the Enforcement Summary, update that too.
- **Changing a value** (branch name, a limit, a library) — edit its row in the Constants Registry first, then visit every rule its **Used in** column names. Run `python3 tools/check_constants.py` before pushing.
- **Adding a rule** — add it at the end of its section and take the next number. Numbers are never reused or reassigned, so an existing reference is never ambiguous. P2.5 is deliberately unused for this reason.
- **Adding a language** — create `standards/<language>/`, claim an unused prefix letter, and number its sections from 1 inside that prefix. Nothing in `process/` or any other language folder changes. The Enforcement Summary and Constants Registry gain rows; they are not forked.
- **Anything unresolved** — record it in `planning/Master_Topic_List.md` rather than leaving it in a commit message. That file exists so open threads have somewhere to live.

### Versioning this document

The standard versions itself the same way it tells code to version itself (P2.1.1): `0.MINOR.PATCH`, with the major version pinned at 0.

| Bump | When |
|---|---|
| **MINOR** | A rule is added, removed, or changed such that code conforming yesterday might not conform today. Also any renumbering or restructuring that changes how rules are referenced. |
| **PATCH** | Clarifications, corrected examples, rationale added to an existing rule, formatting, typos — anything that leaves the set of conforming code unchanged. |
| **MAJOR** | Reserved. It goes to 1.0 when the standard is ratified and leaves draft, and not before. |

The version lives in exactly one place, the line under the title. A merge request that changes a rule bumps it in the same commit, so "which version of the standard was in force when this was approved" is answerable from history.

---

## Status

**v0.1.0 — Draft.** Six numbered sections, holding **106 rules**, plus the Constants Registry, Enforcement Summary and References.

This standard states what it covers. It does not describe work that is not in it — open topics, pending decisions and outstanding findings are tracked in [`planning/Master_Topic_List.md`](planning/Master_Topic_List.md), which is the one place they live. A rule that is absent here is absent, not implied.
