# Appendix B: Example .clang-format

```yaml
BasedOnStyle: LLVM
Language: Cpp

# C3.5.2, C3.5.3
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 100

# C3.5.1
BreakBeforeBraces: Allman

# C3.5.4
PointerAlignment: Left
DerivePointerAlignment: false

# C3.5.5
AccessModifierOffset: -4
IndentAccessModifiers: false

# C3.5.6
SpaceBeforeParens: ControlStatements

# C3.5.7
AllowShortFunctionsOnASingleLine: InlineOnly
AllowShortIfStatementsOnASingleLine: false

# C3.5.8 -- include order: own header, first-party, third-party, C system + stdlib combined
IncludeBlocks: Regroup
# CaseInsensitive, not `true`: `true` sorts by raw ASCII, which puts every
# capitalised header (<GuiToolkit/Window.h>) ahead of every lowercase one
# regardless of letter. C3.5.8 says groups are "alphabetized within
# themselves", and this is the setting that makes that literally true.
# Requires clang-format 13 or newer.
SortIncludes: CaseInsensitive
IncludeIsMainRegex: '(Test)?$'   # default -- own header auto-detected as Priority 0,
                                 # matched by base filename against the .cpp, not by the regexes below
# Listed in priority order for readability. Note that clang-format applies the
# FIRST matching regex, so the specific third-party pattern must stay ahead of
# the general angle-bracket one -- reordering those two silently sends every
# and other capitalised third-party header into the standard-library group.
IncludeCategories:
  # 1: first-party -- any quoted include that is not the main header
  - Regex:           '^".*"$'
    Priority:        1
  # 2: third-party, named explicitly
  - Regex:           '^<(GuiToolkit|dataformat)'   # C-32: replace with this project's third-party prefixes
    Priority:        2
  # 3: everything else in angle brackets -- C system + C++ standard library, combined
  - Regex:           '^<.*>$'
    Priority:        3
```
