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

*Status: this registry is complete as an inventory, but the guide's prose has not yet been rewritten to the role-name convention above. That rewrite is tracked as a separate piece of work — see the note at the foot of this file.*

---

## Scope vocabulary

| Scope | Meaning |
|---|---|
| `org` | Same across every project in the organization. Changing it is an organization-level decision, not a project one. |
| `project` | Set per project. A new project forks this guide and changes these values; the rules around them stay put. |
| `product` | Specific to one product's business requirements. **Does not belong in a general standard** — these are the removal candidates. |

Scope assignments below are a **proposal**. Rows marked ❓ are ones the drafting could not settle — they need confirming before the generalization pass runs.

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
| C-07 | Review process | 4-step manual (agent → read → build → test) | `org` ❓ | 1.8.1 |
| C-08 | Release cadence | Biweekly, day 14 of sprint | `project` ❓ | 2.2, 2.5.1 |

## Branches

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-09 | Integration branch name | `development` | `org` | 1.1.1–1.1.3, 1.2.1–1.2.3, 1.4.1, 1.4.2, 1.5.1, 1.8.1, 2.4.1 |
| C-10 | Production branch name | `release` | `org` | 1.1.1–1.1.4, 1.2.3, 1.4.2, 2.1.1, 2.2, 2.3.1, 2.4.1, 2.4.2, 2.5.1 |
| C-11 | Merge method | Fast-forward, squash per-MR | `org` | 1.2.3, 1.4.1 |
| C-12 | Stale branch thresholds | *not yet adopted — see D-07* | `org` | — |

## Commits and versioning

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-13 | Commit type vocabulary | feat, fix, style, chore, docs, refactor, test, perf, build, ci, revert | `org` | 1.2.2, 1.3.1 |
| C-14 | Commit scope vocabulary | core, gui, cmake, ci, docs, tests, build | `project` | 1.3.1 |
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
| C-27 | Supported platforms | Windows only today | `project` | 1.8.1 |

## Code layout

| ID | Constant | Current value | Scope | Used in |
|---|---|---|---|---|
| C-28 | Top-level source directories | `core`, `gui` | `project` | 3.2, 3.4, 3.11, 3.19, 5.4, 6.5.8, App. A |
| C-29 | Source file extensions | `.h` / `.cpp` | `org` | 3.3, 3.17, 3.19, 4.1 |
| C-30 | Test fixture directory | `test_data/` | `project` | 1.6.1, 1.6.2, 1.6.3 |
| C-31 | Namespace documentation file | `docs/namespaces.h` | `project` | 5.4, App. A |
| C-32 | Third-party include prefixes | Qt, hdf5, H5, vulkan, zip, zlib, duckdb, CLI, glaze, nlohmann | `project` | 6.5.8, App. B |

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
| C-43 | Default classification marking | `UNCLASSIFIED` | `org` ❓ | 3.3, 4.1, 5.4 |
| C-44 | Default export-control statement | "not subject to export control regulations" | `org` ❓ | 4.1 |
| C-45 | Export-control point of contact | *unnamed in the guide* | `project` | 4.1 |

---

## Product-scoped — the removal list

These are the values that make this a *product* document rather than a *standard*. Under the agreed generalization (option B), each is either removed, or moved to a per-project profile.

| ID | Constant | Current value | Used in | Proposed disposition |
|---|---|---|---|---|
| C-46 | Product name | CRNA PA Data Extraction & Visual Analysis | Title block, App. A `PROJECT_NAME` | Move to project profile |
| C-47 | Build expiry mechanism | Poison-pill, 21 days | 2.2, 2.5.1 (whole rule) | Remove 2.5 from the standard; it is a product release requirement, not a coding standard |
| C-48 | Data sensitivity determination | No PHI/PII; CUI/export-control only | 4.2 | Move to project profile — the *obligation to make* the determination is org-level, the *answer* is per-product |
| C-49 | Running example types | `Hdf5Reader`, `RecordBatch`, `Hdf5Error` | 35 rules across §§ 1, 3, 5, 6 | ❓ Decide: keep as-is, or replace with a domain-neutral example. This is the single largest edit in the generalization |

---

## Open questions blocking the generalization pass

1. **C-07, C-08** — is the 4-step review process and the biweekly cadence organization policy, or this project's?
2. **C-43, C-44** — is classification marking an organization-wide obligation (every project marks files) or specific to programs under export control?
3. **C-49** — the `Hdf5Reader` running example appears in 35 rules. Replacing it is mechanical but large, and a domain-neutral example (`FileReader`, `Buffer`) reads more like a textbook and less like this team's code. Worth doing, or leave it?
4. **C-14, C-28, C-32** — confirmed `project` scope? These assume `core`/`gui` and the library list differ between projects.

---

*Next step, not yet done: rewrite the guide's prose to the role-name convention described above, so that changing a value in this table requires touching only the rules its **Used in** column names. Tracked on the master topic list.*
