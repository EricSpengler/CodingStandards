# 4. Classification & Export Control Markings

Every tracked .h/.cpp file carries a classification header as the very first lines of the file, no exceptions.

#### 4.1 Standard header, present on every file

**RULE**  The header includes: the classification marking (UNCLASSIFIED by default), an @file tag naming the file, an @brief tag summarizing its purpose in one or two sentences, and an @export_control statement. "Not subject to export control regulations" is the safe default for the vast majority of files. If a file is ever suspected to warrant a different classification or export-control status, that determination goes to the export-control point of contact — never guessed.

**RATIONALE**  A missing or inconsistent header is the kind of thing that's invisible day-to-day and only matters the one time it's audited — making it a fixed, always-present block removes any judgment call about when it's needed.

**GOOD**

```cpp
// UNCLASSIFIED

/**
 * @file hdf5reader.h
 * @brief RAII wrapper around HDF5 file access for core.
 * @export_control This file is not subject to export control regulations.
 */
```

**BAD**

```cpp
#ifndef CORE_IO_HDF5READER_H  // BAD -- no classification header before the include guard
#define CORE_IO_HDF5READER_H
```

**ENFORCEMENT**  Advisory — code review today. A pre-commit hook or CI script checking the first 10 lines of every tracked .h/.cpp file for the marking is a strong automation candidate once available (see Section 7, known gap).

#### 4.2 Data sensitivity scope

**RULE**  This tool does not process PHI, PII, or other personally-regulated data. CUI/export-control (per 4.1) is the only sensitivity classification that applies to this codebase and the data it handles.

**RATIONALE**  Recorded explicitly so this doesn't get re-litigated or silently assumed differently later — confirmed directly with the team rather than inferred from the project name. If this ever changes (e.g. a future feature ingests personal data), it needs a dedicated data-handling topic — file-at-rest encryption, logging restrictions around sensitive fields, retention policy — none of which exists in this document today because it wasn't needed.

**ENFORCEMENT**  Advisory — revisit this determination if the tool's data sources ever change.
