# Appendix C: Example .clang-tidy

This is the file Sections 3 and 6 refer to whenever a rule's ENFORCEMENT line names a clang-tidy check. It lives at the repository root. Every check enabled below traces to a specific numbered rule, noted in the comment above it — checks with no rule behind them are deliberately not enabled, so that turning a check off is always a visible decision about a written rule rather than silent tuning.

```cpp
---
# Enabled checks. Order matches the sections they enforce.
# -* first: start from nothing enabled and opt in explicitly, so a clang-tidy
# version upgrade can never silently add checks nobody agreed to.
Checks: >
  -*,

  llvm-header-guard,

  readability-identifier-naming,

  cppcoreguidelines-owning-memory,
  cppcoreguidelines-pro-type-cstyle-cast,
  modernize-loop-convert,
  misc-const-correctness,
  modernize-use-nullptr,
  google-explicit-constructor,
  modernize-use-override,
  performance-noexcept-move-constructor,
  performance-unnecessary-value-param,
  google-build-using-namespace,
  cppcoreguidelines-virtual-class-destructor,
  bugprone-unhandled-self-assignment,
  performance-move-const-arg,
  bugprone-use-after-move,
  performance-for-range-copy,

  readability-function-size,
  readability-function-cognitive-complexity,

  cppcoreguidelines-no-malloc,
  cppcoreguidelines-special-member-functions

# Only first-party headers are analyzed. Third-party headers pulled in from
# vcpkg (Qt, HDF5, Vulkan, DuckDB) are not ours to fix -- see 11.4.
HeaderFilterRegex: '^.*/(core|gui|tests)/.*\.h$'

# Every enabled check is an error, not a warning. Rationale in 16.2: a warning
# nobody is forced to clear accumulates until the output is worthless.
WarningsAsErrors: '*'

FormatStyle: file

CheckOptions:
  # ---- 3.4 namespaces ----
  readability-identifier-naming.NamespaceCase: lower_case

  # ---- 3.5 classes and structs, 3.16 type aliases, 3.13 template parameters ----
  readability-identifier-naming.ClassCase: CamelCase
  readability-identifier-naming.StructCase: CamelCase
  readability-identifier-naming.UnionCase: CamelCase
  readability-identifier-naming.TypeAliasCase: CamelCase
  readability-identifier-naming.TypedefCase: CamelCase
  readability-identifier-naming.TemplateParameterCase: CamelCase
  readability-identifier-naming.TypeTemplateParameterCase: CamelCase
  readability-identifier-naming.ValueTemplateParameterCase: CamelCase

  # ---- 3.18 pure interfaces take an I prefix ----
  readability-identifier-naming.AbstractClassCase: CamelCase
  readability-identifier-naming.AbstractClassPrefix: 'I'

  # ---- 3.6 enum class and its members ----
  readability-identifier-naming.EnumCase: CamelCase
  readability-identifier-naming.EnumConstantCase: CamelCase
  readability-identifier-naming.ScopedEnumConstantCase: CamelCase

  # ---- 3.7 functions, 3.8 locals and parameters ----
  readability-identifier-naming.FunctionCase: camelBack
  readability-identifier-naming.MethodCase: camelBack
  readability-identifier-naming.PublicMethodCase: camelBack
  readability-identifier-naming.ProtectedMethodCase: camelBack
  readability-identifier-naming.PrivateMethodCase: camelBack
  readability-identifier-naming.VariableCase: camelBack
  readability-identifier-naming.LocalVariableCase: camelBack
  readability-identifier-naming.ParameterCase: camelBack

  # ---- 3.9 members carry no prefix or suffix, 3.15 statics are no different ----
  readability-identifier-naming.MemberCase: camelBack
  readability-identifier-naming.PublicMemberCase: camelBack
  readability-identifier-naming.ProtectedMemberCase: camelBack
  readability-identifier-naming.PrivateMemberCase: camelBack
  readability-identifier-naming.PrivateMemberPrefix: ''
  readability-identifier-naming.PrivateMemberSuffix: ''
  readability-identifier-naming.ProtectedMemberPrefix: ''
  readability-identifier-naming.ProtectedMemberSuffix: ''
  readability-identifier-naming.ClassMemberCase: camelBack
  readability-identifier-naming.StaticVariableCase: camelBack

  # ---- 3.11 class- and namespace-level constants are UPPER_SNAKE ----
  readability-identifier-naming.ClassConstantCase: UPPER_CASE
  readability-identifier-naming.GlobalConstantCase: UPPER_CASE
  readability-identifier-naming.StaticConstantCase: UPPER_CASE

  # ---- 3.12 local constants are camelBack, NOT UPPER_SNAKE ----
  # Known limitation, already noted in 3.12's ENFORCEMENT line: clang-tidy
  # resolves a constexpr local against both LocalConstantCase and
  # ConstexprVariableCase, and which one wins is not reliably documented.
  # ConstexprVariableCase is therefore left unset rather than pinned to a value
  # that would contradict 3.11 or 3.12 depending on scope. Local constant
  # casing stays a code-review item until this is resolved upstream.
  readability-identifier-naming.LocalConstantCase: camelBack
  readability-identifier-naming.LocalConstantPointerCase: camelBack

  # ---- 3.14 macros, restricted to include guards ----
  readability-identifier-naming.MacroDefinitionCase: UPPER_CASE

  # ---- 3.3 include guards mirror the full path ----
  # GuardPrefix is empty because the guard already starts at the source root
  # (CORE_IO_HDF5READER_H), not at a project-wide prefix.
  llvm-header-guard.HeaderFileExtensions: 'h'

  # ---- 6.2.1 max function length 60 lines ----
  readability-function-size.LineThreshold: 60

  # ---- 6.2.3 max nesting depth 3 ----
  readability-function-size.NestingThreshold: 3

  # ---- 6.2.4 max 5 parameters ----
  readability-function-size.ParameterThreshold: 5

  # ---- 6.2.2 complexity ceiling ----
  # See the note below: readability-function-size has no cyclomatic-complexity
  # option, so BranchThreshold is the closest available proxy and
  # readability-function-cognitive-complexity is enabled alongside it.
  readability-function-size.BranchThreshold: 10
  readability-function-cognitive-complexity.Threshold: 25
  readability-function-cognitive-complexity.IgnoreMacros: true

  # ---- 6.4.2 rule of five, all five declared explicitly ----
  cppcoreguidelines-special-member-functions.AllowSoleDefaultDtor: false
  cppcoreguidelines-special-member-functions.AllowMissingMoveFunctions: false

  # ---- 6.1.18 string_view for read-only string parameters ----
  performance-unnecessary-value-param.AllowedTypes: 'std::string_view;std::span'
...
```

## Correction to 6.2.2's stated enforcement

Section 6.2.2 sets a cyclomatic complexity ceiling of 10 and names `readability-function-size (CyclomaticComplexityThreshold: 10)` as its enforcement. That option does not exist. `readability-function-size` measures lines, statements, branches, parameters, nesting, and variables — not McCabe cyclomatic complexity — and there is no clang-tidy check that computes McCabe directly.

Two checks together get close, and both are enabled above:

- `readability-function-size.BranchThreshold: 10` counts branch statements, which is the dominant term in the McCabe count. It does not count `&&` and `||` as separate paths, so it reads slightly lower than true cyclomatic complexity for a function with compound conditions.
- `readability-function-cognitive-complexity.Threshold: 25` measures cognitive complexity (the Sonar metric), which weights nesting more heavily than McCabe does and ignores a flat `switch`. It catches the deeply-nested functions that a pure branch count misses.

Neither is the metric 6.2.2 names, and the pair is deliberately set slightly loose so the two of them together approximate a McCabe ceiling of 10 rather than double-penalizing the same function. If an exact McCabe number is wanted as a gate, that needs a separate tool (`lizard` is the usual choice) wired into CI, which does not exist today.

*Open item, needs team ratification: either 6.2.2's rule text is amended to name branch count and cognitive complexity as the actual metrics, or a dedicated cyclomatic-complexity tool is adopted. Written here as a documented approximation rather than left as a rule whose stated enforcement does not exist.*
