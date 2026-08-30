# C++ Standards & Styling Guide — Master Topic List

This is the running tracker for the whole standards effort: what's been built out (and where), what's still open, and what's been deliberately deferred. Update this alongside the main guide as topics get covered.

---

## ✅ Covered (see the main guide)

| Topic | Section |
|---|---|
| Git Workflow | 1 |
| Versioning | 2 |
| Naming Conventions | 3 |
| Classification & Export Control Markings | 4 |
| Documentation (Doxygen) | 5 |
| Code Style (language features, complexity limits, error handling, memory management, formatting) | 6 |
| Enforcement Summary | 7 |
| Appendix A: Example Doxyfile | — |
| Appendix B: Example .clang-format | — |

---

## Not yet started — original five-category list

- CMake structure

*(Code style was the fifth original category — now covered as Section 6.)*

---

## Not yet started — surfaced during conversation

- Toolchain/build specifics (C++23 feature subset, cross-toolchain MSVC/GCC parity, warnings-as-errors flags)
- Core/GUI architectural boundary (the Qt-free `core` rule)
- Third-party library rules (Qt, HDF5, Vulkan, DuckDB, CLI11, JSON library decision between glaze/nlohmann, zlib/zip)
- Testing standards (GoogleTest/QTest boundary)
- User-facing error message conventions
- Static analysis tooling scope (beyond clang-tidy)

---

## Not yet started — added along the way

- Logging strategy
- Threading/concurrency model
- Dependency & vulnerability management
- API stability/deprecation policy for `core`
- Packaging/installer standards
- GUI architecture pattern (including Qt signal/slot naming conventions)
- Sanitizers in testing
- Data/file format versioning
- Crash reporting/telemetry
- Developer onboarding
- Application settings/config persistence
- Secrets management
- Accessibility (a11y)
- Performance/benchmarking practices
- Module/code ownership map
- Internationalization/localization
- User Documentation (README, CLI `--help` conventions, GUI in-app help, where user docs live)

---

## Known gaps in already-covered sections (from the internal audit + recheck passes)

- No `.clang-tidy` appendix — referenced dozens of times throughout Sections 3 and 6 as the enforcement mechanism, never actually provided as a file. Same category of gap `.clang-format` had until Appendix B was added.
- No `cliff.toml` appendix — referenced in 2.4.2 as the changelog tool config, never provided.
- Exception class naming convention (e.g. `InvalidRecordException` vs `RecordError`) — flagged early during the naming conversation, never delivered.
- `std::move` usage guidance — when to call it explicitly vs. rely on RVO/implicit moves.
- Fixed-width integer types (`uint32_t`/`int64_t`) vs. `int`/`size_t` — no stated preference, more relevant than usual given this codebase parses binary formats (HDF5).
- Uniform/brace initialization style (`int x{5};` vs `int x = 5;`) — not addressed.
- Structured bindings (`auto [a, b] = pair;`) — not addressed.
- Stale/abandoned branch policy — unclear if this is even wanted; flag before adding.
- Blank-line conventions within a file (beyond what clang-format enforces) — unclear if wanted; flag before adding.

---

## Resolved — not a topic, a settled question

- Sensitive data scope: this tool does not process PHI/PII; only CUI/export-control applies. Recorded in Classification (4.2).

---

## Deferred, explicitly, for later

- Standing up GitLab CI
- Docker container creation
- Dedicated Linux building and testing

---

## Reference standards used throughout

C++ Core Guidelines, Google C++ Style Guide, LLVM Coding Standards, and SEI CERT C++ Coding Standard are the standing cross-reference set for Code Style and Naming. Qt's own conventions get added once GUI-specific topics are covered. See the separate References document for the full list with links, including the git-workflow and tooling-spec sources (Conventional Commits, SemVer, GitHub Flow, Gitflow, Doxygen Manual).
