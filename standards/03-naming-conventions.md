# 3. Naming Conventions

Every naming decision below was worked through as its own question rather than inherited wholesale from an existing style guide — several (member variable prefixing, boolean naming, local constant casing) had genuine tradeoffs worth deciding deliberately, not defaulting on.

#### 3.1 Version-like tokens fuse with the following word

**RULE**  A version-like or product-derived token (hdf5, h5, zlib, etc.) is treated as a single fused word rather than getting its own underscore-separated segment, in any snake_case or SCREAMING_SNAKE_CASE context — directory names, file names, include guards, namespaces.

**RATIONALE**  This is a general rule specifically because it was caught as an inconsistency during review — a directory/file name and its own include guard disagreeing on this point is exactly the kind of ambiguity a junior dev would copy inconsistently without a stated rule to follow.

**GOOD**

```cpp
hdf5reader.h
CORE_IO_HDF5READER_H
```

**BAD**

```cpp
hdf5_reader.h  // inconsistent with the fused form used elsewhere
CORE_IO_HDF5_READER_H
```

**ENFORCEMENT**  Advisory — code review.

#### 3.2 Directory and file names

**RULE**  Lowercase, snake_case, applying the fusion rule above. File names match the primary class they define.

**GOOD**

```cpp
core/io/hdf5reader/
hdf5reader.h
hdf5reader.cpp
```

**BAD**

```cpp
core/io/HDF5Reader/  // wrong casing
Hdf5Reader.h  // wrong casing, and doesn't match the class-name-only rule if the file held multiple classes
```

**ENFORCEMENT**  Advisory — code review.

#### 3.3 Include guards

**RULE**  SCREAMING_SNAKE_CASE, mirroring the full path exactly (including the fusion rule above), for guaranteed uniqueness across the tree.

**GOOD**

```cpp
// UNCLASSIFIED

/**
 * @file hdf5reader.h
 * @brief RAII wrapper around HDF5 file access for core.
 * @export_control This file is not subject to export control regulations.
 */

#ifndef CORE_IO_HDF5READER_H
#define CORE_IO_HDF5READER_H
// ...
#endif  // CORE_IO_HDF5READER_H
```

**BAD**

```cpp
#ifndef HDF5READER_H  // doesn't mirror the full path, not guaranteed unique
#define HDF5READER_H
// ...
#endif
```

*The classification/Doxygen header shown here (UNCLASSIFIED, @file, @brief, @export_control) is the standard file header required on every tracked .h/.cpp file — see 4.1 for the full rule.*

**ENFORCEMENT**  clang-tidy llvm-header-guard, configured to require path-based naming (Manual PR checklist — no CI today).

#### 3.4 Namespaces

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

**ENFORCEMENT**  clang-tidy readability-identifier-naming (NamespaceCase: lower_case) — Manual PR checklist.

#### 3.5 Classes and structs

**RULE**  CamelCase (PascalCase), a noun or noun phrase.

**GOOD**

```cpp
class Hdf5Reader { /* ... */ };
struct RecordBatch { /* ... */ };
```

**BAD**

```cpp
class hdf5_reader { /* ... */ };  // wrong casing
struct record_batch { /* ... */ };  // wrong casing
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ClassCase/StructCase: CamelCase) — Manual PR checklist.

#### 3.6 Enum class and enum members

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

**ENFORCEMENT**  clang-tidy readability-identifier-naming (EnumCase/EnumConstantCase: CamelCase) — Manual PR checklist.

#### 3.7 Free functions and public member functions

**RULE**  camelBack, a verb or verb phrase. No get prefix for a simple accessor (bare noun instead); set prefix is kept for setters, since it distinguishes a mutation from a query at the call site.

**GOOD**

```cpp
std::string normalizeName(const std::string& raw);

class Hdf5Reader
{
public:
    std::expected<RecordBatch, Hdf5Error> readBatch(const std::string& datasetName);
    size_t recordCount() const;          // getter, no "get" prefix
    void setRecordLimit(size_t limit);   // setter keeps "set"
};
```

**BAD**

```cpp
std::string normalize_name(const std::string& raw);  // wrong casing

class Hdf5Reader
{
public:
    size_t GetRecordCount() const;   // wrong casing, and unneeded "Get" prefix
    void RecordLimit(size_t limit);  // setter missing "set" -- reads like a getter
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (FunctionCase: camelBack) — Manual PR checklist.

#### 3.8 Local variables and function parameters

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

**ENFORCEMENT**  clang-tidy readability-identifier-naming (VariableCase/ParameterCase: camelBack) — Manual PR checklist.

#### 3.9 Member variables (private/protected)

**RULE**  camelBack, no m_ prefix, no trailing underscore — same casing as a local variable. Readability comes from scope (you're inside the class), not name decoration.

**RATIONALE**  Considered and rejected the m_ / trailing-underscore alternatives deliberately: they add a small amount of visual noise to every single member access in exchange for a distinction most readers can get from context (which function/class they're already reading). This choice has a direct consequence for boolean naming — see 3.10.

**GOOD**

```cpp
class Hdf5Reader
{
private:
    hid_t fileHandle;
};
```

**BAD**

```cpp
class Hdf5Reader
{
private:
    hid_t m_fileHandle;  // BAD -- m_ prefix, rejected in favor of no decoration
};
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (MemberCase: camelBack) — Manual PR checklist.

#### 3.10 Boolean naming, and the member/accessor collision

**RULE**  Free functions, member functions, and local variables that are or return a boolean use an is/has/should/can prefix so they read like a question at the call site. A private member variable backing a boolean accessor does NOT carry the prefix itself — only the public accessor does.

**RATIONALE**  Under the no-prefix member convention (3.9), a member variable and a member function can't share a name in the same class — bool isOpen; and bool isOpen() const; is a compile error, not a style choice. Putting the prefix only on the accessor still delivers the actual readability payoff, since if (connection.isOpen()) at the call site is the only place this is ever read by someone outside the class.

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

#### 3.11 Constants — class-level and namespace-level

**RULE**  UPPER_SNAKE_CASE.

**GOOD**

```cpp
namespace core::io
{
    constexpr size_t MAX_RECORD_COUNT = 100000;
}

class Hdf5Reader
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

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ConstantCase: UPPER_CASE, scoped to class/namespace level) — Manual PR checklist.

#### 3.12 Constants — local (inside a function)

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

#### 3.13 Template parameters

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

**ENFORCEMENT**  clang-tidy readability-identifier-naming (TemplateParameterCase: CamelCase) — Manual PR checklist.

#### 3.14 Macros

**RULE**  UPPER_SNAKE_CASE, restricted to include guards only (language feature policy for macros generally is not yet covered).

**GOOD**

```cpp
#define CORE_IO_HDF5READER_H
```

**BAD**

```cpp
#define core_io_hdf5reader_h  // BAD -- wrong casing
#define MAX_RETRIES 3  // BAD -- macro used outside an include guard
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (MacroCase: UPPER_CASE) — Manual PR checklist.

#### 3.15 Static member variables

**RULE**  Same casing as a normal member variable (3.9) — camelBack, no distinct prefix (no s_) even though it's shared across all instances rather than per-instance.

**RATIONALE**  Consistent with the broader decision in 3.9 not to encode structural facts about a variable (member-ness, static-ness) into its name — the static keyword at the declaration site already says this.

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
    static int s_activeConnections;  // BAD -- s_ prefix, inconsistent with 3.9
};
```

**ENFORCEMENT**  Advisory — code review.

#### 3.16 Type aliases / using declarations

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

**ENFORCEMENT**  clang-tidy readability-identifier-naming (TypeAliasCase: CamelCase) — Manual PR checklist.

#### 3.17 File extensions

**RULE**  .h / .cpp for everything, no exceptions — no .hpp for template-heavy or header-only code, no .cc in place of .cpp.

**RATIONALE**  Matches what's already used consistently throughout this document. A .hpp carve-out for templates is one more thing to remember for no real readability gain.

**GOOD**

```cpp
hdf5reader.h
hdf5reader.cpp
```

**BAD**

```cpp
hdf5reader.hpp  // BAD -- .hpp carve-out, adds a second rule to remember
hdf5reader.cc  // BAD -- inconsistent with the rest of the codebase
```

**ENFORCEMENT**  Advisory — code review.

#### 3.18 Pure interfaces: I-prefix

**RULE**  A pure interface (all-abstract base class, per 6.1.4) is named with a leading I followed by CamelCase, e.g. IReadable, IWritable. This is the one deliberate exception to this document's general avoidance of decorative naming prefixes (compare 3.9's rejection of m_ on members) — it exists specifically to make “this type is a pure interface, not a concrete class” visible at every use site, not just at the class definition.

**RATIONALE**  Unlike a member variable (where the reader is already inside the class and has full context), a pure interface is referenced constantly from far-away call sites — function signatures, template parameters, inheritance lists — where the reader has no other cue that IReadable is an interface rather than a concrete type. The prefix earns its keep here in a way it didn't for member variables.

**GOOD**

```cpp
class IReadable
{
public:
    virtual ~IReadable() = default;
    virtual std::expected<RecordBatch, Hdf5Error> read() = 0;
};
```

**BAD**

```cpp
class Readable { /* pure interface */ };  // BAD -- no I-prefix, looks like a concrete class
```

**ENFORCEMENT**  clang-tidy readability-identifier-naming (ClassCase with a class-specific prefix rule for abstract classes) — Manual PR checklist.

#### 3.19 Internal-only namespaces: detail

**RULE**  Implementation-only symbols that must be shared across multiple .h/.cpp files within a module, but are not part of that module's public interface, live in a nested detail namespace (e.g. core::io::detail) rather than the module's own namespace.

**RATIONALE**  detail is the established C++ convention for this (used throughout the standard library's own implementations and Boost), so it's immediately recognizable rather than a project-specific invention. It gives implementation helpers a real home when a single .cpp's anonymous namespace (6.1) isn't enough — i.e. when the helper needs to be shared across more than one file within the module.

**GOOD**

```cpp
namespace core::io
{

namespace detail
{
    // implementation helpers, not part of core::io's public interface
}

class Hdf5Reader { /* public interface, uses detail:: helpers internally */ };

}  // namespace core::io
```

**ENFORCEMENT**  Advisory — code review.

#### 3.20 Exception classes take an Exception suffix; std::expected error enums take an Error suffix

**RULE**  A class thrown as an exception is named `<Context>Exception` — InvalidRecordException, Hdf5OpenException. An enum used as the E in std::expected<T, E> is named `<Context>Error` — Hdf5Error, ParseError. The two suffixes are never mixed: there is no RecordError that gets thrown, and no ParseException enum. Both follow the ordinary CamelCase type rule (3.5, 3.6); the suffix is the only addition.

**RATIONALE**  The error-handling split in 6.3.1 is the single most important thing a reader needs to know about a failure type: does this unwind the stack, or is it a value I have to check? Encoding that split in the suffix means the answer is visible at every use site — a signature returning std::expected<RecordBatch, Hdf5Error> and a throw Hdf5OpenException(...) are distinguishable without looking up either type. This is the same reasoning that earned the I-prefix its exception in 3.18: the distinction matters at far-away call sites, not just at the definition. Picking Exception for the thrown side rather than Error also avoids colliding with the ...Error enums this codebase already uses heavily (Hdf5Error appears throughout Sections 5 and 6), which is what makes the rule mechanically unambiguous rather than a coin flip between two equally good suffixes.

**GOOD**

```cpp
/**
 * @brief Thrown when a record violates a documented precondition.
 */
class InvalidRecordException : public std::runtime_error
{
public:
    explicit InvalidRecordException(const std::string& message);
};

/**
 * @brief Reason an HDF5 read did not produce a batch.
 */
enum class Hdf5Error : uint8_t
{
    // enumerators documented per 5.5
};

[[nodiscard]] std::expected<RecordBatch, Hdf5Error> readBatch(std::string_view datasetName);
```

**BAD**

```cpp
class InvalidRecordError : public std::runtime_error { /* ... */ };  // BAD -- Error suffix on a
                                                                      // thrown type; reads like an
                                                                      // std::expected error enum

enum class ParseException : uint8_t { /* ... */ };  // BAD -- Exception suffix on an enum that is
                                                     // returned, never thrown

class InvalidRecord : public std::runtime_error { /* ... */ };  // BAD -- no suffix at all; nothing
                                                                 // at the throw site says this is
                                                                 // an exception type
```

**ENFORCEMENT**  Advisory — code review. clang-tidy's readability-identifier-naming can enforce a suffix on classes derived from a common base (ClassSuffix scoped to a custom base) but cannot tell a thrown type from a returned one on its own, so the thrown-vs-returned half of this rule stays a review judgment.
