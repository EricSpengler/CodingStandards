# Enforcement Summary

A quick-reference map of every hard rule in this standard to what actually enforces it. Anything not listed here is Advisory — code review by default.

*Read the three categories literally. **Actual gate** means a tool rejects the change — a compiler, a repository setting, clang-format. **Manual MR checklist** means tool-checkable in principle, but verified only because the reviewer runs it by hand during the four-step review (P1.8); it is not a gate. **Advisory** means a person reading a diff, or nothing.*

| Rule | Section | Enforcement |
| --- | --- | --- |
| Conventional Commit format, branch naming | P1.2, P1.3 | Advisory — code review only; no linting tool adopted (see P1.3.1 note) |
| Merge method (fast-forward, squash per-MR by default) | P1.4 | GitLab project setting (Fast-forward merge) + per-MR squash checkbox (actual gate) |
| GitLab squash-message truncation — manual verification | P1.4.3 | Manual MR checklist — no tooling catches this today |
| Fast-forward-only release, no direct push to development/release | P1.1, P1.4 | GitLab branch protection rules (actual gate) |
| 1 approval minimum before merge | P1.7 | GitLab MR approval rule (actual gate) |
| Branch auto-delete on merge | P1.5 | GitLab repo setting (actual gate) |
| Line-ending normalization (.gitattributes) | P1.6.3 | Git (actual gate) once committed; Advisory for adding new binary types |
| Four-step manual review (agent → review → build → test) | P1.8 | Manual MR checklist — no automated gate exists |
| Version bump derived from commit types | P2.1 | Manual MR checklist at release-cut time |
| Release process sequence, tag-after-merge | P2.4 | Documented procedure, not tool-enforced |
| Include guard naming (path-based, fused tokens) | C1.3 | clang-tidy llvm-header-guard (Manual MR checklist) |
| Namespace/class/struct/enum/function/variable/member/parameter/template/macro casing | C1.4–C1.9, C1.13–C1.14 | clang-tidy readability-identifier-naming (Manual MR checklist) |
| Boolean member/accessor naming (no collision) | C1.10 | Compiler-enforced (real gate) + Advisory for consistent application |
| Parameter/member name collision | C1.20 | Compiler-enforced (real gate) — MSVC C4458 at /W4, an error under warnings-as-errors; GCC -Wshadow. Clang needs -Wshadow-all. Advisory for whether the renamed parameter still denotes the same value |
| Class/namespace-level constant casing | C1.11 | clang-tidy readability-identifier-naming (Manual MR checklist) |
| Type alias casing | C1.16 | clang-tidy readability-identifier-naming (Manual MR checklist) |
| Classification header present | P3.1 | Advisory — code review (no automated scan today) |
| Doxygen coverage (every entity, all access levels) | C2.2 | Doxygen build (WARN_IF_UNDOCUMENTED) — Manual MR checklist today |
| Doxygen @brief present | C2.3 | Doxygen build (WARN_IF_UNDOCUMENTED) — Manual MR checklist today |
| @tparam on every template parameter | C2.3.2 | Doxygen build (WARN_IF_UNDOCUMENTED) — Manual MR checklist today |
| No owning raw pointers | C3.1.1, C3.4.1 | clang-tidy cppcoreguidelines-owning-memory (Manual MR checklist) |
| No C-style casts | C3.1.2 | clang-tidy cppcoreguidelines-pro-type-cstyle-cast (Manual MR checklist) |
| Range-based for preferred | C3.1.9 | clang-tidy modernize-loop-convert (Manual MR checklist) |
| const-correctness | C3.1.12 | clang-tidy misc-const-correctness (Manual MR checklist) |
| nullptr, not NULL/0 | C3.1.13 | clang-tidy modernize-use-nullptr (Manual MR checklist) |
| Explicit single-arg constructors | C3.1.14 | clang-tidy google-explicit-constructor (Manual MR checklist) |
| override required on virtual overrides | C3.1.15 | clang-tidy modernize-use-override (Manual MR checklist) |
| noexcept on move ops/swap | C3.1.16 | clang-tidy performance-noexcept-move-constructor (Manual MR checklist) |
| Function length ≤ 60 lines | C3.2.1 | clang-tidy readability-function-size (Manual MR checklist) |
| Cyclomatic complexity ≤ 10 | C3.2.2 | clang-tidy readability-function-size (Manual MR checklist) |
| Nesting depth ≤ 3 | C3.2.3 | clang-tidy readability-function-size (Manual MR checklist) |
| Parameter count ≤ 5 | C3.2.4 | clang-tidy readability-function-size (Manual MR checklist) |
| No manual new/delete/malloc/free | C3.4.1 | clang-tidy cppcoreguidelines-no-malloc (Manual MR checklist) |
| Rule of five | C3.4.2 | clang-tidy cppcoreguidelines-special-member-functions (Manual MR checklist) |
| Formatting (braces, spacing, pointer alignment, column limit) | C3.5 | clang-format (IDE integration + AI agent review, P1.8) |
| No using namespace directives | C3.1.22 | clang-tidy google-build-using-namespace (Manual MR checklist) |
| Virtual destructor on polymorphic base classes | C3.1.23 | clang-tidy cppcoreguidelines-virtual-class-destructor (Manual MR checklist) |
| Self-assignment safety | C3.1.26 | clang-tidy bugprone-unhandled-self-assignment (Manual MR checklist) |
| Include order | C3.5.8 | clang-format IncludeCategories (see Appendix B) |
| [[nodiscard]] on std::expected-returning functions | C3.3.4 | Compiler warning (actual gate, once applied) + Advisory for coverage |
| Pure interface I-prefix | C1.18 | Advisory — code review |
| Commit subject line ≤ 72 chars | P1.3.1 | Advisory — code review (no linting tool, see P1.3.1 note) |
| Class member order (access level + intra-block) | C3.5.9 | Advisory — code review |

**What is not enforced.** Every row above marked *Manual MR checklist* is tool-checkable in principle and checked by a person in practice, because this project runs no automated pipeline. Every row marked *Advisory* is checked by a person reading a diff, or not at all. Those two categories are the majority of this table, and a reviewer should treat them as the part of the review that only they can do.

Commit-message format is deliberately not linted: the host truncates long squash-merge messages at merge time (P1.4.3), after any local check has already passed, so a linter would pass and the recorded message would still be wrong.
