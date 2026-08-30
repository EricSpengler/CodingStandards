# 0. Constants Registry

Every value in this guide that is a *choice* rather than a *principle* is recorded here: branch names, the issue tracker, the compiler, numeric limits, directory names. The rules themselves state reasoning that holds regardless of these values; this file states the values.

The point is traceability. When one of these changes — a new tracker, a different column limit, a second compiler — the **Used in** column tells you exactly which rules to revisit, instead of leaving you to grep and hope.

Numbered `0` so it sorts ahead of Section 1 without disturbing any existing section number or cross-reference.

---

## How to use this file

- **Every constant has a permanent ID (`C-nn`).** IDs are never reused or renumbered, even after a constant is retired.
- **Rules refer to a constant by its role, not its value**, wherever the literal value is not what the rule is teaching — "the integration branch", "the issue tracker", "the column limit". A rule written that way survives a change to the value with no edit at all.
- **Examples and config appendices use the literal value.** An example full of placeholders is not copyable, and a `.clang-format` file cannot contain a role name. These are instantiations of the registry, and the **Used in** column is what makes them findable when a value changes.
- **Changing a constant is a normal MR** that updates this row, every rule listed in **Used in**, and nothing else.
- **Adding a constant** means adding a row here in the same MR as the rule that introduced it.
- **If a rule states a project-scoped value literally, it cites the constant id on the same line.** Stating the value is usually the more readable choice — what is not acceptable is stating it with nothing to tell a reader, or a fork of this guide, that it is a value rather than a principle. This is mechanically checked; see below.

*Status: the inventory is complete and the scope column is settled. The guide's prose has not yet been rewritten to the role-name convention above — see the generalization status section below.*

---

## Consistency check

`tools/check_constants.py` verifies this registry against the rules. Run it from the repository root; it exits non-zero on failure, so it can gate a merge once CI exists.

```bash
python3 tools/check_constants.py
```

It catches three things, all of which are otherwise silent:

1. **A "Used in" column naming a rule that no longer exists** — the usual cause is a rule being renumbered or removed without the registry being updated.
2. **A constant delegated to the project profile with no value there** — the delegation silently pointing at nothing.
3. **A project-scoped value written out in a rule without citing its constant id** — the two-sources-of-truth problem rule 5.6 prohibits for documentation. This check is what found C-14, where the commit scope list was written out in both 1.3.1 and the project profile, and C-31.

What it deliberately does *not* check is whether a stated value is *correct* — that `72 characters` in 1.3.1 still matches C-15. Doing that reliably would need a machine-readable probe per constant, which is more registry bookkeeping than the drift risk justifies. The **Used in** column is the manual answer: change a value, visit the rules it names.

## Scope vocabulary

| Scope | Meaning |
|---|---|
| `org` | Same across every project in the organization. Changing it is an organization-level decision, not a project one. |
| `project` | Set per project. A new project forks this guide and changes these values; the rules around them stay put. |
| `product` | Specific to one product's business requirements. **Does not belong in a general standard** — these are the removal candidates. |

Scope assignments below are settled. See the generalization status section at the foot of this file for what each decision changed.

---

## Organization and process

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-01 | Issue tracker | Jira | `org` | 1.2.1, 1.2.2, 1.2.3, 1.3.1, 1.3.3, 1.3.4, 1.4.1, 1.7.3, 2.1.1, 2.4.1 |
| C-02 | Ticket key format | `JIRA-XXX` | `org` | same as C-01 |
| C-03 | Repository host | GitLab | `org` | 1.1.1, 1.2.1, 1.3.1, 1.4.1, 1.4.2, 1.4.3, 1.5.1, 1.7.1, 1.7.3, 1.8.1 |
| C-04 | MR template path | `.gitlab/merge_request_templates/` | `org` | 1.7.3 |
| C-05 | Required approvals before merge | 1 | `org` | 1.7.1 |
| C-06 | MR size target | ~400 changed lines | `org` | 1.7.2 |
| C-07 | Review process | 4-step manual (agent → read → build → test) | `org` | 1.8.1 |
| C-08 | Release cadence | Biweekly, day 14 of sprint | `org` | 2.2 |

## Branches

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-09 | Integration branch name | `development` | `org` | 1.1.1–1.1.3, 1.2.1–1.2.3, 1.4.1, 1.4.2, 1.5.1, 1.8.1, 2.4.1 |
| C-10 | Production branch name | `release` | `org` | 1.1.1–1.1.4, 1.2.3, 1.4.2, 2.1.1, 2.2, 2.3.1, 2.4.1, 2.4.2, plus `PROJECT_PROFILE.md` |
| C-11 | Merge method | Fast-forward, squash per-MR | `org` | 1.2.3, 1.4.1 |
| C-12 | Stale branch thresholds | *not yet adopted — see D-07* | `org` | — |

## Commits and versioning

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-13 | Commit type vocabulary | feat, fix, style, chore, docs, refactor, test, perf, build, ci, revert | `org` | 1.2.2, 1.3.1 |
| C-14 | Commit scope vocabulary | *see project profile* | `project` | 1.3.1 |
| C-15 | Commit subject cap | 72 characters | `org` | 1.3.1 |
| C-16 | Commit body wrap | 100 characters | `org` | 1.3.1 |
| C-17 | Version scheme | `0.MINOR.PATCH`, MAJOR pinned pre-1.0 | `org` | 2.1.1 |
| C-18 | Changelog tool and config | git-cliff, `cliff.toml` | `org` | 2.4.2, App. D |
| C-19 | Changelog file | `CHANGELOG.md` | `org` | 2.4.1 |
| C-20 | Jira base URL (changelog links) | *placeholder — see FW-05* | `org` | App. D |

## Toolchain

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-21 | Language standard | C++23 | `org` | § 6 intro, 6.1.6 |
| C-22 | Compiler | MSVC | `org` | 3.20, 6.1.20 |
| C-23 | Build generator | Ninja | `org` | — (not yet written up) |
| C-24 | Build system | CMake | `org` | 1.1.3, 1.6.1 |
| C-25 | Package manager | vcpkg | `org` | 1.3.1, 1.6.1, 6.5.8 |
| C-26 | Warnings-as-errors | On | `org` | 3.20, 6.1.20 |
| C-27 | Supported platforms | *see project profile* | `project` | 1.8.1 |

## Code layout

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-28 | Top-level source directories | *see project profile* | `project` | 3.2, 3.4, 3.11, 3.19, 5.4, App. A |
| C-29 | Source file extensions | `.h` / `.cpp` | `org` | 3.3, 3.17, 3.19, 4.1 |
| C-30 | Test fixture directory | *see project profile* | `project` | 1.6.1, 1.6.2, 1.6.3 |
| C-31 | Namespace documentation file | *see project profile* | `project` | 5.4, App. A |
| C-32 | Third-party include prefixes | *see project profile* | `project` | 6.5.8, App. B |

## Style limits

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-33 | Indent width | 4 spaces, no tabs | `org` | 6.5.2, App. B |
| C-34 | Column limit | 100 | `org` | 6.5.3, App. B |
| C-35 | Brace style | Allman | `org` | 6.5.1, App. B |
| C-36 | Max function length | 60 lines | `org` | 6.2.1, App. C |
| C-37 | Complexity ceiling | 10 (see D-03 for the metric) | `org` | 6.2.2, App. C |
| C-38 | Max nesting depth | 3 | `org` | 6.2.3, App. C |
| C-39 | Max function parameters | 5 | `org` | 6.2.4, App. C |
| C-40 | Max file length | 1000 lines | `org` | 6.2.5 |

## Documentation

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-41 | Doxygen output directory | `docs/generated` | `org` | App. A |
| C-42 | Doxygen comment style | Javadoc `/** ... */` | `org` | 5.1, App. A |

## Classification and export control

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-43 | Default classification marking | `UNCLASSIFIED` | `org` | 3.3, 4.1, 5.4 |
| C-44 | Default export-control statement | "not subject to export control regulations" | `org` | 4.1 |
| C-45 | Export-control point of contact | *see project profile — still unnamed* | `project` | 4.1 |

---

## Product-scoped — the removal list

These are the values that make this a *product* document rather than a *standard*. Under the agreed generalization (option B), each is either removed, or moved to a per-project profile.

| ID | Constant | Current value | Used in | Proposed disposition |
|---|---|---|---|---|
| C-46 | Product name | *moved* | App. A `PROJECT_NAME` now a placeholder | **done** — in `PROJECT_PROFILE.md` |
| C-47 | Build expiry mechanism | *moved* | 2.5 removed; 2.2 generalized | **done** — rule text verbatim in `PROJECT_PROFILE.md`. Section number 2.5 left unused rather than reassigned |
| C-48 | Data sensitivity determination | *moved* | 4.2 rewritten | **done** — 4.2 now requires every project to record a determination; this project's answer is in `PROJECT_PROFILE.md` |
| C-49 | Running example types | `RecordReader`, `RecordBatch`, `ReadError`, `FileHandle` | §§ 1, 3, 5, 6 | **done** — domain-neutral throughout. `utf8decoder` retained in 3.1 and 3.3, which need a version-like token to demonstrate the fusion rule at all |

---

## Generalization status

The scope column is settled. The generalization pass ran on this basis:

- **C-07, C-08** — review process and release cadence are organization policy. 1.8 and 2.2 stay in the standard unchanged.
- **C-43, C-44** — classification marking is an organization-wide obligation. Section 4 stays, with 4.2 rewritten to require a *determination* rather than to state this product's answer.
- **C-49** — the running example is now domain-neutral.
- **C-46, C-47, C-48** — product-scoped values moved to `PROJECT_PROFILE.md`.

Still outstanding: the guide's prose states constant *values* inline rather than referring to them by role, so changing one still means visiting the rules its **Used in** column names rather than editing only this table. That rewrite is F-32 on the master topic list.

---

*Next step, not yet done: rewrite the guide's prose to the role-name convention described above, so that changing a value in this table requires touching only the rules its **Used in** column names. Tracked on the master topic list.*
