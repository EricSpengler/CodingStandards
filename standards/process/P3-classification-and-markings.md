# P3. Classification & Export Control Markings

Every tracked .h/.cpp file carries a classification header as the very first lines of the file, no exceptions.

## File markings and data scope

### P3.1 Standard header, present on every file

**RULE**  The header includes: the classification marking (UNCLASSIFIED by default), an @file tag naming the file, an @brief tag summarizing its purpose in one or two sentences, and an @export_control statement. "Not subject to export control regulations" is the safe default for the vast majority of files. If a file is ever suspected to warrant a different classification or export-control status, that determination goes to the export-control point of contact — never guessed.

**RATIONALE**  A missing or inconsistent header is the kind of thing that's invisible day-to-day and only matters the one time it's audited — making it a fixed, always-present block removes any judgment call about when it's needed.

**GOOD**

```cpp
// UNCLASSIFIED

/**
 * @file recordreader.h
 * @brief RAII wrapper around buffered file access for core.
 * @export_control This file is not subject to export control regulations.
 */
```

**BAD**

```cpp
#ifndef CORE_IO_RECORDREADER_H  // BAD -- no classification header before the include guard
#define CORE_IO_RECORDREADER_H
```

**ENFORCEMENT**  Advisory — code review today. A pre-commit hook or CI script checking the first 10 lines of every tracked .h/.cpp file for the marking is a strong automation candidate once available (see the Enforcement Summary, known gap).

### P3.2 Data sensitivity scope

**RULE**  Every project records a data-sensitivity determination in its project profile, stating which categories of regulated data it does and does not handle — PHI, PII, CUI, export-controlled technical data. The determination is made explicitly and confirmed with whoever owns compliance for the program; it is never inferred from the project's name or assumed from what the code appears to touch.

**RATIONALE**  Recording it explicitly stops the question being re-litigated, or silently answered differently by two developers, six months apart. It is written down as a *determination* rather than an assumption because the consequences of getting it wrong are external to the codebase. The determination also decides how much of this guide a project needs: a project handling personal data requires a data-handling topic this standard does not currently contain — file-at-rest encryption, logging restrictions around sensitive fields, retention policy — and that absence is only safe while the determination says none is needed.

**ENFORCEMENT**  Advisory — the determination lives in the project profile and is revisited whenever a project's data sources change.
