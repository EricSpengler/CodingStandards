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
