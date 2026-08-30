# C1. Naming Conventions

Every naming decision below was worked through as its own question rather than inherited wholesale from an existing style guide — several (member variable prefixing, boolean naming, local constant casing) had genuine tradeoffs worth deciding deliberately, not defaulting on.

## Files, paths, and include guards

### C1.1 Version-like tokens fuse with the following word

**RULE**  A version-like or numeric-suffixed token (utf8, base64, sha256, etc.) is treated as a single fused word rather than getting its own underscore-separated segment, in any snake_case or SCREAMING_SNAKE_CASE context — directory names, file names, include guards, namespaces.

**RATIONALE**  This is a general rule specifically because it was caught as an inconsistency during review — a directory/file name and its own include guard disagreeing on this point is exactly the kind of ambiguity a junior dev would copy inconsistently without a stated rule to follow.

**GOOD**

```cpp
utf8decoder.h
CORE_TEXT_UTF8DECODER_H
```

**BAD**

```cpp
utf8_decoder.h  // inconsistent with the fused form used elsewhere
CORE_TEXT_UTF8_DECODER_H
```

**ENFORCEMENT**  Advisory — code review.

### C1.2 Directory and file names

**RULE**  Lowercase, snake_case, applying the fusion rule above. File names match the primary class they define.

**GOOD**

```cpp
core/io/recordreader/
recordreader.h
recordreader.cpp
```

**BAD**

```cpp
core/io/RecordReader/  // wrong casing
RecordReader.h  // wrong casing, and doesn't match the class-name-only rule if the file held multiple classes
```

**ENFORCEMENT**  Advisory — code review.

### C1.3 Include guards

**RULE**  SCREAMING_SNAKE_CASE, mirroring the full path exactly (including the fusion rule above), for guaranteed uniqueness across the tree.

**GOOD**

```cpp
// UNCLASSIFIED

/**
 * @file recordreader.h
 * @brief RAII wrapper around buffered file access for core.
 * @export_control This file is not subject to export control regulations.
 */

#ifndef CORE_IO_RECORDREADER_H
#define CORE_IO_RECORDREADER_H
// ...
#endif  // CORE_IO_RECORDREADER_H
```

**BAD**

```cpp
#ifndef RECORDREADER_H  // doesn't mirror the full path, not guaranteed unique
#define RECORDREADER_H
// ...
#endif
```

*The classification/Doxygen header shown here (UNCLASSIFIED, @file, @brief, @export_control) is the standard file header required on every tracked .h/.cpp file — see P3.1 for the full rule.*

**ENFORCEMENT**  clang-tidy llvm-header-guard, configured to require path-based naming (Manual MR checklist — no CI today).

## Namespaces, types, and functions

### C1.4 Namespaces

**RULE**  Lowercase, snake_case, nested to mirror directory structure.

**GOOD**

```cpp
namespace core::io
{
    // ...
}
```

**BAD**

```cpp
namespace Core::IO  // wrong casing
{
    // ...
}
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (NamespaceCase: lower_case) — Manual MR checklist.

### C1.5 Classes and structs

**RULE**  CamelCase (PascalCase), a noun or noun phrase.

**GOOD**

```cpp
class RecordReader { /* ... */ };
struct RecordBatch { /* ... */ };
```

**BAD**

```cpp
class record_reader { /* ... */ };  // wrong casing
struct record_batch { /* ... */ };  // wrong casing
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ClassCase/StructCase: CamelCase) — Manual MR checklist.

### C1.6 Enum class and enum members

**RULE**  enum class always (never a plain enum). Both the enum class name and its members are CamelCase.

**GOOD**

```cpp
enum class LogLevel : uint8_t
{
    Critical = 0,
    Error,
    Warning,
    Info
};
```

**BAD**

```cpp
enum LogLevel  // BAD -- plain enum, not scoped
{
    CRITICAL = 0,  // BAD -- wrong casing for this convention
    ERROR,
    WARNING,
    INFO
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (EnumCase/EnumConstantCase: CamelCase) — Manual MR checklist.

### C1.7 Free functions and public member functions

**RULE**  camelBack, a verb or verb phrase. No get prefix for a simple accessor (bare noun instead); set prefix is kept for setters, since it distinguishes a mutation from a query at the call site.

**GOOD**

```cpp
std::string normalizeName(const std::string& raw);

class RecordReader
{
public:
    std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);
    size_t recordCount() const;          // getter, no "get" prefix
    void setRecordLimit(size_t limit);   // setter keeps "set"
};
```

**BAD**

```cpp
std::string normalize_name(const std::string& raw);  // wrong casing

class RecordReader
{
public:
    size_t GetRecordCount() const;   // wrong casing, and unneeded "Get" prefix
    void RecordLimit(size_t limit);  // setter missing "set" -- reads like a getter
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (FunctionCase: camelBack) — Manual MR checklist.

## Variables and members

### C1.8 Local variables and function parameters

**RULE**  camelBack, descriptive, no type-encoding (no Hungarian notation), no cryptic abbreviation. Function parameters follow the exact same convention as local variables — no distinct marking to tell them apart.

**GOOD**

```cpp
int recordCount = 0;
std::string errorMessage;
void resizeBuffer(size_t newCapacity);
```

**BAD**

```cpp
int iCount = 0;  // type-encoded
std::string strErr;  // type-encoded, cryptic
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (VariableCase/ParameterCase: camelBack) — Manual MR checklist.

### C1.9 Member variables (private/protected)

**RULE**  camelBack, no m_ prefix, no trailing underscore — same casing as a local variable. Readability comes from scope (you're inside the class), not name decoration.

**RATIONALE**  Considered and rejected the m_ / trailing-underscore alternatives deliberately: they add a small amount of visual noise to every single member access in exchange for a distinction most readers can get from context (which function/class they're already reading). This choice has two direct consequences elsewhere: for boolean naming, see C1.10, and for parameters that would otherwise take the same name as the member they initialize, see 3.20.

**GOOD**

```cpp
class RecordReader
{
private:
    std::FILE* fileHandle;
};
```

**BAD**

```cpp
class RecordReader
{
private:
    std::FILE* m_fileHandle;  // BAD -- m_ prefix, rejected in favor of no decoration
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (MemberCase: camelBack) — Manual MR checklist.

### C1.10 Boolean naming, and the member/accessor collision

**RULE**  Free functions, member functions, and local variables that are or return a boolean use an is/has/should/can prefix so they read like a question at the call site. A private member variable backing a boolean accessor does NOT carry the prefix itself — only the public accessor does.

**RATIONALE**  Under the no-prefix member convention (C1.9), a member variable and a member function can't share a name in the same class — bool isOpen; and bool isOpen() const; is a compile error, not a style choice. Putting the prefix only on the accessor still delivers the actual readability payoff, since if (connection.isOpen()) at the call site is the only place this is ever read by someone outside the class.

**GOOD**

```cpp
class Connection
{
private:
    bool open;

public:
    bool isOpen() const;
};
```

**BAD**

```cpp
class Connection
{
private:
    bool isOpen;        // BAD — collides with the accessor below

public:
    bool isOpen() const;
};
```

**ENFORCEMENT**  Compiler enforces the collision itself; Advisory — code review for consistent application.

## Constants

### C1.11 Constants — class-level and namespace-level

**RULE**  UPPER_SNAKE_CASE.

**GOOD**

```cpp
namespace core::io
{
    constexpr size_t MAX_RECORD_COUNT = 100000;
}

class RecordReader
{
    static constexpr size_t DEFAULT_BATCH_SIZE = 1024;
};
```

**BAD**

```cpp
namespace core::io
{
    constexpr size_t maxRecordCount = 100000;  // BAD -- wrong casing for a real constant
}
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ConstantCase: UPPER_CASE, scoped to class/namespace level) — Manual MR checklist.

### C1.12 Constants — local (inside a function)

**RULE**  camelBack, same as a normal local variable — not UPPER_SNAKE_CASE.

**RATIONALE**  A local constant is lower-traffic and more like “a local variable that happens not to change” than a real project-wide constant. UPPER_SNAKE_CASE inside a function body tends to overstate its importance relative to everything around it.

**GOOD**

```cpp
void processRecords()
{
    constexpr size_t maxRetries = 3;
}
```

**BAD**

```cpp
void processRecords()
{
    constexpr size_t MAX_RETRIES = 3;  // BAD -- overstates a local's importance
}
```

**ENFORCEMENT**  Advisory — code review (clang-tidy's ConstantCase check does not distinguish local scope from class/namespace scope, so this specific rule isn't independently tool-enforceable without a scoped exception).

## Templates and macros

### C1.13 Template parameters

**RULE**  CamelCase, a single descriptive word where possible.

**GOOD**

```cpp
template<typename ElementType>
class Buffer
{
    // ...
};
```

**BAD**

```cpp
template<typename t>  // BAD -- wrong casing
class Buffer
{
    // ...
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (TemplateParameterCase: CamelCase) — Manual MR checklist.

### C1.14 Macros

**RULE**  UPPER_SNAKE_CASE, restricted to include guards only (language feature policy for macros generally is not yet covered).

**GOOD**

```cpp
#define CORE_IO_RECORDREADER_H
```

**BAD**

```cpp
#define core_io_recordreader_h  // BAD -- wrong casing
#define MAX_RETRIES 3  // BAD -- macro used outside an include guard
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (MacroCase: UPPER_CASE) — Manual MR checklist.

## Statics, aliases, and file extensions

### C1.15 Static member variables

**RULE**  Same casing as a normal member variable (C1.9) — camelBack, no distinct prefix (no s_) even though it's shared across all instances rather than per-instance.

**RATIONALE**  Consistent with the broader decision in C1.9 not to encode structural facts about a variable (member-ness, static-ness) into its name — the static keyword at the declaration site already says this.

**GOOD**

```cpp
class ConnectionPool
{
private:
    static int activeConnections;
};
```

**BAD**

```cpp
class ConnectionPool
{
private:
    static int s_activeConnections;  // BAD -- s_ prefix, inconsistent with C1.9
};
```

**ENFORCEMENT**  Advisory — code review.

### C1.16 Type aliases / using declarations

**RULE**  CamelCase, same as a class — consistent with the rule that CamelCase names anything that stands in for a type, since a using alias behaves exactly like a type everywhere it's used.

**GOOD**

```cpp
using RecordId = uint64_t;
using BatchCallback = std::function<void(const RecordBatch&)>;
```

**BAD**

```cpp
using record_id_t = uint64_t;  // inconsistent with class/type casing elsewhere
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (TypeAliasCase: CamelCase) — Manual MR checklist.

### C1.17 File extensions

**RULE**  .h / .cpp for everything, no exceptions — no .hpp for template-heavy or header-only code, no .cc in place of .cpp.

**RATIONALE**  Matches what's already used consistently throughout this document. A .hpp carve-out for templates is one more thing to remember for no real readability gain.

**GOOD**

```cpp
recordreader.h
recordreader.cpp
```

**BAD**

```cpp
recordreader.hpp  // BAD -- .hpp carve-out, adds a second rule to remember
recordreader.cc  // BAD -- inconsistent with the rest of the codebase
```

**ENFORCEMENT**  Advisory — code review.

## Interfaces, internal namespaces, and name collisions

### C1.18 Pure interfaces: I-prefix

**RULE**  A pure interface (all-abstract base class, per C3.1.4) is named with a leading I followed by CamelCase, e.g. IReadable, IWritable. This is the one deliberate exception to this document's general avoidance of decorative naming prefixes (compare C1.9's rejection of m_ on members) — it exists specifically to make “this type is a pure interface, not a concrete class” visible at every use site, not just at the class definition.

**RATIONALE**  Unlike a member variable (where the reader is already inside the class and has full context), a pure interface is referenced constantly from far-away call sites — function signatures, template parameters, inheritance lists — where the reader has no other cue that IReadable is an interface rather than a concrete type. The prefix earns its keep here in a way it didn't for member variables.

**GOOD**

```cpp
class IReadable
{
public:
    virtual ~IReadable() = default;
    virtual std::expected<RecordBatch, ReadError> read() = 0;
};
```

**BAD**

```cpp
class Readable { /* pure interface */ };  // BAD -- no I-prefix, looks like a concrete class
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ClassCase with a class-specific prefix rule for abstract classes) — Manual MR checklist.

### C1.19 Internal-only namespaces: detail

**RULE**  Implementation-only symbols that must be shared across multiple .h/.cpp files within a module, but are not part of that module's public interface, live in a nested detail namespace (e.g. core::io::detail) rather than the module's own namespace.

**RATIONALE**  detail is the established C++ convention for this (used throughout the standard library's own implementations and Boost), so it's immediately recognizable rather than a project-specific invention. It gives implementation helpers a real home when a single .cpp's anonymous namespace (C3.1) isn't enough — i.e. when the helper needs to be shared across more than one file within the module.

**GOOD**

```cpp
namespace core::io
{

namespace detail
{
    // implementation helpers, not part of core::io's public interface
}

class RecordReader { /* public interface, uses detail:: helpers internally */ };

}  // namespace core::io
```

**ENFORCEMENT**  Advisory — code review.

### C1.20 Parameter names versus member names

**RULE**  A function parameter is not required to carry the same name as the member it initializes or assigns, and where the two would otherwise be identical, the parameter is the side that changes — never the member. A renamed parameter must still denote the same value: name it for what it is inside the function, and let the function's own name supply the context the member name has to state explicitly. A parameter is never renamed to a name that denotes a different member, and never shortened to a placeholder that says nothing — C1.8 applies to it in full.

**RATIONALE**  There are two reasons, one mechanical and one about readability. Mechanically, C1.8 and C1.9 give parameters and members identical naming rules, so a constructor that stores the value it was handed produces a parameter that shadows the member it initializes. MSVC reports that as C4458 at /W4, which under this project's warnings-as-errors build is not a warning but a build failure — the naming rules as written describe code that does not compile. Note that `this->` does not fix this: the diagnostic fires at the parameter's declaration, not at the point of use, so qualifying the member inside the function body leaves the error exactly where it was.

The parameter is the side that changes because the member's name is read by every function in the class, while the parameter's name is read inside one. Letting a constructor dictate what a member is called for the rest of its life inverts that relationship for no gain.

On readability: a setter named setInputPath has already said which path it takes, so repeating that in the parameter adds nothing. The parameter is named from inside the function, where the surrounding context is established; the member is named from inside the class, where it has to distinguish itself from every sibling member. That is why `inputPath` is right for the member and `path` is right for the parameter, in the same class. The "denotes the same value" constraint is what stops this becoming licence to rename freely — a parameter called outputPath that assigns to inputPath is a worse problem than the shadow it avoided.

**GOOD**

```cpp
class RecordExporter
{
public:
    // Both parameters would collide with a member, so both are renamed -- to names
    // that still denote exactly the same values.
    RecordExporter(std::filesystem::path source, std::filesystem::path destination);

    // No collision: the function name already says which path this is, so the
    // parameter does not repeat it.
    void setInputPath(std::filesystem::path path);
    void setOutputPath(std::filesystem::path path);

private:
    std::filesystem::path inputPath;
    std::filesystem::path outputPath;
};
```

**BAD**

```cpp
class RecordExporter
{
public:
    RecordExporter(std::filesystem::path inputPath,         // BAD -- shadows the member it
                 std::filesystem::path outputPath);        // initializes; C4458, and a build
                                                           // failure under warnings-as-errors

    void setInputPath(std::filesystem::path p);            // BAD -- collision dodged by saying
                                                           // nothing at all; violates C1.8

    void setOutputPath(std::filesystem::path inputPath);   // BAD -- renamed to a name that
                                                           // denotes a different member
private:
    std::filesystem::path inputPath;
    std::filesystem::path outputPath;
};
```

**ENFORCEMENT**  Compiler (actual gate) for the collision itself — MSVC C4458, "declaration of 'x' hides class member," is emitted at /W4 and is an error under this project's warnings-as-errors build. GCC's -Wshadow reports the same declaration. Clang's plain -Wshadow does NOT — it deliberately exempts constructor parameters that shadow fields — so a future Clang toolchain needs -Wshadow-all, or specifically -Wshadow-field-in-constructor, to keep this gated. Whether a renamed parameter still denotes the same value is Advisory — code review.
