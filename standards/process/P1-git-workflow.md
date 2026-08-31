# P1. Git Workflow

This project uses GitLab Flow with a production branch: development is the single required-stable integration branch (always buildable and runnable, per P1.1.3), short-lived, MR-reviewed branches come off it and merge back into it, and release is the production branch that trails development. This is not Gitflow: there's no main/develop split where develop is allowed to be unstable, and no hotfix/* branch type, because the reason for having a hotfix escape hatch (an unstable develop that a production fix can't safely be pulled from) doesn't apply here. It is also not GitHub Flow, which this document previously called it — GitHub Flow has exactly one long-lived branch and deploys from it, whereas the release branch below is a second long-lived branch, which is precisely the distinction GitLab Flow's production-branch variant describes. We extend that base with a few additions of our own: release only ever fast-forward-mirrors whatever's actually tagged/shipped, squash-merge/fast-forward-only with zero merge commits anywhere, and umbrella branches for work too large for one MR. See the separate References document for further reading.

## P1.1 Branching model

### P1.1.1 development is the integration branch; release is a fast-forward-only mirror

**RULE**  All work branches off development and merges back into development via MR. release is never committed to directly — it only ever fast-forwards to a point already reached on development. There is no separate main/master; development is the default branch.

**RATIONALE**  Fast-forward-only means release is never anything but a snapshot of development at a point in time — no merge commits to interpret, no divergent history to reconcile. This is what makes a release tag meaningful: it points to an exact, unambiguous point in a single linear history.

**GOOD**

```bash
git checkout release
git merge --ff-only development
git push origin release
```

**BAD**

```bash
git checkout release
git merge development  # BAD -- creates a merge commit if release has diverged, breaking fast-forward-only
```

**ENFORCEMENT**  GitLab branch protection: release accepts fast-forward merges only, no direct pushes.

### P1.1.2 No hotfix branches — all fixes go through development first

**RULE**  Even urgent post-release bugs are fixed via a normal branch off development, merged through the standard MR process. There is no separate hotfix/* branch type or expedited path.

**RATIONALE**  One path for how a change gets in, regardless of urgency, is one less branch type for a rotating team to learn. This only works because of the next rule.

**ENFORCEMENT**  Advisory — code review / team convention.

### P1.1.3 development is always in a buildable, runnable “beta” state

**RULE**  Known bugs are acceptable on development. A change that would leave development unable to build or unable to run (an incomplete CMakeLists.txt, a half-wired feature that crashes on startup, etc.) must not be merged there — that work stays on its feature/umbrella branch until it is at least buildable and non-crashing, even if functionally incomplete.

**RATIONALE**  Since release is a fast-forward snapshot of development and there's no separate hotfix path, development being shippable-if-imperfect at all times is what makes “everything goes through development first” safe. It's also what makes the manual build/test review step (P1.8) meaningful — a reviewer building development-plus-this-MR should always expect it to compile and run.

**ENFORCEMENT**  Manual MR checklist — the manual build/test step in P1.8 is precisely what catches this.

### P1.1.4 Single release line

**RULE**  release is never branched into version-specific lines (release/1.x, release/2.x, etc.). It always represents the one current shippable state. There is no requirement to patch older shipped versions independently.

**RATIONALE**  Matches the team's actual need — only the latest version matters. Revisit this rule if parallel-version support ever becomes necessary; it would require rethinking the fast-forward-only policy too.

**ENFORCEMENT**  Advisory — team convention.

## P1.2 Branch naming

### P1.2.1 Default: JIRA-XXX-kebab-desc, no type prefix

**RULE**  Most branches — anything that merges straight into development, and any sub-branch cut from an umbrella branch — are named JIRA-XXX-kebab-desc. No type prefix. The type prefix is reserved for the one exception in 1.2.2.

**RATIONALE**  This is the common case — most branches never take other branches into them, so the default should be the simple form. A fixed, mechanical pattern means branch purpose and tracking ticket are visible at a glance, with no free-form naming to interpret.

**GOOD**

```cpp
JIRA-123-record-batch-reader
JIRA-456-docking-layout-crash
```

**BAD**

```cpp
JIRA-123  // missing description
my-branch  // missing ticket number
feat/JIRA-123-record-batch-reader  // type prefix, but this isn't an umbrella branch
```

**ENFORCEMENT**  Advisory — code review; a server-side branch-name hook (regex) is a good candidate if/when available on the GitLab tier in use.

### P1.2.2 Exception: umbrella branches get a type prefix

**RULE**  Only when a branch is itself an umbrella — i.e. other branches will be merged into it before it merges into development — does it get a type prefix: `<type>`/JIRA-XXX-kebab-desc, tied to the umbrella-level Jira ticket. `<type>` is drawn from the same fixed type list as P1.3.1 — feat, fix, style, chore, docs, refactor, test, perf, build, ci, revert — using the identical short form, so a branch prefix and the commit it eventually becomes never disagree. Sub-branches cut from that umbrella branch still follow the default in P1.2.1 (no prefix), since the umbrella branch already carries that context.

**RATIONALE**  Keeps the type prefix meaningful at exactly one level: the umbrella branch, which is the thing that eventually becomes a feat/fix/etc. commit on development. Applying it to every branch would be noise, since the vast majority of branches are never an umbrella for anything else.

**GOOD**

```cpp
feat/JIRA-123-record-batch-reader  // umbrella branch, JIRA-456/JIRA-457/etc. will merge into this before it merges into development
```

**BAD**

```cpp
feat/JIRA-999-fix-typo  // BAD -- this is a single, standalone change; no type prefix needed, see P1.2.1
```

**ENFORCEMENT**  Advisory — code review.

### P1.2.3 Sub-branches squash into the umbrella branch; the umbrella branch fast-forwards into development

**RULE**  Each sub-branch MR into the umbrella branch is squashed to one commit, following the same Conventional Commits format as a normal development merge. The umbrella branch itself is the one exception to squashing: its merge into development is a fast-forward — no squash, no merge commit — which requires the umbrella branch to be rebased onto the latest development (P1.4.2) immediately before merging so the fast-forward is possible. This preserves each sub-branch's individual squashed commit exactly as it appears on the umbrella branch.

**RATIONALE**  If the umbrella branch also squashed into development, every sub-branch's Conventional Commit — type, scope, description, ticket — would collapse into a single commit by the time development's history is read. Since git-cliff (P2.4.2) and the SemVer-bump derivation (P2.1) both work by reading commit types from history between tags, that loss is not cosmetic: it silently produces an inaccurate changelog and can derive the wrong version bump for any release that included umbrella work. Fast-forward is the cleaner fix versus a merge commit: it avoids creating any new commit at all, consistent with how release (P1.1.1) also only ever fast-forwards — same mechanism, already familiar elsewhere in this workflow.

**GOOD**

```bash
git checkout development
git merge --ff-only feat/JIRA-123-record-batch-work   # umbrella branch, NOT squashed
git push origin development
# development now ends in: ...feat(core): add record batch reader (JIRA-456),
#                           fix(core): correct record batch reader edge case (JIRA-457)
```

**BAD**

```cpp
# BAD -- squashing the umbrella branch into development collapses this into ONE commit:
feat(core): JIRA-123 umbrella of record batch work
# git-cliff and the version-bump derivation (P2.1) can no longer see the individual
# feat/fix entries that made up this umbrella -- changelog and version accuracy both degrade
```

**ENFORCEMENT**  GitLab project merge method is set to Fast-forward merge (see P1.4.1). For the umbrella branch's own MR into development, the squash checkbox is left OFF, so GitLab fast-forwards it as-is. Advisory — code review to confirm squash was left off for this one MR.

## P1.3 Commit messages — Conventional Commits

### P1.3.1 Format: type(scope): description (JIRA-XXX)

**RULE**  Type is one of feat, fix, style, chore, docs, refactor, test, perf, build, ci, revert. Scope is required whenever the change is scoped to a specific part of the tree, and must be one of the fixed list recorded in the project profile (C-14), extendable only by amending that list, never invented ad hoc. Description is imperative mood, lowercase, no trailing period. Jira ticket reference is always required, no exceptions, even for trivial changes (typo fixes, dependency bumps get a real ticket first). The subject line (the whole type(scope): description (JIRA-XXX) string) is capped at 72 characters; if the change needs more explanation, that goes in the commit body, wrapped at 100 characters per line.

**RATIONALE**  A fixed type/scope vocabulary turns commit history into a queryable log (git log --grep '^feat(core)') instead of free-text prose that means something different depending on who wrote it — and pre-1.0 versioning (P2) is mechanically derived directly from these types. The 72-character subject limit is adapted from the traditional 50-character git convention, widened specifically to accommodate the mandatory type(scope)/JIRA-ticket overhead this format carries that a plain free-text commit message wouldn't — a strict 50 would leave almost no room for the actual description. It also directly helps avoid GitLab's squash-message truncation (P1.4.3), since a subject that never gets long in the first place can't hit the truncation threshold as easily.

**GOOD**

```cpp
feat(core): add record batch reader (JIRA-123)
fix(cmake): correct vcpkg toolchain path (JIRA-456)
style(gui): reformat dock_manager.cpp with clang-format (JIRA-789)
```

**BAD**

```cpp
Added the record reader.
fix: bug (JIRA-123)  // too vague
feat(RecordReader): ...  // scope not in the fixed list
feat(core): add a much longer description that blows well past the seventy-two character subject line limit (JIRA-789)  // BAD -- too long, wrap the extra detail into the body instead
```

**ENFORCEMENT**  Advisory — code review, checked as part of the four-step manual review process (P1.8). No commit-message linting tool is in use today; deliberately not adopting one for now given GitLab’s squash-message truncation behavior (P1.4.3) limits how much a tool like this can actually guarantee.

### P1.3.2 WIP commits are unformatted; only the squash message conforms

**RULE**  Commits on a feature branch during active work are not required to follow Conventional Commits. The MR title (which becomes the squash commit message on merge) is the only commit message enforced.

**RATIONALE**  Enforcing format on commits nobody but the author will ever see is friction with no payoff. Enforcement effort belongs where it's actually visible in history.

**ENFORCEMENT**  Advisory — not tool-checked; the MR title is what a reviewer checks, not individual pushes to the feature branch.

### P1.3.3 Breaking changes use ! + a BREAKING CHANGE: footer

**RULE**  A commit that breaks compatibility (API signature change, changed file format, removed CLI flag, etc.) marks the type with ! and includes a BREAKING CHANGE: footer describing what breaks and how to migrate.

**RATIONALE**  This is what makes automated version derivation possible (P2) — breaking-change commits are what bump the version pre-1.0 — and it makes breaking changes impossible to merge without the author consciously flagging them.

**GOOD**

```cpp
feat(core)!: change RecordReader::readBatch return type (JIRA-456)

BREAKING CHANGE: readBatch now returns std::expected<RecordBatch, ReadError>
instead of a raw RecordBatch. Callers must check the result before use.
```

**ENFORCEMENT**  Advisory — code review, both for footer format and for whether a change actually warrants the marker.

### P1.3.4 Reverts follow the same convention

**RULE**  git revert's auto-generated Revert "..." message is reformatted before merge to revert: <original description> (JIRA-XXX), referencing the original ticket or a new one if the revert needs its own justification captured.

**GOOD**

```cpp
revert(core): remove record batch reader (JIRA-789)
```

**BAD**

```cpp
Revert "feat(core): add record batch reader (JIRA-456)"  // BAD -- raw git-generated message, not reformatted
```

**ENFORCEMENT**  Advisory — code review, same as all other commit-format rules; also code review for whether a fresh ticket is warranted.

## P1.4 Merging

### P1.4.1 Merge method: fast-forward, with squash applied per-MR by default

**RULE**  The GitLab project merge method is set to Fast-forward merge — no merge commits are ever created, for any branch, full stop. Combined with the per-MR squash option (checked by default), a normal branch's MR into development results in a single squashed commit fast-forwarded into place, with no merge commit. The umbrella branch's own merge into development (P1.2.3) is the one case where squash is left unchecked, so its already-squashed sub-branch commits fast-forward in individually. The squash commit message follows the Conventional Commits rule (P1.3.1); since the MR title should already be in that format, the default squash message needs no editing — but see P1.4.3 for a GitLab-specific caveat on this.

**GOOD**

```cpp
feat(core): add record batch reader (JIRA-123)  # single squashed commit, fast-forwarded onto development, no merge commit
```

**BAD**

```cpp
Merge branch 'JIRA-123-record-batch-reader' into development  # BAD -- merge commits are never
  # created under this project's merge method; this branch should have been squashed
```

**ENFORCEMENT**  GitLab project setting: Merge method = Fast-forward merge. Per-MR squash checkbox: on by default, off only for the umbrella branch's own merge into development (P1.2.3).

### P1.4.2 Feature branches are rebased onto development, never merged from it

**RULE**  While a MR is open, if development has moved forward, the dev rebases their feature branch onto the latest development and force-pushes with --force-with-lease (never bare --force). Rebase/force-push is only ever performed on your own feature branch — never on development or release. This applies to umbrella branches too: keeping an umbrella branch rebased onto development throughout its life is what makes its eventual fast-forward merge (P1.2.3) possible at all.

**RATIONALE**  Keeps feature-branch history linear and easy to review incrementally, consistent with the fast-forward merge method (P1.4.1). --force-with-lease prevents silently overwriting a collaborator's pushes to the same branch — the standard failure mode of bare --force that costs someone their work with no warning.

**GOOD**

```bash
git fetch origin && git rebase origin/development && git push --force-with-lease
```

**BAD**

```bash
git push --force   # no lease check — can silently destroy a teammate's commits
```

**ENFORCEMENT**  GitLab branch protection prevents force-push to development/release entirely (actual gate). Advisory — code review / onboarding docs for --force-with-lease usage on feature branches.

### P1.4.3 GitLab truncates long squash-merge messages — verify before confirming

**RULE**  This applies to normal squashed merges only (not the umbrella branch's un-squashed fast-forward, P1.2.3, which introduces no new commit message). GitLab auto-generates the squash-merge commit message from the MR's title/commits, but truncates it with a trailing “...” when it runs long. The person completing the merge must check the commit message field before confirming and, if truncated, manually retype it in full, correctly-formatted Conventional Commits form — never merge with a silently truncated message.

**RATIONALE**  A truncated commit message breaks the same things the umbrella-squash trap (P1.2.3) breaks — git-cliff and the version-bump derivation (P2.1) both read this text, so a silently truncated message is a real correctness bug in the changelog, not just a cosmetic one. This can't be fully solved by a pre-commit hook, since the truncation happens inside GitLab at merge time, after any local check has already passed.

**BAD**

```cpp
feat(core): add record batch reader and fix related edge cases in the be...  // BAD -- truncated, merged without checking
```

**ENFORCEMENT**  Manual MR checklist — the person merging is responsible for this check every time; no tooling catches it today.

## P1.5 Branch cleanup

### P1.5.1 Branches auto-delete on merge

**RULE**  Repository setting deletes the source branch automatically once a MR is merged into development.

**RATIONALE**  Free cleanup, zero downside — a merged branch has already had its content absorbed via squash.

**ENFORCEMENT**  GitLab “automatically delete source branch” setting (actual gate).

## P1.6 Repository hygiene

### P1.6.1 .gitignore follows durable principles, not a locked exhaustive list

**RULE**  Entries fall into a small set of categories — build output, package-manager artifacts, IDE-local state for both supported IDEs — and new entries are added as they come up rather than requiring this document to be revised for every one. Note that test_data/ is NOT in this list — see P1.6.2, it's committed to the repo, not ignored.

**RATIONALE**  A .gitignore that tries to be a complete, permanent list becomes stale the moment the toolchain changes. Better to state the categories that should always be excluded and let the file grow organically as new instances show up.

**GOOD**

```gitignore
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

```bash
git add build/  # BAD -- build output should never be tracked
git add .vs/  # BAD -- IDE-local state, differs per developer
```

**ENFORCEMENT**  Advisory — code review. .gitignore evolves by ordinary MR, no special process.

### P1.6.2 test_data/ is committed to the repository

**RULE**  Test fixtures and sample data live in test_data/ and are tracked normally in git — not gitignored. A fixture is the smallest file that exercises the case it exists for, never a copy of a production dataset, and is confirmed to carry nothing whose classification exceeds the repository's own marking (P3.1) before it is committed.

**RATIONALE**  Committing fixtures is what makes a test suite runnable from a fresh clone with no setup step, which matters more here than usual because the review process (P1.8) has a reviewer build and test the branch by hand. The size and classification constraints are the price of that: a repository is cloned by everyone and kept forever, so a large binary fixture is permanent, and a fixture derived from real data is the most common way controlled data reaches somewhere it should not be.

**ENFORCEMENT**  Advisory — code review.

### P1.6.3 Line endings are normalized by a committed .gitattributes, not by developer settings

**RULE**  A .gitattributes at the repository root sets `* text=auto`, so text files are stored with LF in the repository and checked out with whatever endings the developer's platform expects. File types that require CRLF to function (.bat, .cmd, .ps1) are pinned to CRLF explicitly. Binary file types committed under test_data/ (P1.6.2) are marked binary explicitly rather than left to git's content-detection heuristic. No developer relies on a personal core.autocrlf setting to get correct results.

**RATIONALE**  Without this file, what actually lands in the repository depends on each developer's local core.autocrlf. Two people with different settings editing the same file produce a diff in which every line changed, which makes reviewing the real one-line change impossible and makes git blame point at whoever last flipped the endings rather than whoever wrote the code. Today this is latent, since everyone is on Windows; it surfaces the moment anything is built or edited on a second platform, which is a stated future direction. The rule costs one file now and prevents a repository-wide reformatting event later.

Marking binaries explicitly matters more here than in most repositories precisely because P1.6.2 commits test fixtures to git. Git's binary detection is good but not infallible, and a line-ending-normalized binary fixture is a corrupted fixture — one that fails at read time with an error pointing nowhere near the cause. Pinning the Windows script types is the mirror image of the same concern: cmd.exe mis-parses a .bat file that has LF endings.

**GOOD**

```gitattributes
# .gitattributes at the repository root

# Normalize on commit: LF in the repository, native in the working tree.
* text=auto

# Explicit for the types this project actually has, so no tool's guess
# overrides the rule above.
*.h      text eol=lf
*.cpp    text eol=lf
*.cmake  text eol=lf
*.txt    text eol=lf
*.md     text eol=lf
*.json   text eol=lf

# Windows scripts must keep CRLF or cmd.exe mis-parses them.
*.bat    text eol=crlf
*.cmd    text eol=crlf
*.ps1    text eol=crlf

# Binary -- never normalized, never diffed as text. This matters because
# test_data/ is committed (P1.6.2): a normalized binary fixture is a corrupted one.
*.bin    binary
*.dat    binary
*.zip    binary
*.png    binary
*.ico    binary
```

**BAD**

```bash
git config --global core.autocrlf true  # BAD as the project's answer -- this is a per-developer
                                        # setting, so it guarantees nothing about what any other
                                        # developer commits
```

*Adding .gitattributes to a repository that already has content does not retroactively fix files already committed with the wrong endings. Immediately after the .gitattributes commit, run `git add --renormalize .` once and commit the result as its own chore commit, so the one-time reformatting is isolated from any real change.*

**ENFORCEMENT**  Git itself (actual gate) — once .gitattributes is committed, normalization happens at commit time regardless of any developer's local configuration. Advisory — code review that a newly introduced binary file type gets added to the binary list before the first file of that type is committed.

## P1.7 Merge request mechanics

### P1.7.1 One required approval, any team member

**RULE**  Minimum 1 approval before merge. No CODEOWNERS restriction, no seniority requirement — any team member may approve any MR.

**ENFORCEMENT**  GitLab MR approval rule: 1 required approval, no restricted approver group (actual gate).

### P1.7.2 MR size is soft-guided, not hard-blocked

**RULE**  Target under ~400 changed lines, excluding generated/lockfiles. MRs trending larger should be reconsidered as an umbrella-branch structure (P1.2.2) rather than one large diff.

**ENFORCEMENT**  Manual MR checklist / Advisory — reviewer's judgment during manual code review.

### P1.7.3 MR description follows a fixed template

**RULE**  What changed · Jira link · how it was tested · screenshots/recording for any UI-visible change.

**ENFORCEMENT**  GitLab MR description template file (.gitlab/merge_request_templates/).

## P1.8 Manual review process

This project does not currently run an automated CI pipeline. Every MR is verified by the approving reviewer performing four steps, in order, before approving. This section documents that process explicitly — until now it existed only as tribal knowledge, which is itself the kind of ambiguity this whole document exists to remove.

### P1.8.1 Four-step sequence, performed by the approving reviewer

**RULE**  1) AI agent review — reviewer exports the MR's .diff and runs it through the in-house review agent (checks standards adherence, commit message format, formatting/static-analysis conformance), and posts the agent's output as an MR comment before proceeding. 2) Manual code review — reviewer reads the diff themselves, informed by (not replaced by) the agent's output. 3) Manual build — reviewer pulls the branch and builds it locally, on every platform the project profile lists as supported (C-27). 4) Manual test — reviewer runs the relevant test suite locally and confirms the MR's stated “how tested” claims. A MR is not approved until all four steps are complete, in this order.

**RATIONALE**  Without CI, every one of these checks depends entirely on a human remembering to do it, in a useful order — agent review first means the reviewer's own read of the diff isn't spent re-deriving problems a tool already caught; build and test last because they're the most expensive steps and shouldn't be run against code that's already failed static review. Posting the agent output as a comment is the only durable record that the step actually happened, useful for later auditing and for catching a reviewer who skipped it.

*Every step here depends on a human performing it correctly and in order, and nothing prevents an incomplete review from approving anyway. That is a property of the process as it stands, and reviewers should read it as one.*

**ENFORCEMENT**  Manual MR checklist — no automated gate exists today.
