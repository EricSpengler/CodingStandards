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
