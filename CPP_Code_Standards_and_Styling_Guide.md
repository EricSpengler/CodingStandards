# C++ Code Standards and Styling Guide

**CRNA PA Data Extraction & Visual Analysis**

*v1.0 — Draft (Git Workflow, Versioning, Naming Conventions, Classification, Documentation, Code Style)*

*Sections below are built out only as far as they've been reviewed together; everything else is intentionally not yet drafted.*

---

# 1. Git Workflow

This project uses a workflow we call GitHub Flow: development is the single required-stable integration branch (always buildable and runnable, per 1.1.3), and short-lived, PR-reviewed branches come off it and merge back into it. This is not Gitflow: there's no main/develop split where develop is allowed to be unstable, and no hotfix/* branch type, because the reason for having a hotfix escape hatch (an unstable develop that a production fix can't safely be pulled from) doesn't apply here. We extend the base workflow with a few additions of our own: a release branch that fast-forward-mirrors whatever's actually tagged/shipped, squash-merge/fast-forward-only with zero merge commits anywhere, and umbrella branches for work too large for one PR. See the separate References document for further reading.

## 1.1 Branching model

#### 1.1.1 development is the integration branch; release is a fast-forward-only mirror

**RULE**  All work branches off development and merges back into development via MR. release is never committed to directly — it only ever fast-forwards to a point already reached on development. There is no separate main/master; development is the default branch.

**RATIONALE**  Fast-forward-only means release is never anything but a snapshot of development at a point in time — no merge commits to interpret, no divergent history to reconcile. This is what makes a release tag meaningful: it points to an exact, unambiguous point in a single linear history.

**GOOD**

```cpp
git checkout release
git merge --ff-only development
git push origin release
```

**BAD**

```cpp
git checkout release
git merge development  # BAD -- creates a merge commit if release has diverged, breaking fast-forward-only
```

**ENFORCEMENT**  GitLab branch protection: release accepts fast-forward merges only, no direct pushes.

#### 1.1.2 No hotfix branches — all fixes go through development first

**RULE**  Even urgent post-release bugs are fixed via a normal branch off development, merged through the standard MR process. There is no separate hotfix/* branch type or expedited path.

**RATIONALE**  One path for how a change gets in, regardless of urgency, is one less branch type for a rotating team to learn. This only works because of the next rule.

**ENFORCEMENT**  Advisory — code review / team convention.

#### 1.1.3 development is always in a buildable, runnable “beta” state

**RULE**  Known bugs are acceptable on development. A change that would leave development unable to build or unable to run (an incomplete CMakeLists.txt, a half-wired feature that crashes on startup, etc.) must not be merged there — that work stays on its feature/umbrella branch until it is at least buildable and non-crashing, even if functionally incomplete.

**RATIONALE**  Since release is a fast-forward snapshot of development and there's no separate hotfix path, development being shippable-if-imperfect at all times is what makes “everything goes through development first” safe. It's also what makes the manual build/test review step (1.8) meaningful — a reviewer building development-plus-this-PR should always expect it to compile and run.

**ENFORCEMENT**  Manual PR checklist — the manual build/test step in 1.8 is precisely what catches this.

#### 1.1.4 Single release line

**RULE**  release is never branched into version-specific lines (release/1.x, release/2.x, etc.). It always represents the one current shippable state. There is no requirement to patch older shipped versions independently.

**RATIONALE**  Matches the team's actual need — only the latest version matters. Revisit this rule if parallel-version support ever becomes necessary; it would require rethinking the fast-forward-only policy too.

**ENFORCEMENT**  Advisory — team convention.

## 1.2 Branch naming

#### 1.2.1 Default: JIRA-XXX-kebab-desc, no type prefix

**RULE**  Most branches — anything that merges straight into development, and any sub-branch cut from an umbrella branch — are named JIRA-XXX-kebab-desc. No type prefix. The type prefix is reserved for the one exception in 1.2.2.

**RATIONALE**  This is the common case — most branches never take other branches into them, so the default should be the simple form. A fixed, mechanical pattern means branch purpose and tracking ticket are visible at a glance, with no free-form naming to interpret.

**GOOD**

```cpp
JIRA-123-hdf5-batch-reader
JIRA-456-docking-layout-crash
```

**BAD**

```cpp
JIRA-123  // missing description
my-branch  // missing ticket number
feature/JIRA-123-hdf5-batch-reader  // type prefix, but this isn't an umbrella branch
```

**ENFORCEMENT**  Advisory — code review; a server-side branch-name hook (regex) is a good candidate if/when available on the GitLab tier in use.

#### 1.2.2 Exception: umbrella branches get a type prefix

**RULE**  Only when a branch is itself an umbrella — i.e. other branches will be merged into it before it merges into development — does it get a type prefix: `<type>`/JIRA-XXX-kebab-desc, tied to the umbrella-level Jira ticket. `<type>` matches the commit type list in 1.3 (feature, fix, chore, docs, refactor, test, perf, build, ci). Sub-branches cut from that umbrella branch still follow the default in 1.2.1 (no prefix), since the umbrella branch already carries that context.

**RATIONALE**  Keeps the type prefix meaningful at exactly one level: the umbrella branch, which is the thing that eventually becomes a feat/fix/etc. commit on development. Applying it to every branch would be noise, since the vast majority of branches are never an umbrella for anything else.

**GOOD**

```cpp
feature/JIRA-123-hdf5-batch-reader  // umbrella branch, JIRA-456/JIRA-457/etc. will merge into this before it merges into development
```

**BAD**

```cpp
feature/JIRA-999-fix-typo  // BAD -- this is a single, standalone change; no type prefix needed, see 1.2.1
```

**ENFORCEMENT**  Advisory — code review.

#### 1.2.3 Sub-branches squash into the umbrella branch; the umbrella branch fast-forwards into development

**RULE**  Each sub-branch PR into the umbrella branch is squashed to one commit, following the same Conventional Commits format as a normal development merge. The umbrella branch itself is the one exception to squashing: its merge into development is a fast-forward — no squash, no merge commit — which requires the umbrella branch to be rebased onto the latest development (1.4.2) immediately before merging so the fast-forward is possible. This preserves each sub-branch's individual squashed commit exactly as it appears on the umbrella branch.

**RATIONALE**  If the umbrella branch also squashed into development, every sub-branch's Conventional Commit — type, scope, description, ticket — would collapse into a single commit by the time development's history is read. Since git-cliff (2.4.2) and the SemVer-bump derivation (2.1) both work by reading commit types from history between tags, that loss is not cosmetic: it silently produces an inaccurate changelog and can derive the wrong version bump for any release that included umbrella work. Fast-forward is the cleaner fix versus a merge commit: it avoids creating any new commit at all, consistent with how release (1.1.1) also only ever fast-forwards — same mechanism, already familiar elsewhere in this workflow.

**GOOD**

```cpp
git checkout development
git merge --ff-only feature/JIRA-123-hdf5-work   # umbrella branch, NOT squashed
git push origin development
# development now ends in: ...feat(core): add hdf5 batch reader (JIRA-456),
#                           fix(core): correct hdf5 batch reader edge case (JIRA-457)
```

**BAD**

```cpp
# BAD -- squashing the umbrella branch into development collapses this into ONE commit:
feat(core): JIRA-123 umbrella of hdf5 work
# git-cliff and the version-bump derivation (2.1) can no longer see the individual
# feat/fix entries that made up this umbrella -- changelog and version accuracy both degrade
```

**ENFORCEMENT**  GitLab project merge method is set to Fast-forward merge (see 1.4.1). For the umbrella branch's own MR into development, the squash checkbox is left OFF, so GitLab fast-forwards it as-is. Advisory — code review to confirm squash was left off for this one MR.

## 1.3 Commit messages — Conventional Commits

#### 1.3.1 Format: type(scope): description (JIRA-XXX)

**RULE**  Type is one of feat, fix, style, chore, docs, refactor, test, perf, build, ci, revert. Scope is required whenever the change is scoped to a specific part of the tree, and must be one of a fixed list — core, gui, cmake, ci, docs, tests, build — extendable only via a one-line addition to this document, never invented ad hoc. Description is imperative mood, lowercase, no trailing period. Jira ticket reference is always required, no exceptions, even for trivial changes (typo fixes, dependency bumps get a real ticket first). The subject line (the whole type(scope): description (JIRA-XXX) string) is capped at 72 characters; if the change needs more explanation, that goes in the commit body, wrapped at 100 characters per line.

**RATIONALE**  A fixed type/scope vocabulary turns commit history into a queryable log (git log --grep '^feat(core)') instead of free-text prose that means something different depending on who wrote it — and pre-1.0 versioning (Section 2) is mechanically derived directly from these types. The 72-character subject limit is adapted from the traditional 50-character git convention, widened specifically to accommodate the mandatory type(scope)/JIRA-ticket overhead this format carries that a plain free-text commit message wouldn't — a strict 50 would leave almost no room for the actual description. It also directly helps avoid GitLab's squash-message truncation (1.4.3), since a subject that never gets long in the first place can't hit the truncation threshold as easily.

**GOOD**

```cpp
feat(core): add hdf5 batch reader (JIRA-123)
fix(cmake): correct vcpkg toolchain path (JIRA-456)
style(gui): reformat dock_manager.cpp with clang-format (JIRA-789)
```

**BAD**

```cpp
Added the HDF5 reader.
fix: bug (JIRA-123)  // too vague
feat(HDF5Reader): ...  // scope not in the fixed list
feat(core): add a much longer description that blows well past the seventy-two character subject line limit (JIRA-789)  // BAD -- too long, wrap the extra detail into the body instead
```

**ENFORCEMENT**  Advisory — code review, checked as part of the four-step manual review process (1.8). No commit-message linting tool is in use today; deliberately not adopting one for now given GitLab’s squash-message truncation behavior (1.4.3) limits how much a tool like this can actually guarantee.

#### 1.3.2 WIP commits are unformatted; only the squash message conforms

**RULE**  Commits on a feature branch during active work are not required to follow Conventional Commits. The PR title (which becomes the squash commit message on merge) is the only commit message enforced.

**RATIONALE**  Enforcing format on commits nobody but the author will ever see is friction with no payoff. Enforcement effort belongs where it's actually visible in history.

**ENFORCEMENT**  Advisory — not tool-checked; the PR title is what a reviewer checks, not individual pushes to the feature branch.

#### 1.3.3 Breaking changes use ! + a BREAKING CHANGE: footer

**RULE**  A commit that breaks compatibility (API signature change, changed file format, removed CLI flag, etc.) marks the type with ! and includes a BREAKING CHANGE: footer describing what breaks and how to migrate.

**RATIONALE**  This is what makes automated version derivation possible (Section 2) — breaking-change commits are what bump the version pre-1.0 — and it makes breaking changes impossible to merge without the author consciously flagging them.

**GOOD**

```cpp
feat(core)!: change Hdf5Reader::readBatch return type (JIRA-456)

BREAKING CHANGE: readBatch now returns std::expected<RecordBatch, Hdf5Error>
instead of a raw RecordBatch. Callers must check the result before use.
```

**ENFORCEMENT**  Advisory — code review, both for footer format and for whether a change actually warrants the marker.

#### 1.3.4 Reverts follow the same convention

**RULE**  git revert's auto-generated Revert "..." message is reformatted before merge to revert: <original description> (JIRA-XXX), referencing the original ticket or a new one if the revert needs its own justification captured.

**GOOD**

```cpp
revert(core): remove hdf5 batch reader (JIRA-789)
```

**BAD**

```cpp
Revert "feat(core): add hdf5 batch reader (JIRA-456)"  // BAD -- raw git-generated message, not reformatted
```

**ENFORCEMENT**  Advisory — code review, same as all other commit-format rules; also code review for whether a fresh ticket is warranted.

## 1.4 Merging

#### 1.4.1 Merge method: fast-forward, with squash applied per-MR by default

**RULE**  The GitLab project merge method is set to Fast-forward merge — no merge commits are ever created, for any branch, full stop. Combined with the per-MR squash option (checked by default), a normal branch's PR/MR into development results in a single squashed commit fast-forwarded into place, with no merge commit. The umbrella branch's own merge into development (1.2.3) is the one case where squash is left unchecked, so its already-squashed sub-branch commits fast-forward in individually. The squash commit message follows the Conventional Commits rule (1.3.1); since the PR title should already be in that format, the default squash message needs no editing — but see 1.4.3 for a GitLab-specific caveat on this.

**GOOD**

```cpp
feat(core): add hdf5 batch reader (JIRA-123)  # single squashed commit, fast-forwarded onto development, no merge commit
```

**BAD**

```cpp
Merge branch 'JIRA-123-hdf5-batch-reader' into development  # BAD -- merge commits are never
  # created under this project's merge method; this branch should have been squashed
```

**ENFORCEMENT**  GitLab project setting: Merge method = Fast-forward merge. Per-MR squash checkbox: on by default, off only for the umbrella branch's own merge into development (1.2.3).

#### 1.4.2 Feature branches are rebased onto development, never merged from it

**RULE**  While a PR is open, if development has moved forward, the dev rebases their feature branch onto the latest development and force-pushes with --force-with-lease (never bare --force). Rebase/force-push is only ever performed on your own feature branch — never on development or release. This applies to umbrella branches too: keeping an umbrella branch rebased onto development throughout its life is what makes its eventual fast-forward merge (1.2.3) possible at all.

**RATIONALE**  Keeps feature-branch history linear and easy to review incrementally, consistent with the fast-forward merge method (1.4.1). --force-with-lease prevents silently overwriting a collaborator's pushes to the same branch — the standard failure mode of bare --force that costs someone their work with no warning.

**GOOD**

```cpp
git fetch origin && git rebase origin/development && git push --force-with-lease
```

**BAD**

```cpp
git push --force  // no lease check — can silently destroy a teammate's commits
```

**ENFORCEMENT**  GitLab branch protection prevents force-push to development/release entirely (actual gate). Advisory — code review / onboarding docs for --force-with-lease usage on feature branches.

#### 1.4.3 GitLab truncates long squash-merge messages — verify before confirming

**RULE**  This applies to normal squashed merges only (not the umbrella branch's un-squashed fast-forward, 1.2.3, which introduces no new commit message). GitLab auto-generates the squash-merge commit message from the PR's title/commits, but truncates it with a trailing “...” when it runs long. The person completing the merge must check the commit message field before confirming and, if truncated, manually retype it in full, correctly-formatted Conventional Commits form — never merge with a silently truncated message.

**RATIONALE**  A truncated commit message breaks the same things the umbrella-squash trap (1.2.3) breaks — git-cliff and the version-bump derivation (2.1) both read this text, so a silently truncated message is a real correctness bug in the changelog, not just a cosmetic one. This can't be fully solved by a pre-commit hook, since the truncation happens inside GitLab at merge time, after any local check has already passed.

**BAD**

```cpp
feat(core): add hdf5 batch reader and fix related edge cases in the be...  // BAD -- truncated, merged without checking
```

**ENFORCEMENT**  Manual PR checklist — the person merging is responsible for this check every time; no tooling catches it today.

## 1.5 Branch cleanup

#### 1.5.1 Branches auto-delete on merge

**RULE**  Repository setting deletes the source branch automatically once a PR is merged into development.

**RATIONALE**  Free cleanup, zero downside — a merged branch has already had its content absorbed via squash.

**ENFORCEMENT**  GitLab “automatically delete source branch” setting (actual gate).

## 1.6 Repository hygiene

#### 1.6.1 .gitignore follows durable principles, not a locked exhaustive list

**RULE**  Entries fall into a small set of categories — build output, package-manager artifacts, IDE-local state for both supported IDEs — and new entries are added as they come up rather than requiring this document to be revised for every one. Note that test_data/ is NOT in this list — see 1.6.2, it's committed to the repo, not ignored.

**RATIONALE**  A .gitignore that tries to be a complete, permanent list becomes stale the moment the toolchain changes. Better to state the categories that should always be excluded and let the file grow organically as new instances show up.

**GOOD**

```cpp
# build output
build/
out/
CMakeFiles/
CMakeCache.txt
cmake_install.cmake

# vcpkg
vcpkg_installed/

# IDE
.vs/
.idea/
cmake-build-*/

# local logs
*.log
```

**BAD**

```cpp
git add build/  # BAD -- build output should never be tracked
git add .vs/  # BAD -- IDE-local state, differs per developer
```

**ENFORCEMENT**  Advisory — code review. .gitignore evolves by ordinary PR, no special process.

#### 1.6.2 test_data/ is committed to the repository, with a controlled addition process

**RULE**  Test fixtures and sample data live in test_data/ and are tracked normally in git — not gitignored. Adding new files to test_data/ requires following a specific process (details TBD — open item, not yet documented here).

*Open item: the exact process for adding to test_data/ (approval step, size limits, a manifest file, etc.) still needs to be documented here once it's spelled out.*

**ENFORCEMENT**  Advisory — code review.

## 1.7 Pull request mechanics

#### 1.7.1 One required approval, any team member

**RULE**  Minimum 1 approval before merge. No CODEOWNERS restriction, no seniority requirement — any team member may approve any PR.

**ENFORCEMENT**  GitLab MR approval rule: 1 required approval, no restricted approver group (actual gate).

#### 1.7.2 PR size is soft-guided, not hard-blocked

**RULE**  Target under ~400 changed lines, excluding generated/lockfiles. PRs trending larger should be reconsidered as an umbrella-branch structure (1.2.2) rather than one large diff.

**ENFORCEMENT**  Manual PR checklist / Advisory — reviewer's judgment during manual code review.

#### 1.7.3 PR description follows a fixed template

**RULE**  What changed · Jira link · how it was tested · screenshots/recording for any UI-visible change.

**ENFORCEMENT**  GitLab MR description template file (.gitlab/merge_request_templates/).

## 1.8 Manual review process

This project does not currently run an automated CI pipeline. Every PR is verified by the approving reviewer performing four steps, in order, before approving. This section documents that process explicitly — until now it existed only as tribal knowledge, which is itself the kind of ambiguity this whole document exists to remove.

#### 1.8.1 Four-step sequence, performed by the approving reviewer

**RULE**  1) AI agent review — reviewer exports the PR's .diff and runs it through the in-house review agent (checks standards adherence, commit message format, formatting/static-analysis conformance), and posts the agent's output as an MR comment before proceeding. 2) Manual code review — reviewer reads the diff themselves, informed by (not replaced by) the agent's output. 3) Manual build — reviewer pulls the branch and builds it locally. Windows only today, since no Linux development environment exists yet; revisit once one does. 4) Manual test — reviewer runs the relevant test suite locally and confirms the PR's stated “how tested” claims. A PR is not approved until all four steps are complete, in this order.

**RATIONALE**  Without CI, every one of these checks depends entirely on a human remembering to do it, in a useful order — agent review first means the reviewer's own read of the diff isn't spent re-deriving problems a tool already caught; build and test last because they're the most expensive steps and shouldn't be run against code that's already failed static review. Posting the agent output as a comment is the only durable record that the step actually happened, useful for later auditing and for catching a reviewer who skipped it.

*This is the single biggest reliability gap in the current process — every step depends on a human doing it correctly and in order, with no gate preventing an incomplete review from approving anyway. Standing up GitLab CI is the direct fix, and was discussed and deliberately deferred rather than built now.*

**ENFORCEMENT**  Manual PR checklist — no automated gate exists today.

# 2. Versioning

Semantic Versioning, pre-1.0 convention, derived mechanically from Conventional Commit types since the last tag — removing “is this a major or minor bump” as a judgment call.

## 2.1 Version scheme

#### 2.1.1 0.MINOR.PATCH, pinned MAJOR until first stable release

**RULE**  MAJOR stays pinned at 0 until the project reaches its first stable public contract, at which point this rule is revisited and standard post-1.0 SemVer takes over (breaking → MAJOR, feat → MINOR, fix/other → PATCH). Until then: MINOR bumps on any commit since the last tag with a ! marker or BREAKING CHANGE: footer, OR any feat commit. PATCH bumps when a release contains only fix/chore/docs/refactor/test/perf/build/ci commits — no feat, no breaking changes.

**RATIONALE**  Because MAJOR is pinned at 0, breaking changes and new features both land in the same bucket (MINOR) pre-1.0 — matching the honest reality that nothing pre-1.0 has a stable contract to break yet. The ! marker still matters for changelog clarity even though it doesn't create a separate version tier yet.

**GOOD**

```cpp
Release with feat(core): add hdf5 batch reader (JIRA-101) and
fix(gui): correct docking layout bug (JIRA-102)
  -> MINOR bump: 0.4.0 -> 0.5.0

Release with only fix(cmake): correct vcpkg toolchain path (JIRA-103)
  -> PATCH bump: 0.5.0 -> 0.5.1
```

*This specific MINOR/PATCH split for the 0.y.z phase is our own addition on top of semantic versioning — pre-1.0 versions are understood to be free to change without a fixed sub-convention on their own, so we chose this split ourselves for consistency with our Conventional Commits types.*

**ENFORCEMENT**  Manual PR checklist item at release-cut time (2.3). Strong future-automation candidate once CI exists, since the bump is mechanically derivable from git log.

## 2.2 Release cadence

- Releases are cut biweekly, tied to sprint close-out (day 14 of each two-week sprint).

- If a sprint's commits warrant a version bump, that's a normal release (new tag, changelog entry, full process below). If not, see 2.5 (poison-pill reset rebuild) — a build always goes out at day 14 regardless.

## 2.3 Release-cutting

#### 2.3.1 Documented procedure, not restricted to one person

**RULE**  Any team member should be able to cut a release by following the written procedure in 2.4; it is not restricted to a specific individual by design, even though one person does it today in practice.

**RATIONALE**  A release process simple and well-documented enough that it isn't a single-person bus-factor risk is itself a goal worth stating explicitly.

**ENFORCEMENT**  Manual PR checklist / Advisory — the procedure itself is the enforcement.

## 2.4 Release process

#### 2.4.1 Full sequence

**RULE**  1) Cut a release-prep branch off development, named JIRA-XXX-desc (a Jira ticket for the release itself; no type prefix, same as any other sub-branch). 2) Pull latest development into it. 3) Generate the changelog entry for commits since the last tag using git-cliff. 4) Append the generated entry to CHANGELOG.md. 5) Commit the changelog update, following standard Conventional Commits format (e.g. chore(docs): update changelog for v0.5.0 (JIRA-XXX)). 6) Push the branch, open an MR into development. 7) Squash-merge into development — standard merge rule, no exception. 8) Tag the resulting squash commit on development as v0.MINOR.PATCH (per 2.1), push the tag. 9) Fast-forward release to that same tagged commit, push. 10) Build from the tagged commit; package for distribution.

**RATIONALE**  Tagging after the squash-merge (rather than on the pre-merge release-prep branch) means the tag always points to a commit that's actually reachable from both development and release history. Squashing creates a new commit with a different hash — tagging before the merge would leave the tag pointing to an orphaned commit neither branch's log ever shows, defeating the purpose of a release tag. This keeps the universal squash-merge rule intact with no special case carved out for releases.

**ENFORCEMENT**  Manual PR checklist / documented procedure — anyone should be able to execute this from the written steps, per 2.3.1.

#### 2.4.2 Changelog tooling: git-cliff

**RULE**  Changelog entries are generated with git-cliff, configured via a committed cliff.toml at the repo root, grouping entries by Conventional Commit type and reading directly from commit history between tags. git-cliff must NOT be run with --first-parent-only history traversal — doing so would skip the individual sub-branch commits preserved by the umbrella-branch merge exception (1.2.3) and only see the merge commit itself.

*This requirement exists specifically because of the umbrella-branch merge exception in 1.2.3 — if that rule ever changes, this one needs to be reconsidered too.*

**ENFORCEMENT**  Manual — run as part of the release process (2.4.1, step 3); cliff.toml configuration is what actually controls this.

## 2.5 Poison-pill reset rebuild

#### 2.5.1 Day-14 rebuild fallback when nothing is releasable

**RULE**  The tool has a poison-pill license mechanism: builds expire and shut down 21 days after being built, by design, to force users onto current versions during testing. Every sprint close-out (day 14, biweekly) produces a build. If the sprint's commits don't warrant a version bump per 2.1, no new tag or changelog entry is created — instead, release at its current tip is rebuilt and repackaged as-is (same source, same version tag, fresh build/package output only) purely to reset the license expiry timer.

**RATIONALE**  Anchoring the rebuild trigger to the existing sprint close-out means there's no separate calendar to watch — “did we ship a build this sprint” is already a natural checkpoint the team hits every two weeks, and a build always goes out at day 14 regardless of which case applies, so the 21-day timer never has a chance to lapse.

**ENFORCEMENT**  Manual PR checklist / sprint close-out ritual.

# 3. Naming Conventions

Every naming decision below was worked through as its own question rather than inherited wholesale from an existing style guide — several (member variable prefixing, boolean naming, local constant casing) had genuine tradeoffs worth deciding deliberately, not defaulting on.

#### 3.1 Version-like tokens fuse with the following word

**RULE**  A version-like or product-derived token (hdf5, h5, zlib, etc.) is treated as a single fused word rather than getting its own underscore-separated segment, in any snake_case or SCREAMING_SNAKE_CASE context — directory names, file names, include guards, namespaces.

**RATIONALE**  This is a general rule specifically because it was caught as an inconsistency during review — a directory/file name and its own include guard disagreeing on this point is exactly the kind of ambiguity a junior dev would copy inconsistently without a stated rule to follow.

**GOOD**

```cpp
hdf5reader.h
CORE_IO_HDF5READER_H
```

**BAD**

```cpp
hdf5_reader.h  // inconsistent with the fused form used elsewhere
CORE_IO_HDF5_READER_H
```

**ENFORCEMENT**  Advisory — code review.

#### 3.2 Directory and file names

**RULE**  Lowercase, snake_case, applying the fusion rule above. File names match the primary class they define.

**GOOD**

```cpp
core/io/hdf5reader/
hdf5reader.h
hdf5reader.cpp
```

**BAD**

```cpp
core/io/HDF5Reader/  // wrong casing
Hdf5Reader.h  // wrong casing, and doesn't match the class-name-only rule if the file held multiple classes
```

**ENFORCEMENT**  Advisory — code review.

#### 3.3 Include guards

**RULE**  SCREAMING_SNAKE_CASE, mirroring the full path exactly (including the fusion rule above), for guaranteed uniqueness across the tree.

**GOOD**

```cpp
// UNCLASSIFIED

/**
 * @file hdf5reader.h
 * @brief RAII wrapper around HDF5 file access for core.
 * @export_control This file is not subject to export control regulations.
 */

#ifndef CORE_IO_HDF5READER_H
#define CORE_IO_HDF5READER_H
// ...
#endif  // CORE_IO_HDF5READER_H
```

**BAD**

```cpp
#ifndef HDF5READER_H  // doesn't mirror the full path, not guaranteed unique
#define HDF5READER_H
// ...
#endif
```

*The classification/Doxygen header shown here (UNCLASSIFIED, @file, @brief, @export_control) is the standard file header required on every tracked .h/.cpp file — see 4.1 for the full rule.*

**ENFORCEMENT**  clang-tidy llvm-header-guard, configured to require path-based naming (Manual PR checklist — no CI today).

#### 3.4 Namespaces

**RULE**  Lowercase, snake_case, nested to mirror directory structure.

**GOOD**

```cpp
namespace core::io
{
    // ...
}
```

**BAD**

```cpp
namespace Core::IO  // wrong casing
{
    // ...
}
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (NamespaceCase: lower_case) — Manual PR checklist.

#### 3.5 Classes and structs

**RULE**  CamelCase (PascalCase), a noun or noun phrase.

**GOOD**

```cpp
class Hdf5Reader { /* ... */ };
struct RecordBatch { /* ... */ };
```

**BAD**

```cpp
class hdf5_reader { /* ... */ };  // wrong casing
struct record_batch { /* ... */ };  // wrong casing
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ClassCase/StructCase: CamelCase) — Manual PR checklist.

#### 3.6 Enum class and enum members

**RULE**  enum class always (never a plain enum). Both the enum class name and its members are CamelCase.

**GOOD**

```cpp
enum class LogLevel : uint8_t
{
    Critical = 0,
    Error,
    Warning,
    Info
};
```

**BAD**

```cpp
enum LogLevel  // BAD -- plain enum, not scoped
{
    CRITICAL = 0,  // BAD -- wrong casing for this convention
    ERROR,
    WARNING,
    INFO
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (EnumCase/EnumConstantCase: CamelCase) — Manual PR checklist.

#### 3.7 Free functions and public member functions

**RULE**  camelBack, a verb or verb phrase. No get prefix for a simple accessor (bare noun instead); set prefix is kept for setters, since it distinguishes a mutation from a query at the call site.

**GOOD**

```cpp
std::string normalizeName(const std::string& raw);

class Hdf5Reader
{
public:
    std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);
    size_t recordCount() const;          // getter, no "get" prefix
    void setRecordLimit(size_t limit);   // setter keeps "set"
};
```

**BAD**

```cpp
std::string normalize_name(const std::string& raw);  // wrong casing

class Hdf5Reader
{
public:
    size_t GetRecordCount() const;   // wrong casing, and unneeded "Get" prefix
    void RecordLimit(size_t limit);  // setter missing "set" -- reads like a getter
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (FunctionCase: camelBack) — Manual PR checklist.

#### 3.8 Local variables and function parameters

**RULE**  camelBack, descriptive, no type-encoding (no Hungarian notation), no cryptic abbreviation. Function parameters follow the exact same convention as local variables — no distinct marking to tell them apart.

**GOOD**

```cpp
int recordCount = 0;
std::string errorMessage;
void resizeBuffer(size_t newCapacity);
```

**BAD**

```cpp
int iCount = 0;  // type-encoded
std::string strErr;  // type-encoded, cryptic
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (VariableCase/ParameterCase: camelBack) — Manual PR checklist.

#### 3.9 Member variables (private/protected)

**RULE**  camelBack, no m_ prefix, no trailing underscore — same casing as a local variable. Readability comes from scope (you're inside the class), not name decoration.

**RATIONALE**  Considered and rejected the m_ / trailing-underscore alternatives deliberately: they add a small amount of visual noise to every single member access in exchange for a distinction most readers can get from context (which function/class they're already reading). This choice has a direct consequence for boolean naming — see 3.10.

**GOOD**

```cpp
class Hdf5Reader
{
private:
    hid_t fileHandle;
};
```

**BAD**

```cpp
class Hdf5Reader
{
private:
    hid_t m_fileHandle;  // BAD -- m_ prefix, rejected in favor of no decoration
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (MemberCase: camelBack) — Manual PR checklist.

#### 3.10 Boolean naming, and the member/accessor collision

**RULE**  Free functions, member functions, and local variables that are or return a boolean use an is/has/should/can prefix so they read like a question at the call site. A private member variable backing a boolean accessor does NOT carry the prefix itself — only the public accessor does.

**RATIONALE**  Under the no-prefix member convention (3.9), a member variable and a member function can't share a name in the same class — bool isOpen; and bool isOpen() const; is a compile error, not a style choice. Putting the prefix only on the accessor still delivers the actual readability payoff, since if (connection.isOpen()) at the call site is the only place this is ever read by someone outside the class.

**GOOD**

```cpp
class Connection
{
private:
    bool open;

public:
    bool isOpen() const;
};
```

**BAD**

```cpp
class Connection
{
private:
    bool isOpen;        // BAD — collides with the accessor below

public:
    bool isOpen() const;
};
```

**ENFORCEMENT**  Compiler enforces the collision itself; Advisory — code review for consistent application.

#### 3.11 Constants — class-level and namespace-level

**RULE**  UPPER_SNAKE_CASE.

**GOOD**

```cpp
namespace core::io
{
    constexpr size_t MAX_RECORD_COUNT = 100000;
}

class Hdf5Reader
{
    static constexpr size_t DEFAULT_BATCH_SIZE = 1024;
};
```

**BAD**

```cpp
namespace core::io
{
    constexpr size_t maxRecordCount = 100000;  // BAD -- wrong casing for a real constant
}
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ConstantCase: UPPER_CASE, scoped to class/namespace level) — Manual PR checklist.

#### 3.12 Constants — local (inside a function)

**RULE**  camelBack, same as a normal local variable — not UPPER_SNAKE_CASE.

**RATIONALE**  A local constant is lower-traffic and more like “a local variable that happens not to change” than a real project-wide constant. UPPER_SNAKE_CASE inside a function body tends to overstate its importance relative to everything around it.

**GOOD**

```cpp
void processRecords()
{
    constexpr size_t maxRetries = 3;
}
```

**BAD**

```cpp
void processRecords()
{
    constexpr size_t MAX_RETRIES = 3;  // BAD -- overstates a local's importance
}
```

**ENFORCEMENT**  Advisory — code review (clang-tidy's ConstantCase check does not distinguish local scope from class/namespace scope, so this specific rule isn't independently tool-enforceable without a scoped exception).

#### 3.13 Template parameters

**RULE**  CamelCase, a single descriptive word where possible.

**GOOD**

```cpp
template<typename ElementType>
class Buffer
{
    // ...
};
```

**BAD**

```cpp
template<typename t>  // BAD -- wrong casing
class Buffer
{
    // ...
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (TemplateParameterCase: CamelCase) — Manual PR checklist.

#### 3.14 Macros

**RULE**  UPPER_SNAKE_CASE, restricted to include guards only (language feature policy for macros generally is not yet covered).

**GOOD**

```cpp
#define CORE_IO_HDF5READER_H
```

**BAD**

```cpp
#define core_io_hdf5reader_h  // BAD -- wrong casing
#define MAX_RETRIES 3  // BAD -- macro used outside an include guard
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (MacroCase: UPPER_CASE) — Manual PR checklist.

#### 3.15 Static member variables

**RULE**  Same casing as a normal member variable (3.9) — camelBack, no distinct prefix (no s_) even though it's shared across all instances rather than per-instance.

**RATIONALE**  Consistent with the broader decision in 3.9 not to encode structural facts about a variable (member-ness, static-ness) into its name — the static keyword at the declaration site already says this.

**GOOD**

```cpp
class ConnectionPool
{
private:
    static int activeConnections;
};
```

**BAD**

```cpp
class ConnectionPool
{
private:
    static int s_activeConnections;  // BAD -- s_ prefix, inconsistent with 3.9
};
```

**ENFORCEMENT**  Advisory — code review.

#### 3.16 Type aliases / using declarations

**RULE**  CamelCase, same as a class — consistent with the rule that CamelCase names anything that stands in for a type, since a using alias behaves exactly like a type everywhere it's used.

**GOOD**

```cpp
using RecordId = uint64_t;
using BatchCallback = std::function<void(const RecordBatch&)>;
```

**BAD**

```cpp
using record_id_t = uint64_t;  // inconsistent with class/type casing elsewhere
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (TypeAliasCase: CamelCase) — Manual PR checklist.

#### 3.17 File extensions

**RULE**  .h / .cpp for everything, no exceptions — no .hpp for template-heavy or header-only code, no .cc in place of .cpp.

**RATIONALE**  Matches what's already used consistently throughout this document. A .hpp carve-out for templates is one more thing to remember for no real readability gain.

**GOOD**

```cpp
hdf5reader.h
hdf5reader.cpp
```

**BAD**

```cpp
hdf5reader.hpp  // BAD -- .hpp carve-out, adds a second rule to remember
hdf5reader.cc  // BAD -- inconsistent with the rest of the codebase
```

**ENFORCEMENT**  Advisory — code review.

#### 3.18 Pure interfaces: I-prefix

**RULE**  A pure interface (all-abstract base class, per 6.1.4) is named with a leading I followed by CamelCase, e.g. IReadable, IWritable. This is the one deliberate exception to this document's general avoidance of decorative naming prefixes (compare 3.9's rejection of m_ on members) — it exists specifically to make “this type is a pure interface, not a concrete class” visible at every use site, not just at the class definition.

**RATIONALE**  Unlike a member variable (where the reader is already inside the class and has full context), a pure interface is referenced constantly from far-away call sites — function signatures, template parameters, inheritance lists — where the reader has no other cue that IReadable is an interface rather than a concrete type. The prefix earns its keep here in a way it didn't for member variables.

**GOOD**

```cpp
class IReadable
{
public:
    virtual ~IReadable() = default;
    virtual std::expected<RecordBatch, Hdf5Error> read() = 0;
};
```

**BAD**

```cpp
class Readable { /* pure interface */ };  // BAD -- no I-prefix, looks like a concrete class
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ClassCase with a class-specific prefix rule for abstract classes) — Manual PR checklist.

#### 3.19 Internal-only namespaces: detail

**RULE**  Implementation-only symbols that must be shared across multiple .h/.cpp files within a module, but are not part of that module's public interface, live in a nested detail namespace (e.g. core::io::detail) rather than the module's own namespace.

**RATIONALE**  detail is the established C++ convention for this (used throughout the standard library's own implementations and Boost), so it's immediately recognizable rather than a project-specific invention. It gives implementation helpers a real home when a single .cpp's anonymous namespace (6.1) isn't enough — i.e. when the helper needs to be shared across more than one file within the module.

**GOOD**

```cpp
namespace core::io
{

namespace detail
{
    // implementation helpers, not part of core::io's public interface
}

class Hdf5Reader { /* public interface, uses detail:: helpers internally */ };

}  // namespace core::io
```

**ENFORCEMENT**  Advisory — code review.

# 4. Classification & Export Control Markings

Every tracked .h/.cpp file carries a classification header as the very first lines of the file, no exceptions.

#### 4.1 Standard header, present on every file

**RULE**  The header includes: the classification marking (UNCLASSIFIED by default), an @file tag naming the file, an @brief tag summarizing its purpose in one or two sentences, and an @export_control statement. "Not subject to export control regulations" is the safe default for the vast majority of files. If a file is ever suspected to warrant a different classification or export-control status, that determination goes to the export-control point of contact — never guessed.

**RATIONALE**  A missing or inconsistent header is the kind of thing that's invisible day-to-day and only matters the one time it's audited — making it a fixed, always-present block removes any judgment call about when it's needed.

**GOOD**

```cpp
// UNCLASSIFIED

/**
 * @file hdf5reader.h
 * @brief RAII wrapper around HDF5 file access for core.
 * @export_control This file is not subject to export control regulations.
 */
```

**BAD**

```cpp
#ifndef CORE_IO_HDF5READER_H  // BAD -- no classification header before the include guard
#define CORE_IO_HDF5READER_H
```

**ENFORCEMENT**  Advisory — code review today. A pre-commit hook or CI script checking the first 10 lines of every tracked .h/.cpp file for the marking is a strong automation candidate once available (see Section 5, known gap).

#### 4.2 Data sensitivity scope

**RULE**  This tool does not process PHI, PII, or other personally-regulated data. CUI/export-control (per 4.1) is the only sensitivity classification that applies to this codebase and the data it handles.

**RATIONALE**  Recorded explicitly so this doesn't get re-litigated or silently assumed differently later — confirmed directly with the team rather than inferred from the project name. If this ever changes (e.g. a future feature ingests personal data), it needs a dedicated data-handling topic — file-at-rest encryption, logging restrictions around sensitive fields, retention policy — none of which exists in this document today because it wasn't needed.

**ENFORCEMENT**  Advisory — revisit this determination if the tool's data sources ever change.

# 5. Documentation (Doxygen)

Documentation coverage isn't limited to the public API surface — private and protected members are documented just as thoroughly as public ones, since understanding the implementation matters for onboarding, maintenance, and code review, not just for calling into a public interface.

#### 5.1 Comment style: /** ... */ Javadoc-style, matching the file header

**RULE**  All Doxygen documentation blocks use /** ... */, consistent with the @file/@brief/@export_control header already established in Section 4. No /// triple-slash style.

**GOOD**

```cpp
/**
 * @brief Opens the given HDF5 file for reading.
 */
```

**BAD**

```cpp
/// Opens the given HDF5 file for reading.  // BAD -- wrong comment style
```

**ENFORCEMENT**  Doxygen build warns on non-conforming comment styles it can't parse as documentation; otherwise Advisory — code review.

#### 5.2 Scope: every function, variable, class, struct, and namespace — regardless of access level

**RULE**  Every free function, every member function (public, protected, AND private), every member variable, every namespace/global-scope variable or constant, every class/struct, and every namespace gets a Doxygen comment. Function-local variables are excluded (3.8/3.12 already cover their naming; they don't get Doxygen blocks).

**RATIONALE**  Documenting every access level, not just the public surface, is what makes the codebase understandable end-to-end — a private helper function is exactly the kind of thing that needs explaining, arguably more than a well-named public method whose signature already communicates most of its own intent.

**ENFORCEMENT**  Doxygen build with EXTRACT_ALL=NO, EXTRACT_PRIVATE=YES, WARN_IF_UNDOCUMENTED=YES (see Appendix A) surfaces every undocumented entity at build time. Manual PR checklist today (reviewer runs the Doxygen build during the manual build step, 1.8) — CI gate once available (Section 7, known gap).

#### 5.3 Required tags: @brief, @param, and @return on everything (@return omitted only for void); @throws when a function can throw

**RULE**  @brief is mandatory on every documented entity, even a short description for a trivial private member. @brief is written in third-person descriptive form with an implied subject of “This function/class/etc.” — e.g. “Reads the dataset” or “Opens the file,” not imperative mood (“Read the dataset,” “Open the file”). @param is mandatory for every parameter, with no exception for names that seem self-explanatory — same full-coverage principle as 5.2/5.5. @return is mandatory for every function with a non-void return type; a void function omits @return entirely, since there's no value to describe. @throws is required whenever a function can throw. Every Doxygen block spans multiple lines — opening /**, content, closing */ — never collapsed onto a single line, regardless of how short the content is.

**RATIONALE**  Requiring @brief, @param, and @return everywhere (rather than leaving them to judgment) keeps coverage total and mechanical to check, consistent with the full-coverage principle already applied in 5.2 and 5.5 — no entity is skipped because it “seemed obvious.” Void is the one genuine structural exception, not a judgment call: there's no return value to describe, so @return would either be omitted or say something meaningless. The multi-line-always rule keeps every Doxygen block visually consistent regardless of content length, so a reader scanning code doesn't have to parse two different block shapes. The verb-tense rule removes a small but real inconsistency — without it, some @brief lines read as commands and others as descriptions, which is a needless variation once a whole codebase's worth of comments are read together.

**GOOD**

```cpp
/**
 * @brief Reads one record batch from the currently open dataset.
 * @param datasetName Name of the HDF5 dataset to read.
 * @return The parsed batch, or an Hdf5Error if the read fails.
 */
std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);

/**
 * @brief Closes the currently open file handle.
 * @param force If true, closes even if pending writes have not been flushed.
 */
void close(bool force);  // void -- no @return, nothing to describe

/**
 * @brief Number of records currently buffered.
 */
size_t bufferedCount;
```

**BAD**

```cpp
/**
 * @brief Reads one record batch.  // BAD -- missing @param and @return entirely
 */
std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);

/**
 * @brief Close the currently open file handle.  // BAD -- imperative mood, should be "Closes"
 * @param force If true, closes even if pending writes have not been flushed.
 * @return None.  // BAD -- void function, nothing to document; omit @return entirely
 */
void close(bool force);
```

**ENFORCEMENT**  Doxygen WARN_IF_UNDOCUMENTED / WARN_NO_PARAMDOC catches missing @brief and @param; missing @return on a non-void function, verb tense, and single-line blocks are Advisory — code review.

#### 5.3.1 Documenting std::expected<T, E>: @return covers both outcomes, error detail lives on the enum

**RULE**  @return on a function returning std::expected<T, E> describes both the success and failure outcomes in one sentence. It does not itemize each specific error value with @retval — the meaning of each individual error (e.g. each Hdf5Error enumerator) is documented once, on the error enum's own definition, per 5.5's full-coverage requirement for enum members.

**RATIONALE**  Itemizing every error value with @retval in every function that can return it creates the same duplicate-documentation problem 5.6 already solved for declaration-vs-definition — if there are 20 functions returning Hdf5Error, that block gets copy-pasted 20 times, and updating one error's meaning means finding and fixing all 20. Keeping error-value detail on the enum itself (already mandated by 5.5) gives it exactly one home.

**GOOD**

```cpp
/**
 * @brief Reads one record batch from the currently open dataset.
 * @param datasetName Name of the HDF5 dataset to read.
 * @return The parsed batch on success, or an Hdf5Error describing why the read failed.
 */
[[nodiscard]] std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);
```

**BAD**

```cpp
/**
 * @brief Reads one record batch from the currently open dataset.
 * @param datasetName Name of the HDF5 dataset to read.
 * @return The parsed batch, or an Hdf5Error if the read fails.
 * @retval Hdf5Error::FileNotFound The dataset does not exist.        // BAD -- duplicates
 * @retval Hdf5Error::InvalidFormat The dataset format is wrong.      // documentation that
 * @retval Hdf5Error::ReadFailure A read error occurred.              // belongs on the enum
 */
[[nodiscard]] std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);
```

**ENFORCEMENT**  Advisory — code review.

#### 5.3.2 @tparam for every template parameter

**RULE**  A template class or function documents each of its template parameters with @tparam, positioned right after @brief and before @param. Coverage is total — every template parameter gets one, same full-coverage principle as everywhere else in this section.

**GOOD**

```cpp
/**
 * @brief Fixed-capacity buffer for a single element type.
 * @tparam ElementType Type of element stored in the buffer.
 */
template<typename ElementType>
class Buffer
{
    // ...
};

/**
 * @brief Clamps a value to the given inclusive range.
 * @tparam T Integral type being clamped.
 * @param value Value to clamp.
 * @param low Lower bound, inclusive.
 * @param high Upper bound, inclusive.
 * @return The clamped value.
 */
template<typename T>
requires std::integral<T>
T clamp(T value, T low, T high);
```

**BAD**

```cpp
/**
 * @brief Fixed-capacity buffer for a single element type.  // BAD -- missing @tparam for ElementType
 */
template<typename ElementType>
class Buffer
{
    // ...
};
```

**ENFORCEMENT**  Doxygen WARN_IF_UNDOCUMENTED (Manual PR checklist).

#### 5.4 Namespaces are documented once, in a dedicated doc-only header

**RULE**  Each namespace gets exactly one Doxygen block, using the @namespace command, living in a dedicated file (e.g. docs/namespaces.h) that contains nothing but namespace documentation — no actual code. Namespaces are never documented inline at the point they're opened in an ordinary header, since a namespace is typically reopened across many files and there'd be no single obvious place to put its one canonical description.

**RATIONALE**  A namespace is reopened in dozens of files; documenting it inline in “whichever header happened to be first” is exactly the kind of ambiguity this document exists to remove. A dedicated doc-only file makes it mechanical: one namespace, one block, one obvious location to look. It's still a tracked .h file, so it carries the same file header as any other (4.1).

**GOOD**

```cpp
// UNCLASSIFIED

/**
 * @file namespaces.h
 * @brief Doxygen-only namespace documentation; contains no code, never #included.
 * @export_control This file is not subject to export control regulations.
 */

/**
 * @namespace core::io
 * @brief File I/O and format-specific readers/writers (HDF5, zip) for core.
 */
```

**ENFORCEMENT**  Advisory — code review; Doxygen will warn if a namespace has no @namespace documentation anywhere in the project.

#### 5.5 Enum documentation: @brief on the enum class, and on every enumerator

**RULE**  The enum class itself gets a standard multi-line @brief block above it. Every enumerator also gets its own multi-line block above it — never an inline single-line trailing comment — with no exception for enumerators whose name might seem self-explanatory. This follows the same full-coverage requirement as 5.2 and the same multi-line-always convention as everywhere else in this document.

**RATIONALE**  Skipping enumerators whose name “seems obvious” is exactly the kind of judgment call 5.2's full-coverage rule exists to remove — what counts as obvious to the author isn't necessarily obvious to a new dev six months later, and a partially-documented enum leaves a reader unsure whether the missing docs were a deliberate choice or an oversight.

**GOOD**

```cpp
/**
 * @brief Severity level for a log entry.
 */
enum class LogLevel : uint8_t
{
    /**
     * @brief Unrecoverable; the application cannot continue.
     */
    Critical = 0,

    /**
     * @brief Recoverable, but the current operation failed.
     */
    Error,

    /**
     * @brief Non-fatal issue worth surfacing to the user or log.
     */
    Warning,

    /**
     * @brief Informational message with no actionable severity.
     */
    Info
};
```

**BAD**

```cpp
/** @brief Severity level for a log entry. */  // BAD -- single-line block
enum class LogLevel : uint8_t
{
    Critical = 0,  /**< Unrecoverable */  // BAD -- inline single-line comment
    Error,         // BAD -- undocumented
    Warning,       // BAD -- undocumented, even though the name seems obvious
    Info           // BAD -- undocumented
};
```

**ENFORCEMENT**  Doxygen WARN_IF_UNDOCUMENTED catches missing enumerator docs the same as any other entity (5.2); Advisory — code review for the multi-line formatting.

#### 5.6 Documentation lives at the declaration, not the definition

**RULE**  For anything with a separate declaration and definition (a member or free function declared in a .h and defined in the matching .cpp, an out-of-line static member, etc.), the Doxygen block goes on the declaration only. The definition carries no Doxygen block — a plain // comment there is fine if something implementation-specific needs explaining, but @brief/@param/@return/etc. are never repeated. If something is declared and defined in the same place (an inline function in a header, a function-local to one .cpp with no header declaration), the documentation goes wherever that single declaration+definition is.

**RATIONALE**  Documenting both the declaration and the definition creates two sources of truth that can silently drift out of sync as the function changes — the declaration is what a reader consults first (it's what the header/interface shows), so that's the one canonical place.

**GOOD**

```cpp
// hdf5reader.h
/**
 * @brief Reads one record batch from the currently open dataset.
 * @param datasetName Name of the HDF5 dataset to read.
 * @return The parsed batch, or an Hdf5Error if the read fails.
 */
std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);

// hdf5reader.cpp
std::expected<RecordBatch, Hdf5Error> Hdf5Reader::readBatch(const std::string& datasetName)
{
    // implementation notes, if any, as a plain comment -- no Doxygen block here
}
```

**BAD**

```cpp
// hdf5reader.cpp
/**
 * @brief Reads one record batch from the currently open dataset.  // BAD -- duplicated
 * @param datasetName Name of the HDF5 dataset to read.            // from the header,
 * @return The parsed batch, or an Hdf5Error if the read fails.    // now two sources of truth
 */
std::expected<RecordBatch, Hdf5Error> Hdf5Reader::readBatch(const std::string& datasetName)
{
    // ...
}
```

**ENFORCEMENT**  Advisory — code review.

# 6. Code Style

This project targets C++23, and follows a consistent, modern C++ style throughout — where a newer feature cleanly replaces an older idiom, this document prefers the modern one (concepts over SFINAE, for example) rather than carrying legacy patterns forward out of habit. See the separate References document for the guides this section draws from.

## 6.1 Language Feature Policy

#### 6.1.1 Smart pointers vs raw pointers — ownership

**RULE**  std::unique_ptr is the default for any owning pointer. std::shared_ptr is used only when ownership is genuinely shared across multiple independent owners. Raw pointers are always non-owning — never used to express or transfer ownership.

**RATIONALE**  A raw pointer carries no information about who is responsible for freeing it — smart pointers make that ownership question part of the type itself, removing an entire category of leak/double-free bugs.

**GOOD**

```cpp
std::unique_ptr<Hdf5Reader> reader;         // owns the Hdf5Reader
std::shared_ptr<ConnectionPool> pool;       // genuinely shared across owners
Hdf5Reader* activeReader;                   // non-owning reference only
```

**BAD**

```cpp
Hdf5Reader* reader = new Hdf5Reader(path);  // BAD -- raw owning pointer, unclear lifetime
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-owning-memory (Manual PR checklist).

#### 6.1.2 No C-style casts

**RULE**  Named casts only — static_cast, dynamic_cast, const_cast, reinterpret_cast — matching whichever conversion is actually intended.

**RATIONALE**  A C-style cast can silently perform any of static/const/reinterpret conversion without telling the reader which one — a named cast makes the intent, and the risk, visible at the call site.

**GOOD**

```cpp
auto* dog = dynamic_cast<Dog*>(animal);
auto x = static_cast<float>(count) / 2.0f;
```

**BAD**

```cpp
auto x = (float)count / 2.0f;  // BAD -- C-style cast, doesn't say which conversion is intended
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-pro-type-cstyle-cast.

#### 6.1.3 Macros

**RULE**  Banned except #ifndef include guards (naming 3.3, 3.14). No other use of the preprocessor for constants, inline-like functions, or conditional logic.

**RATIONALE**  Macros bypass the type system and scoping rules entirely, and their errors are notoriously hard to trace back to source — constexpr, templates, and inline functions cover every legitimate case a macro used to handle, with none of the downsides.

**GOOD**

```cpp
#ifndef CORE_IO_HDF5READER_H
#define CORE_IO_HDF5READER_H
```

**BAD**

```cpp
#define MAX_RETRIES 3  // BAD -- use constexpr instead
#define SQUARE(x) ((x) * (x))  // BAD -- use a function/template instead
```

**ENFORCEMENT**  Advisory — code review; a grep-based check for #define outside include guards is a good CI candidate later.

#### 6.1.4 Multiple inheritance

**RULE**  Banned except pure interfaces — all-abstract base classes where every method is pure virtual and there are no data members, named per the I-prefix convention (naming 3.18).

**RATIONALE**  Multiple inheritance from stateful classes reintroduces the classic C++ diamond-inheritance and initialization-order problems. Pure interfaces sidestep this entirely, since there's no state to conflict.

**GOOD**

```cpp
class IReadable
{
public:
    virtual ~IReadable() = default;
    virtual std::expected<RecordBatch, Hdf5Error> read() = 0;
};

class IWritable
{
public:
    virtual ~IWritable() = default;
    virtual void write(const RecordBatch& batch) = 0;
};

class Hdf5File : public IReadable, public IWritable  // ok -- both pure interfaces
{
    // ...
};
```

**BAD**

```cpp
class Hdf5File : public Hdf5Handle, public LoggingMixin  // BAD -- neither base is a
{                                                         // pure interface (both have state)
    // ...
};
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.5 friend

**RULE**  Banned by default. When used, requires a one-line justification comment directly above the friend declaration explaining why the public interface can't accomplish the same thing.

**RATIONALE**  friend is a legitimate tool (operator overloads are the classic case) but an easy shortcut to reach for when the real fix is a more complete public interface. Requiring a written justification forces the author to either produce a real reason or realize there wasn't one.

**GOOD**

```cpp
class Matrix
{
    // Justification: operator* needs private element access for performance;
    // a public accessor would allow arbitrary mutation we don't want to expose.
    friend Matrix operator*(const Matrix& a, const Matrix& b);
};
```

**BAD**

```cpp
class Matrix
{
    friend Matrix operator*(const Matrix& a, const Matrix& b);  // BAD -- no justification comment
};
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.6 Template metaprogramming: concepts over SFINAE

**RULE**  Concepts/requires (C++20) are the required way to constrain a template. SFINAE-style enable_if tricks are banned for new code.

**RATIONALE**  SFINAE exploits a compiler quirk to constrain templates and is one of the least readable corners of pre-C++20 code — a reader has to already know the trick to parse it. Concepts express the exact same constraint in plain, readable syntax, with no reason to keep writing the old form now that C++23 is the target.

**GOOD**

```cpp
template<typename T>
requires std::integral<T>
T clamp(T value, T low, T high);
```

**BAD**

```cpp
template<typename T, typename = std::enable_if_t<std::is_integral_v<T>>>
T clamp(T value, T low, T high);  // BAD -- SFINAE trick, use concepts instead
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.7 auto usage

**RULE**  Use auto when the type is obvious from the right-hand side, or would otherwise be unreadably long (iterators, lambdas). Don't use it where it hides a type the reader actually needs to see to understand the code.

**RATIONALE**  auto reduces noise exactly where the type is redundant information, but hiding a genuinely load-bearing type (one that affects overflow behavior, signedness, or an API contract) trades a small typing savings for real ambiguity.

**GOOD**

```cpp
auto reader = std::make_unique<Hdf5Reader>(path);   // type is obvious (ctor call)
auto it = records.begin();                          // iterator type is noise
```

**BAD**

```cpp
auto count = getCount();  // BAD if whether "count" is int vs size_t matters to the reader here
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.8 enum vs enum class

**RULE**  enum class always, matching naming 3.6 — listed here too since it's as much a language-feature rule as a naming one.

**GOOD**

```cpp
enum class LogLevel : uint8_t { Critical, Error, Warning, Info };
```

**BAD**

```cpp
enum LogLevel { Critical, Error, Warning, Info };  // BAD -- unscoped, implicitly converts to int
```

**ENFORCEMENT**  Advisory — code review (see naming 3.6 for the full rule).

#### 6.1.9 Range-based for vs index/iterator loops

**RULE**  Range-based for by default. An index or iterator loop is used only when the index itself is needed for something beyond element access.

**GOOD**

```cpp
for (const auto& record : records) { /* ... */ }
```

**BAD**

```cpp
for (size_t i = 0; i < records.size(); ++i) { use(records[i]); }  // BAD -- index isn't needed, prefer range-for
```

**ENFORCEMENT**  clang-tidy modernize-loop-convert (Manual PR checklist).

#### 6.1.10 Algorithms/ranges vs hand-rolled loops

**RULE**  Prefer a standard algorithm when it's at least as readable as the loop to someone unfamiliar with it, and when it avoids reimplementing something the standard library already provides correctly. Write the loop when in doubt, or when the algorithm would need a non-obvious lambda to express.

**RATIONALE**  There's no reason to hand-write logic the standard library already implements correctly and efficiently — but a clever one-liner that requires decoding a lambda isn't actually more readable than the loop it replaces, so this stays a judgment call rather than a blanket rule either way.

**GOOD**

```cpp
auto it = std::ranges::find(records, targetId, &Record::id);  // clear, and std::find already exists
```

**BAD**

```cpp
auto it = std::ranges::find_if(records, [&](const auto& r) {  // BAD -- nested lambda obscures
    return r.id() == targetId && r.status() == Status::Active;  // intent more than a loop would
});
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.11 Lambda captures: explicit only, no defaults

**RULE**  Lambda captures are always explicit — name each variable captured, by value or reference. Default captures ([=] or [&]) are never used.

**RATIONALE**  A default capture hides exactly what a lambda depends on, which is also the classic source of dangling-reference bugs when a [&]-captured lambda outlives the variables it references. Explicit captures make both the dependency and the lifetime risk visible at the point of capture.

**GOOD**

```cpp
auto callback = [&recordCount, &errorList](const Record& r) { /* ... */ };
```

**BAD**

```cpp
auto callback = [&](const Record& r) { /* ... */ };  // BAD -- default capture, unclear what's actually captured
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-avoid-capturing-lambda-coroutines catches one related case; explicit-vs-default capture style is otherwise Advisory — code review.

#### 6.1.12 const-correctness

**RULE**  Member functions that don't mutate object state are marked const. Parameters passed by reference that aren't modified are const&. Local variables that are never reassigned are const.

**RATIONALE**  const-correctness documents intent directly in the type system — a const member function is a promise the compiler enforces, not just a comment a reader has to trust.

**GOOD**

```cpp
class Hdf5Reader
{
public:
    size_t recordCount() const;                     // const member function
    void processBatch(const RecordBatch& batch);    // const& parameter
};
const size_t maxRetries = 3;                         // const local
```

**BAD**

```cpp
size_t recordCount();  // BAD -- doesn't mutate state, should be const
```

**ENFORCEMENT**  clang-tidy misc-const-correctness (Manual PR checklist).

#### 6.1.13 nullptr, never NULL or 0

**RULE**  nullptr is used for every null pointer value.

**RATIONALE**  nullptr is a real, typed null-pointer value; NULL and 0 are integer literals that happen to convert, which can cause overload-resolution ambiguity nullptr doesn't have.

**GOOD**

```cpp
Hdf5Reader* reader = nullptr;
```

**BAD**

```cpp
Hdf5Reader* reader = NULL;  // BAD
Hdf5Reader* reader = 0;     // BAD
```

**ENFORCEMENT**  clang-tidy modernize-use-nullptr.

#### 6.1.14 Explicit constructors

**RULE**  Any constructor callable with a single argument is marked explicit, unless implicit conversion is specifically and deliberately desired.

**RATIONALE**  An implicit single-argument constructor lets a raw value silently convert to the class type anywhere a function expects it — explicit forces the conversion to be written out, catching accidental type confusion at compile time.

**GOOD**

```cpp
class RecordId
{
public:
    explicit RecordId(uint64_t value);   // explicit -- prevents accidental implicit conversion
};

class Meters
{
public:
    Meters(double value);   // NOT explicit -- implicit conversion from double is intentional,
                            // e.g. so `Meters distance = 5.0;` reads naturally
};
```

**BAD**

```cpp
class RecordId { public: RecordId(uint64_t value); };  // BAD -- allows silent implicit conversion, e.g. passing a raw uint64_t where a RecordId was expected
```

**ENFORCEMENT**  clang-tidy google-explicit-constructor (Manual PR checklist).

#### 6.1.15 override and final

**RULE**  override is required on every virtual override, with no exceptions. final is used when a class or method is deliberately closed to further derivation or overriding.

**RATIONALE**  override makes the compiler verify the function actually overrides something, catching the common bug where a typo'd signature silently creates a new, unrelated function instead of overriding the intended one.

**GOOD**

```cpp
class Hdf5Writer final : public IWritable   // final -- no further derivation allowed
{
public:
    void write(const RecordBatch& batch) override;
};
```

**BAD**

```cpp
void write(const RecordBatch& batch);  // BAD -- overrides IWritable::write but doesn't say so
```

**ENFORCEMENT**  clang-tidy modernize-use-override.

#### 6.1.16 noexcept: required on move operations and swap only

**RULE**  noexcept is required on move constructors, move assignment operators, and swap — the cases where the standard library changes real behavior based on the promise (e.g. std::vector uses moves instead of copies during reallocation only if the move is noexcept). It is not required, and not applied as a matter of habit, anywhere else.

**RATIONALE**  noexcept genuinely earns its cost on move/swap because the standard library's behavior changes based on the promise; everywhere else it's only documentation, with a real downside: if a noexcept function later gains code that can throw, the program calls std::terminate() immediately instead of propagating the exception — a much harder failure to debug. Keeping the rule narrow avoids scattering that footgun through the codebase.

**GOOD**

```cpp
Buffer(Buffer&& other) noexcept;
Buffer& operator=(Buffer&& other) noexcept;
void swap(Buffer& other) noexcept;
```

**BAD**

```cpp
void processRecord(const Record& r) noexcept;  // BAD -- no real payoff here, and if this ever gains a throwing call, it becomes a std::terminate() footgun
```

**ENFORCEMENT**  clang-tidy performance-noexcept-move-constructor (Manual PR checklist).

#### 6.1.17 No trailing return types

**RULE**  Traditional return-type-first syntax is used for all functions. Trailing return type (auto foo() -> ReturnType) is not used. In the rare template case where the return type depends on a parameter declared later in the signature, prefer plain auto with the return type deduced from the function body instead of introducing a trailing return type.

**RATIONALE**  Trailing return type only exists to solve a narrow template problem that, in this codebase's style (templates fully defined inline, deduced auto available), essentially never comes up in practice — so there's no reason to introduce a second way to write a function signature.

**GOOD**

```cpp
RecordBatch readBatch(const std::string& name);
template<typename T, typename U>
auto add(T a, U b) { return a + b; }  // deduced from the body, no trailing return type needed
```

**BAD**

```cpp
auto readBatch(const std::string& name) -> RecordBatch;  // BAD -- trailing return type with no reason to need it
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.18 std::string_view for read-only string parameters

**RULE**  A function parameter that only reads a string (never stores it beyond the call, never needs a stable owned copy) takes std::string_view instead of const std::string&. A function that needs to keep the string beyond its own scope (store it in a member, pass it to another thread, etc.) still takes an owned std::string, since string_view doesn't own its data and can dangle.

**RATIONALE**  const std::string& still requires the caller to have (or construct) an actual std::string, which can force an unnecessary allocation when the caller only has a string literal or a substring view. std::string_view accepts any of those without copying, since it's just a non-owning view over existing character data — but that non-ownership is exactly why it's unsafe to store beyond the call it was passed into.

**GOOD**

```cpp
void logMessage(std::string_view message);   // read-only, used and discarded within the call

class Hdf5Reader
{
public:
    explicit Hdf5Reader(std::string path);   // BAD example below shows why this stays std::string, not string_view
private:
    std::string path_;   // stored beyond the constructor call -- needs to own the data
};
```

**BAD**

```cpp
void logMessage(const std::string& message);  // BAD -- forces a std::string to exist/allocate even when the caller only has a string literal or substring
```

**ENFORCEMENT**  clang-tidy performance-unnecessary-value-param / modernize-pass-by-value related checks flag some cases; the read-only-vs-stored distinction itself is Advisory — code review.

#### 6.1.19 Internal linkage: anonymous namespace, not static

**RULE**  A function or variable that's local to a single .cpp file (not declared in any header) is given internal linkage via an anonymous namespace, not the static keyword.

**RATIONALE**  static works for a single function or variable, but not for a type, and using two different mechanisms (static for some things, anonymous namespace for others) depending on what's being hidden is one more thing to remember. An anonymous namespace covers every case — functions, variables, and types — with one consistent mechanism.

**GOOD**

```cpp
// hdf5reader.cpp
namespace
{
    constexpr size_t kChunkSize = 4096;

    bool isRecoverable(Hdf5Error error)
    {
        return error != Hdf5Error::FileNotFound;
    }
}  // namespace
```

**BAD**

```cpp
// hdf5reader.cpp
static constexpr size_t kChunkSize = 4096;         // BAD -- static, not anonymous namespace
static bool isRecoverable(Hdf5Error error) { /* ... */ }  // BAD -- same issue
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.20 size_t/unsigned for sizes and counts; never mix signed and unsigned in one expression

**RULE**  size_t and other unsigned types remain the default for sizes, counts, and indices, matching what the standard library itself returns (container .size(), etc.) — this codebase does not require signed types for sizes/indices, given the ergonomic cost of casting at every standard-library boundary. However, signed and unsigned values are never compared or combined in arithmetic within the same expression without an explicit, deliberate cast.

**RATIONALE**  Mixing signed and unsigned in a comparison or arithmetic expression silently converts the signed value to unsigned first, which can turn a small negative number into a huge positive one — a classic, hard-to-spot C++ bug (the canonical case is a loop like for (size_t i = count - 1; i >= 0; --i), which never terminates because an unsigned i can never be negative). Requiring signed types everywhere would eliminate this entirely, but at the cost of casting constantly against a standard library that returns size_t everywhere — so this codebase takes the narrower fix (never mix the two types in one expression) rather than banning unsigned types outright.

**GOOD**

```cpp
size_t count = records.size();
if (count > 0) { /* ... */ }              // unsigned-to-unsigned, fine

int delta = -3;
if (delta < 0 && static_cast<size_t>(-delta) <= count) { /* ... */ }  // explicit cast, deliberate
```

**BAD**

```cpp
int delta = -1;
size_t count = records.size();
if (delta < count) { /* BAD -- delta is silently converted to a huge unsigned
                        number; this is false even though -1 < 5 looks obviously true */ }
```

**ENFORCEMENT**  Compiler warning (-Wsign-compare / -Wsign-conversion on GCC/Clang, /W4's C4018/C4245 on MSVC) is the real gate once warnings-as-errors is configured — that belongs to the not-yet-built Toolchain/Build Specifics topic on the master list, so this isn't wired up as an actual gate yet. Advisory — code review in the meantime.

#### 6.1.21 Pre-increment (++X), not post-increment (X++), when the returned value isn't used

**RULE**  Use pre-increment/decrement (++x, --x) rather than post-increment/decrement (x++, x--) whenever the expression's own value isn't used by the surrounding statement — loop counters and iterator advancement being the common case. Post-increment is only used when the old value is specifically what's needed.

**RATIONALE**  Post-increment has to produce a copy of the pre-increment value to return, even when nothing uses it. For a plain int the compiler trivially optimizes that copy away, but for an iterator or any type with a non-trivial copy constructor, that copy can be a real, measurable cost the optimizer doesn't always eliminate. Pre-increment is never worse and is sometimes meaningfully better, so it's the default everywhere the returned value isn't actually needed.

**GOOD**

```cpp
for (size_t i = 0; i < count; ++i) { /* ... */ }
++it;

int a = ++x;   // a gets the NEW value -- fine, the return value is actually used and needed
```

**BAD**

```cpp
for (size_t i = 0; i < count; i++) { /* ... */ }  // BAD -- return value discarded, no reason for post-increment
it++;                                              // BAD -- same issue
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.22 No using namespace — explicit namespace prefixes always

**RULE**  using namespace std; and any other using namespace X; directive are never used, in headers or .cpp files. Every identifier from another namespace is written out with its full qualification (std::string, core::io::Hdf5Reader, etc.) at every use.

**RATIONALE**  A using namespace directive in a header pollutes the namespace of every file that includes it, creating name clashes that are hard to trace back to their source. Even confined to a single .cpp file, it makes it unclear at a glance which namespace an identifier actually comes from — explicit prefixes keep that always visible at the point of use, and this codebase applies the same rule everywhere rather than relaxing it for .cpp files specifically.

**GOOD**

```cpp
std::string name;
std::vector<Record> records;
core::io::Hdf5Reader reader(path);
```

**BAD**

```cpp
using namespace std;  // BAD -- never used, in headers or .cpp files
string name;           // BAD -- relies on the banned using-namespace directive above
```

**ENFORCEMENT**  clang-tidy google-build-using-namespace (Manual PR checklist).

#### 6.1.23 Virtual destructor required on any polymorphic base class

**RULE**  Any class with at least one virtual function, and that might be deleted through a pointer to that base class, has a virtual destructor.

**RATIONALE**  Deleting a derived object through a base-class pointer with a non-virtual destructor skips the derived destructor entirely — undefined behavior, and in practice a resource leak (any RAII members the derived class owns never get cleaned up). This is directly why every pure interface in this document (6.1.4) declares its destructor virtual.

**GOOD**

```cpp
class IReadable
{
public:
    virtual ~IReadable() = default;   // virtual -- required
    virtual std::expected<RecordBatch, Hdf5Error> read() = 0;
};
```

**BAD**

```cpp
class IReadable
{
public:
    ~IReadable() = default;   // BAD -- not virtual
    virtual std::expected<RecordBatch, Hdf5Error> read() = 0;
};

std::unique_ptr<IReadable> reader = std::make_unique<Hdf5Reader>(path);
// deleting reader here only runs ~IReadable(), never ~Hdf5Reader() -- undefined behavior
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-virtual-class-destructor.

#### 6.1.24 No virtual function calls from constructors or destructors

**RULE**  A constructor or destructor never calls a virtual function on *this, directly or indirectly.

**RATIONALE**  During construction, an object's vtable isn't fully set up for its most-derived type yet — a virtual call from a base class constructor always resolves to the base class's own version, never a derived override, even when constructing a derived object. The same applies in reverse during destruction. This is one of the more surprising C++ behaviors for anyone coming from a language without this restriction, and it fails silently (no compiler error, just the wrong function running).

**BAD**

```cpp
class Base
{
public:
    Base() { init(); }   // BAD -- calls a virtual function during construction
    virtual void init() { /* ... */ }
};

class Derived : public Base
{
public:
    void init() override { /* this override is NEVER called from Base's constructor */ }
};
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.25 No object slicing — pass polymorphic types by reference or pointer, never by value

**RULE**  A polymorphic type (anything with virtual functions) is never passed, returned, or stored by value where a base-class type is used to hold a potentially-derived object. Use a reference, pointer, or smart pointer instead.

**RATIONALE**  Copying a derived object into a base-class-by-value variable or parameter only copies the base-class portion — the derived-specific data and overridden behavior are silently discarded (“sliced off”). The result still compiles and runs, just not as the derived type it was supposed to be, which makes this bug easy to miss until it produces wrong behavior far from where the actual mistake was made.

**GOOD**

```cpp
void process(const IReadable& reader);   // reference -- no slicing
void process(std::unique_ptr<IReadable> reader);   // or ownership transfer via smart pointer
```

**BAD**

```cpp
void process(IReadable reader);   // BAD -- IReadable is polymorphic; passing by value
                                   // slices away everything the derived type added

Hdf5Reader concrete(path);
process(concrete);   // only the IReadable part of concrete is copied in
```

**ENFORCEMENT**  Advisory — code review.

#### 6.1.26 Self-assignment must not corrupt the object

**RULE**  A hand-written copy assignment operator must produce a correct result when the source and target are the same object (a = a;).

**RATIONALE**  a = a; must remain a valid, safe operation. A naive assignment operator that releases its own resources before copying from the source will corrupt itself in the self-assignment case, since source and target are the same object — it ends up reading from memory it just freed. This ties directly to the Rule of Five (6.4.2): any hand-written assignment operator needs this guard.

**GOOD**

```cpp
MyType& operator=(const MyType& other)
{
    if (this == &other) return *this;   // self-assignment guard
    // ... release old resources, copy from other ...
    return *this;
}
```

**BAD**

```cpp
MyType& operator=(const MyType& other)
{
    delete data_;             // BAD -- if other is *this, this frees the data
    data_ = new int(*other.data_);  // being read from on this line -- use-after-free
    return *this;
}
```

**ENFORCEMENT**  clang-tidy bugprone-unhandled-self-assignment.

## 6.2 Complexity & Readability Limits

#### 6.2.1 Max function length: 60 lines

**RULE**  A function body, excluding braces and blank lines, does not exceed 60 lines.

**RATIONALE**  Past roughly 60 lines, a function is very likely doing more than one job and should be split — a blunt but effective signal, since almost nothing that's genuinely simple runs that long.

**ENFORCEMENT**  clang-tidy readability-function-size (LineThreshold: 60).

#### 6.2.2 Max cyclomatic complexity: 10

**RULE**  Cyclomatic complexity — the count of independent paths through a function, starting at 1 and incrementing for every if/else if/while/for/case/&&/|| — does not exceed 10 for any function.

**RATIONALE**  Cyclomatic complexity is a direct, measurable predictor of how many test cases a function needs to be thoroughly covered — a function with complexity 20 needs 20+ tests just to exercise every branch, which is exactly the kind of function that tends to hide bugs.

**GOOD**

```cpp
void processRecord(const Record& r)
{
    if (r.isValid())            // +1
    {
        if (r.hasData())        // +1
        {
            // complexity so far: 3 (1 base + 2 decisions) -- well within budget
        }
    }
}
```

**ENFORCEMENT**  clang-tidy readability-function-size (CyclomaticComplexityThreshold: 10).

#### 6.2.3 Max nesting depth: 3, use guard clauses

**RULE**  Nesting depth does not exceed 3 levels. When a function would otherwise nest deeper, restructure using early-return guard clauses for invalid/edge cases at the top of the function.

**RATIONALE**  Guard clauses handle the “get out early” cases up front and leave the main logic flat and immediately visible, instead of squeezed to the right under conditions the reader has to mentally hold open.

**GOOD**

```cpp
void processRecord(const Record& r)
{
    if (!r.isValid()) return;   // guard clause, keeps nesting shallow
    if (r.isEmpty()) return;
    // main logic, unindented
}
```

**BAD**

```cpp
void processRecord(const Record& r)
{
    if (r.isValid())
    {
        if (!r.isEmpty())
        {
            // BAD -- the actual logic is buried 2 levels deep
        }
    }
}
```

**ENFORCEMENT**  clang-tidy readability-function-size (NestingThreshold: 3).

#### 6.2.4 Max function parameters: 5, then pass a struct

**RULE**  A function takes at most 5 parameters. Beyond that, group related parameters into a struct.

**RATIONALE**  Beyond a handful of parameters, call sites become error-prone (easy to swap two same-typed arguments) and hard to read at a glance — a named struct makes each value self-documenting at the call site.

**GOOD**

```cpp
struct ReaderOptions
{
    size_t batchSize;
    bool strictMode;
    std::optional<size_t> maxRecords;
};
void configureReader(const ReaderOptions& options);
```

**BAD**

```cpp
void configureReader(size_t batchSize, bool strictMode, size_t maxRecords, bool skipInvalid, bool logErrors, size_t retryCount);  // BAD -- 6 params, easy to pass in the wrong order
```

**ENFORCEMENT**  clang-tidy readability-function-size (ParameterThreshold: 5).

#### 6.2.5 Max file length: 1000 lines (advisory)

**RULE**  A file should not exceed 1000 lines. Beyond that, split the class or namespace it contains.

**ENFORCEMENT**  Advisory — code review.

#### 6.2.6 Single responsibility: for classes and functions alike

**RULE**  A class or function should have one job. If a class name needs “and” to describe it accurately (e.g. ReaderAndValidator), or a function does multiple unrelated things (e.g. validateAndSave()), that's a signal to split it.

**RATIONALE**  A function or class doing multiple unrelated jobs adds bloat and forces every caller to accept both responsibilities even when they only need one. This is inherently a judgment call with no mechanical check — the “and” naming smell is a useful heuristic, not a hard rule.

**GOOD**

```cpp
void validate(const Record& r);
void save(const Record& r);  // called separately by whoever needs both
```

**BAD**

```cpp
void validateAndSave(const Record& r);  // BAD -- two unrelated jobs bundled into one function
```

**ENFORCEMENT**  Advisory — code review.

## 6.3 Error Handling Strategy

#### 6.3.1 Exceptions for programming errors, std::expected for recoverable failures

**RULE**  Throw an exception when a function is called with arguments that violate a documented precondition or invariant, or when the program reaches a state that should be impossible if the rest of the codebase is correct — including constructor validation for classes with invariants (6.4.5). Use std::expected<T, E> when a function's failure is a normal, anticipated outcome the caller is expected to handle explicitly — file I/O, parsing untrusted input, network calls, user-facing validation.

**RATIONALE**  Exceptions unwind the stack automatically and can't be silently ignored, which matters most exactly when the program has already reached an impossible state. std::expected keeps genuinely normal, anticipated failures visible in the type system without paying the cost of an exception for something that isn't exceptional.

**GOOD**

```cpp
class RecordBatch
{
public:
    explicit RecordBatch(size_t count)
    {
        if (count == 0)
        {
            throw std::invalid_argument("RecordBatch requires count > 0");  // programming error
        }
    }
};

std::expected<RecordBatch, ParseError> parseCsvFile(const std::filesystem::path& path);  // expected failure, see 6.3.4 for [[nodiscard]]
```

**ENFORCEMENT**  Advisory — code review.

#### 6.3.2 No error codes or bool success flags, anywhere, with no exceptions

**RULE**  First-party code never returns an int/bool status code communicated via an out-parameter or errno-style global — zero exceptions to this, including the boundary layer that wraps any third-party C-style API (for example, but not limited to, HDF5 or Vulkan). That wrapper layer's entire job is to convert the underlying library's error convention into std::expected or an exception right at the boundary, before anything else in the codebase ever sees it — the wrapper does not inherit or forward the C API's own convention.

**RATIONALE**  Boolean/int status codes are the easiest error-handling mechanism to silently ignore. Allowing them inside a wrapper “because the underlying library uses them” would just relocate the ambiguity this rule exists to remove — the conversion has to happen exactly at the boundary, not be deferred past it.

**GOOD**

```cpp
[[nodiscard]] std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);  // see 6.3.4
```

**BAD**

```cpp
bool tryReadBatch(RecordBatch& out);  // BAD -- error-code style, banned even inside a wrapper layer
```

**ENFORCEMENT**  Advisory — code review.

#### 6.3.3 assert() only for invariant checks in identified hot paths

**RULE**  assert() is permitted only for invariant checks inside identified hot paths — code that runs many times per second in a tight loop (a render loop, the inner loop of large batch processing) — and only for a condition that would otherwise be routed to an exception under 6.3.1, where paying that cost every iteration is measurably expensive. A hot path must be identified by profiling, not by feel. Everywhere else, invariant violations are exceptions, per 6.3.1, with no assert() carve-out.

**RATIONALE**  assert() is compiled out entirely in release builds, so it's genuinely free at runtime — but that also means it silently disappears in production if misused as a general validation tool. Scoping it strictly to profiling-justified hot paths keeps it from becoming a way to skip real error handling anywhere a dev feels like it's “just a debug check.”

**GOOD**

```cpp
// Hot path, identified by profiling: called per-vertex in the render loop.
void transformVertex(Vertex& v, const Matrix& m)
{
    assert(m.isValid() && "transform matrix must be valid");
    // ...
}
```

**BAD**

```cpp
void setBatchSize(size_t size)  // BAD -- not a hot path, should throw per 6.3.1
{
    assert(size > 0 && "batch size must be positive");
}
```

**ENFORCEMENT**  Advisory — code review; reviewer should ask for the profiling justification when assert() appears.

#### 6.3.4 [[nodiscard]] on every function returning std::expected

**RULE**  Every function that returns std::expected<T, E> is marked [[nodiscard]], with no exceptions.

**RATIONALE**  Without [[nodiscard]], nothing stops a caller from invoking the function and discarding the returned std::expected entirely — silently ignoring a possible failure with no compiler warning. This directly undermines the whole point of 6.3.1's split: std::expected only keeps failures visible in the type system if something actually forces the caller to look at the return value.

**GOOD**

```cpp
[[nodiscard]] std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);
```

**BAD**

```cpp
std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);  // BAD -- missing [[nodiscard]], caller can silently drop the error
```

**ENFORCEMENT**  Compiler warning (real gate, [[nodiscard]] is a language feature enforced by every compiler) once applied; Advisory — code review to confirm it's applied everywhere it should be.

## 6.4 Memory Management & Ownership

#### 6.4.1 No manual memory management

**RULE**  new, delete, malloc, and free never appear in first-party code. Use stack-allocated variables and RAII wrappers (smart pointers, containers) exclusively.

**RATIONALE**  It's easy to forget a delete on an early-return or exception path; it's impossible to forget to release a stack-owned resource.

**GOOD**

```cpp
auto reader = std::make_unique<Hdf5Reader>(path);
```

**BAD**

```cpp
Hdf5Reader* reader = new Hdf5Reader(path);  // BAD
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-no-malloc, cppcoreguidelines-owning-memory.

#### 6.4.2 Rule of five, explicit

**RULE**  If a class declares a custom destructor, it must also explicitly declare (or explicitly = default / = delete) the copy constructor, copy assignment, move constructor, and move assignment operators.

**RATIONALE**  The compiler-generated copy/move operations are frequently wrong once a custom destructor exists — leaving them implicit is a latent double-free or slicing bug waiting for someone to trigger it.

**GOOD**

```cpp
class Hdf5Reader
{
public:
    ~Hdf5Reader();
    Hdf5Reader(const Hdf5Reader&) = delete;
    Hdf5Reader& operator=(const Hdf5Reader&) = delete;
    Hdf5Reader(Hdf5Reader&&) noexcept;
    Hdf5Reader& operator=(Hdf5Reader&&) noexcept;
};
```

**BAD**

```cpp
class Hdf5Reader { public: ~Hdf5Reader(); };  // BAD -- compiler-generated copy/move left implicit, likely wrong once the class owns a resource
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-special-member-functions.

#### 6.4.3 Passing ownership: unique_ptr by value; non-owning by pointer or reference

**RULE**  Ownership is transferred by passing a std::unique_ptr by value. Non-owning access is expressed with a raw pointer or reference — never a raw owning pointer.

**RATIONALE**  A raw pointer parameter is ambiguous about ownership transfer; std::unique_ptr by value makes the transfer explicit and compiler-checked (the caller can't accidentally keep using it afterward).

**GOOD**

```cpp
void takeOwnership(std::unique_ptr<Hdf5Reader> reader);
void useReader(const Hdf5Reader& reader);
```

**BAD**

```cpp
void takeOwnership(Hdf5Reader* reader);  // BAD -- unclear whether this takes ownership or just uses it
```

**ENFORCEMENT**  Advisory — code review.

#### 6.4.4 RAII for every resource, not just heap memory

**RULE**  Every resource that must be explicitly acquired and released — file handles, locks, network/database connections, handles from a wrapped C API — is wrapped in an RAII type whose constructor acquires it and whose destructor releases it. Nothing is manually released.

**RATIONALE**  Manual acquire/release pairs are exactly as fragile as manual new/delete (6.4.1), just for a different kind of resource — an exception or early return between acquire and release leaves the resource held forever. RAII guarantees the release runs via the destructor, regardless of how the scope is exited.

**GOOD**

```cpp
{
    std::lock_guard<std::mutex> lock(mutex_);   // constructor locks
    doSomething();                               // if this throws...
}                                                 // ...destructor still runs, unlocking automatically
```

**BAD**

```cpp
mutex_.lock();
doSomething();       // BAD -- if this throws or returns early, unlock() never runs
mutex_.unlock();
```

**ENFORCEMENT**  Advisory — code review.

#### 6.4.5 struct vs class: presence of any function beyond data

**RULE**  struct is for a pure container of variables — no member functions beyond perhaps an aggregate initializer. The moment a type has any member function, it's a class.

**RATIONALE**  This is a deliberately simpler, mechanically-checkable version of the more common “struct for no-invariant data, class when an invariant must be protected” rule — every invariant-protecting type necessarily has a constructor with logic, so this rule is a safe subset of that reasoning: it can never misclassify a type that needs protecting as a struct, it only occasionally classifies a function-only, no-invariant type (e.g. a Point with a distanceFromOrigin() query method) as a class when it strictly didn't need to be, which is a safe direction to err in.

**GOOD**

```cpp
struct RecordBatch       // pure data, no functions
{
    std::vector<Record> records;
    size_t batchId;
};

class Hdf5Reader          // has functions (and an invariant the constructor protects)
{
    // ...
};
```

**ENFORCEMENT**  Advisory — code review.

## 6.5 Formatting

#### 6.5.1 Brace style: Allman

**RULE**  Opening braces go on their own new line, for every block — functions, control statements, classes.

**GOOD**

```cpp
void readBatch()
{
    if (isValid)
    {
        // ...
    }
}
```

**BAD**

```cpp
void readBatch() {  // BAD -- K&R style, not Allman
    if (isValid) {
    }
}
```

**ENFORCEMENT**  clang-format (BreakBeforeBraces: Allman).

#### 6.5.2 Indentation: 4 spaces, never tabs

**RULE**  4 spaces per indentation level. Tabs are never committed.

**ENFORCEMENT**  clang-format (IndentWidth: 4, UseTab: Never).

#### 6.5.3 Column limit: 100

**RULE**  Lines wrap at 100 columns.

**ENFORCEMENT**  clang-format (ColumnLimit: 100).

#### 6.5.4 Pointer/reference alignment: left

**RULE**  The * or & binds to the type, not the variable name.

**GOOD**

```cpp
int* pointer;
const std::string& name;
```

**BAD**

```cpp
int *pointer;  // BAD
```

**ENFORCEMENT**  clang-format (PointerAlignment: Left).

#### 6.5.5 Access modifiers: flush with the class keyword, no indent

**RULE**  public:/private:/protected: are flush with the class declaration's indentation — not indented an extra level.

**RATIONALE**  Access modifiers act more like section dividers within the class than genuine nested scope — keeping them flush avoids an extra visual nesting level for no real benefit, consistent with this document's general preference for flat, low-nesting code (6.2.3).

**GOOD**

```cpp
class Hdf5Reader
{
public:
    void readBatch();
private:
    hid_t fileHandle;
};
```

**BAD**

```cpp
class Hdf5Reader
{
    public:  // BAD -- indented, adds a nesting level with no readability payoff
        void readBatch();
};
```

**ENFORCEMENT**  clang-format (AccessModifierOffset: -4, IndentAccessModifiers: false).

#### 6.5.6 Space before parens in control statements

**RULE**  A space always separates a control keyword from its parenthesis: if (x), never if(x).

**GOOD**

```cpp
if (isValid) { /* ... */ }
```

**BAD**

```cpp
if(isValid) { }  // BAD
```

**ENFORCEMENT**  clang-format (SpaceBeforeParens: ControlStatements).

#### 6.5.7 Single-line function bodies: trivial getters/setters only

**RULE**  Only a trivial inline getter/setter may collapse to one line. Every other function body spans multiple lines regardless of how short its content is — the same multi-line-always principle already applied to Doxygen blocks (5.3).

**GOOD**

```cpp
size_t recordCount() const { return count_; }  // ok -- trivial getter
```

**BAD**

```cpp
bool isValid() const { if (!ptr) return false; return ptr->check(); }  // BAD -- not trivial, must be multi-line
```

**ENFORCEMENT**  clang-format (AllowShortFunctionsOnASingleLine: InlineOnly); Advisory — code review for the “trivial” judgment call.

#### 6.5.8 Include order: own header, first-party, third-party, C system + standard library

**RULE**  A .cpp file's #includes are grouped and ordered: (1) the matching header for this file (e.g. hdf5reader.cpp includes hdf5reader.h first), (2) this project's other first-party headers, (3) third-party library headers (Qt, HDF5, vcpkg-installed libraries), (4) C system headers and C++ standard library headers, combined into one group. Each group is separated by a blank line and alphabetized within itself.

**RATIONALE**  Putting the file's own matching header first is what actually proves that header is self-contained — if hdf5reader.h secretly depends on something included earlier in hdf5reader.cpp, including it first is what makes that compile failure show up immediately, rather than being masked by whatever happened to be included before it. The remaining three groups reflect this codebase's existing convention (own header, first-party, third-party, then system/stdlib combined), rather than importing a different split from elsewhere.

**GOOD**

```cpp
// hdf5reader.cpp
#include "hdf5reader.h"                     // 1: own header first

#include "core/io/record_batch.h"           // 2: first-party (alphabetical)
#include "gui/docking/dock_manager.h"

#include <hdf5.h>                            // 3: third-party (alphabetical)
#include <QString>

#include <optional>                          // 4: C system + standard library, combined (alphabetical)
#include <string>
#include <unistd.h>
```

**BAD**

```cpp
// hdf5reader.cpp
#include <string>                            // BAD -- own header should come first, not stdlib
#include "hdf5reader.h"
#include <hdf5.h>                            // BAD -- third-party before first-party
#include "core/io/record_batch.h"
```

**ENFORCEMENT**  clang-format (IncludeBlocks: Regroup, IncludeCategories — see Appendix B).

#### 6.5.9 Member order: public/protected/private, then types → constants → factory functions → constructors → assignment operators → destructor → other methods → data members

**RULE**  A class's access-level blocks appear in the order public, then protected, then private — each access level as one contiguous block, never scattered (e.g. two separate public: sections with something else between them). Within each access-level block, declarations follow this order: types (nested typedefs/using/structs/classes), constants, factory functions, constructors, assignment operators, destructor, all other methods, data members. Within any one of those 8 groups — e.g. among the “other methods” — declarations are NOT required to be alphabetical; group related declarations together instead. For data members specifically, declaration order follows initialization dependencies, not alphabetical order or grouping — C++ always initializes members in declaration order regardless of constructor initializer-list order, so a member that depends on another member already being initialized must be declared after it.

**RATIONALE**  A conventional, predictable member order means a reader always knows roughly where to look for a constructor vs. a data member, without having to scan the whole class first.

**GOOD**

```cpp
class Hdf5Reader
{
public:
    using RecordCallback = std::function<void(const RecordBatch&)>;   // 1: types

    static constexpr size_t DEFAULT_BATCH_SIZE = 1024;                // 2: constants

    static Hdf5Reader open(const std::filesystem::path& path);        // 3: factory function

    explicit Hdf5Reader(const std::filesystem::path& path);           // 4: constructors
    Hdf5Reader(Hdf5Reader&&) noexcept;
    Hdf5Reader& operator=(Hdf5Reader&&) noexcept;                     // 5: assignment operators
    ~Hdf5Reader();                                                     // 6: destructor

    std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);  // 7: other methods
    size_t recordCount() const;

private:
    hid_t fileHandle;                                                  // 8: data members
};
```

**BAD**

```cpp
class Hdf5Reader
{
public:
    hid_t fileHandle;                    // BAD -- data member before constructors/methods
    explicit Hdf5Reader(const std::filesystem::path& path);
private:
    void logError(const std::string& msg);
public:                                  // BAD -- a second public: block, scattered from the first
    size_t recordCount() const;
};
```

**ENFORCEMENT**  Advisory — code review; a custom clang-tidy check could enforce ordering later if this becomes a recurring review comment.

# 7. Enforcement Summary

A quick-reference map of every hard rule above to what actually enforces it. Anything not listed here is Advisory — code review by default. This covers the Git Workflow, Versioning, Naming Conventions, Classification Markings, Documentation, and Code Style sections — CMake structure and the remaining topics on the master list have not been built out yet.

*Important: this project has no automated CI pipeline today. Rows marked “Manual PR checklist” are tool-checkable in principle but are only actually verified because the reviewer runs them by hand during the four-step review process (1.8) — they are not a hard gate the way a CI-enforced row would be. Standing up GitLab CI would convert most of these into real gates; this was discussed and deliberately deferred rather than built now.*

| Rule | Section | Enforcement |
| --- | --- | --- |
| Conventional Commit format, branch naming | 1.2, 1.3 | Advisory — code review only; no linting tool adopted (see 1.3.1 note) |
| Merge method (fast-forward, squash per-MR by default) | 1.4 | GitLab project setting (Fast-forward merge) + per-MR squash checkbox (actual gate) |
| GitLab squash-message truncation — manual verification | 1.4.3 | Manual PR checklist — no tooling catches this today |
| Fast-forward-only release, no direct push to development/release | 1.1, 1.4 | GitLab branch protection rules (actual gate) |
| 1 approval minimum before merge | 1.7 | GitLab MR approval rule (actual gate) |
| Branch auto-delete on merge | 1.5 | GitLab repo setting (actual gate) |
| Four-step manual review (agent → review → build → test) | 1.8 | Manual PR checklist — no automated gate exists |
| Version bump derived from commit types | 2.1 | Manual PR checklist at release-cut time |
| Release process sequence, tag-after-merge | 2.4 | Documented procedure, not tool-enforced |
| Poison-pill reset rebuild trigger (day 14) | 2.5 | Manual — sprint close-out ritual |
| Include guard naming (path-based, fused tokens) | 3.3 | clang-tidy llvm-header-guard (Manual PR checklist) |
| Namespace/class/struct/enum/function/variable/member/parameter/template/macro casing | 3.4–3.9, 3.13–3.14 | clang-tidy readability-identifier-naming (Manual PR checklist) |
| Boolean member/accessor naming (no collision) | 3.10 | Compiler-enforced (real gate) + Advisory for consistent application |
| Class/namespace-level constant casing | 3.11 | clang-tidy readability-identifier-naming (Manual PR checklist) |
| Type alias casing | 3.16 | clang-tidy readability-identifier-naming (Manual PR checklist) |
| Classification header present | 4.1 | Advisory — code review (no automated scan today) |
| Doxygen coverage (every entity, all access levels) | 5.2 | Doxygen build (WARN_IF_UNDOCUMENTED) — Manual PR checklist today |
| Doxygen @brief present | 5.3 | Doxygen build (WARN_IF_UNDOCUMENTED) — Manual PR checklist today |
| @tparam on every template parameter | 5.3.2 | Doxygen build (WARN_IF_UNDOCUMENTED) — Manual PR checklist today |
| No owning raw pointers | 6.1.1, 6.4.1 | clang-tidy cppcoreguidelines-owning-memory (Manual PR checklist) |
| No C-style casts | 6.1.2 | clang-tidy cppcoreguidelines-pro-type-cstyle-cast (Manual PR checklist) |
| Range-based for preferred | 6.1.9 | clang-tidy modernize-loop-convert (Manual PR checklist) |
| const-correctness | 6.1.12 | clang-tidy misc-const-correctness (Manual PR checklist) |
| nullptr, not NULL/0 | 6.1.13 | clang-tidy modernize-use-nullptr (Manual PR checklist) |
| Explicit single-arg constructors | 6.1.14 | clang-tidy google-explicit-constructor (Manual PR checklist) |
| override required on virtual overrides | 6.1.15 | clang-tidy modernize-use-override (Manual PR checklist) |
| noexcept on move ops/swap | 6.1.16 | clang-tidy performance-noexcept-move-constructor (Manual PR checklist) |
| Function length ≤ 60 lines | 6.2.1 | clang-tidy readability-function-size (Manual PR checklist) |
| Cyclomatic complexity ≤ 10 | 6.2.2 | clang-tidy readability-function-size (Manual PR checklist) |
| Nesting depth ≤ 3 | 6.2.3 | clang-tidy readability-function-size (Manual PR checklist) |
| Parameter count ≤ 5 | 6.2.4 | clang-tidy readability-function-size (Manual PR checklist) |
| No manual new/delete/malloc/free | 6.4.1 | clang-tidy cppcoreguidelines-no-malloc (Manual PR checklist) |
| Rule of five | 6.4.2 | clang-tidy cppcoreguidelines-special-member-functions (Manual PR checklist) |
| Formatting (braces, spacing, pointer alignment, column limit) | 6.5 | clang-format (IDE integration + AI agent review, 1.8) |
| No using namespace directives | 6.1.22 | clang-tidy google-build-using-namespace (Manual PR checklist) |
| Virtual destructor on polymorphic base classes | 6.1.23 | clang-tidy cppcoreguidelines-virtual-class-destructor (Manual PR checklist) |
| Self-assignment safety | 6.1.26 | clang-tidy bugprone-unhandled-self-assignment (Manual PR checklist) |
| Include order | 6.5.8 | clang-format IncludeCategories (see Appendix B) |
| [[nodiscard]] on std::expected-returning functions | 6.3.4 | Compiler warning (actual gate, once applied) + Advisory for coverage |
| Pure interface I-prefix | 3.18 | Advisory — code review |
| Commit subject line ≤ 72 chars | 1.3.1 | Advisory — code review (no linting tool, see 1.3.1 note) |
| Class member order (access level + intra-block) | 6.5.9 | Advisory — code review |

**Known gap: standing up GitLab CI to run builds, warnings-as-errors, and clang-format/clang-tidy (including the identifier-naming checks above) automatically — once those sections are built out — would convert most “Manual PR checklist” rows above into real gates. Commit-message linting was considered and deliberately not adopted for now (see 1.3.1) given GitLab's squash-message truncation behavior (1.4.3) limits what it can actually guarantee. Revisit both as a standalone initiative.**

---

# Appendix A: Example Doxyfile

```cpp
PROJECT_NAME           = "CRNA PA Data Extraction & Visual Analysis"
OUTPUT_DIRECTORY       = docs/generated
INPUT                  = core gui docs/namespaces.h
RECURSIVE              = YES

# Comment style: explicit /** @brief ... */ everywhere (5.1) -- don't infer
# a brief from the first sentence of an undecorated comment block.
JAVADOC_AUTOBRIEF      = NO

# Full-codebase documentation coverage (5.2) -- extract and warn on private/protected members too, not just public.
EXTRACT_ALL            = NO
EXTRACT_PRIVATE        = YES
EXTRACT_PRIV_VIRTUAL   = YES
EXTRACT_STATIC         = YES
EXTRACT_LOCAL_CLASSES  = YES

# Surface every undocumented entity as a warning (5.2, 5.3).
WARN_IF_UNDOCUMENTED   = YES
WARN_IF_INCOMPLETE_DOC = YES
WARN_NO_PARAMDOC       = YES  # 5.3: every parameter requires @param, no exceptions

GENERATE_HTML          = YES
GENERATE_LATEX         = NO
GENERATE_XML           = NO
```

---

# Appendix B: Example .clang-format

```cpp
BasedOnStyle: LLVM
Language: Cpp

# 6.5.2, 6.5.3
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 100

# 6.5.1
BreakBeforeBraces: Allman

# 6.5.4
PointerAlignment: Left
DerivePointerAlignment: false

# 6.5.5
AccessModifierOffset: -4
IndentAccessModifiers: false

# 6.5.6
SpaceBeforeParens: ControlStatements

# 6.5.7
AllowShortFunctionsOnASingleLine: InlineOnly
AllowShortIfStatementsOnASingleLine: false

# 6.5.8 -- include order: own header, first-party, third-party, C system + stdlib combined
IncludeBlocks: Regroup
SortIncludes: true
IncludeIsMainRegex: '(Test)?$'   # default -- own header auto-detected as Priority 0,
                                 # matched by base filename against the .cpp, not by the regexes below
IncludeCategories:
  - Regex:           '^<(Q[A-Za-z0-9]+|hdf5|H5[A-Za-z]*|vulkan|zip|zlib|duckdb|CLI|glaze|nlohmann)'  # 2: third-party
    Priority:        2
  - Regex:           '^<.*>$'               # 3: everything else in angle brackets --
    Priority:        3                      #    C system + C++ standard library, combined
  - Regex:           '^".*"$'               # 1: first-party (any quoted include that isn't the main header)
    Priority:        1
```
