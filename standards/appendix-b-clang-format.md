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
# CaseInsensitive, not `true`: `true` sorts by raw ASCII, which puts every
# capitalised Qt header (<QString>) ahead of every lowercase one (<hdf5.h>)
# regardless of letter. 6.5.8 says groups are "alphabetized within
# themselves", and this is the setting that makes that literally true.
# Requires clang-format 13 or newer.
SortIncludes: CaseInsensitive
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
