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

**ENFORCEMENT**  Manual — run as part of the release process (2.4.1, step 3); cliff.toml configuration is what actually controls this. See Appendix D for the file itself, the exact command, and how to use the same tool to verify the version bump derived in 2.1 before tagging.

## 2.5 Poison-pill reset rebuild

#### 2.5.1 Day-14 rebuild fallback when nothing is releasable

**RULE**  The tool has a poison-pill license mechanism: builds expire and shut down 21 days after being built, by design, to force users onto current versions during testing. Every sprint close-out (day 14, biweekly) produces a build. If the sprint's commits don't warrant a version bump per 2.1, no new tag or changelog entry is created — instead, release at its current tip is rebuilt and repackaged as-is (same source, same version tag, fresh build/package output only) purely to reset the license expiry timer.

**RATIONALE**  Anchoring the rebuild trigger to the existing sprint close-out means there's no separate calendar to watch — “did we ship a build this sprint” is already a natural checkpoint the team hits every two weeks, and a build always goes out at day 14 regardless of which case applies, so the 21-day timer never has a chance to lapse.

**ENFORCEMENT**  Manual PR checklist / sprint close-out ritual.
