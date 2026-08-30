# C2. Documentation (Doxygen)

Documentation coverage isn't limited to the public API surface — private and protected members are documented just as thoroughly as public ones, since understanding the implementation matters for onboarding, maintenance, and code review, not just for calling into a public interface.

## Comment style and coverage

### C2.1 Comment style: /** ... */ Javadoc-style, matching the file header

**RULE**  All Doxygen documentation blocks use /** ... */, consistent with the @file/@brief/@export_control header already established in P3. No /// triple-slash style.

**GOOD**

```cpp
/**
 * @brief Opens the given file for reading.
 */
```

**BAD**

```cpp
/// Opens the given file for reading.  // BAD -- wrong comment style
```

**ENFORCEMENT**  Doxygen build warns on non-conforming comment styles it can't parse as documentation; otherwise Advisory — code review.

### C2.2 Scope: every function, variable, class, struct, and namespace — regardless of access level

**RULE**  Every free function, every member function (public, protected, AND private), every member variable, every namespace/global-scope variable or constant, every class/struct, and every namespace gets a Doxygen comment. Function-local variables are excluded (C1.8/C1.12 already cover their naming; they don't get Doxygen blocks).

**RATIONALE**  Documenting every access level, not just the public surface, is what makes the codebase understandable end-to-end — a private helper function is exactly the kind of thing that needs explaining, arguably more than a well-named public method whose signature already communicates most of its own intent.

**ENFORCEMENT**  Doxygen build with EXTRACT_ALL=NO, EXTRACT_PRIVATE=YES, WARN_IF_UNDOCUMENTED=YES (see Appendix A) surfaces every undocumented entity at build time. Manual MR checklist today (reviewer runs the Doxygen build during the manual build step, P1.8) — CI gate once available (the Enforcement Summary, known gap).

## Required tags

### C2.3 Required tags: @brief, @param, and @return on everything (@return omitted only for void); @throws when a function can throw

**RULE**  @brief is mandatory on every documented entity, even a short description for a trivial private member. @brief is written in third-person descriptive form with an implied subject of “This function/class/etc.” — e.g. “Reads the section” or “Opens the file,” not imperative mood (“Read the section,” “Open the file”). @param is mandatory for every parameter, with no exception for names that seem self-explanatory — same full-coverage principle as C2.2/5.5. @return is mandatory for every function with a non-void return type; a void function omits @return entirely, since there's no value to describe. @throws is required whenever a function can throw. Every Doxygen block spans multiple lines — opening /**, content, closing */ — never collapsed onto a single line, regardless of how short the content is.

**RATIONALE**  Requiring @brief, @param, and @return everywhere (rather than leaving them to judgment) keeps coverage total and mechanical to check, consistent with the full-coverage principle already applied in C2.2 and C2.5 — no entity is skipped because it “seemed obvious.” Void is the one genuine structural exception, not a judgment call: there's no return value to describe, so @return would either be omitted or say something meaningless. The multi-line-always rule keeps every Doxygen block visually consistent regardless of content length, so a reader scanning code doesn't have to parse two different block shapes. The verb-tense rule removes a small but real inconsistency — without it, some @brief lines read as commands and others as descriptions, which is a needless variation once a whole codebase's worth of comments are read together.

**GOOD**

```cpp
/**
 * @brief Reads one record batch from the currently open file.
 * @param sectionName Name of the section to read.
 * @return The parsed batch, or an ReadError if the read fails.
 */
std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);

/**
 * @brief Closes the currently open file handle.
 * @param force If true, closes even if pending writes have not been flushed.
 */
void close(bool force);  // void -- no @return, nothing to describe

/**
 * @brief Number of records currently buffered.
 */
size_t bufferedCount;
```

**BAD**

```cpp
/**
 * @brief Reads one record batch.  // BAD -- missing @param and @return entirely
 */
std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);

/**
 * @brief Close the currently open file handle.  // BAD -- imperative mood, should be "Closes"
 * @param force If true, closes even if pending writes have not been flushed.
 * @return None.  // BAD -- void function, nothing to document; omit @return entirely
 */
void close(bool force);
```

**ENFORCEMENT**  Doxygen WARN_IF_UNDOCUMENTED / WARN_NO_PARAMDOC catches missing @brief and @param; missing @return on a non-void function, verb tense, and single-line blocks are Advisory — code review.

#### C2.3.1 Documenting std::expected<T, E>: @return covers both outcomes, error detail lives on the enum

**RULE**  @return on a function returning std::expected<T, E> describes both the success and failure outcomes in one sentence. It does not itemize each specific error value with @retval — the meaning of each individual error (e.g. each ReadError enumerator) is documented once, on the error enum's own definition, per C2.5's full-coverage requirement for enum members.

**RATIONALE**  Itemizing every error value with @retval in every function that can return it creates the same duplicate-documentation problem C2.6 already solved for declaration-vs-definition — if there are 20 functions returning ReadError, that block gets copy-pasted 20 times, and updating one error's meaning means finding and fixing all 20. Keeping error-value detail on the enum itself (already mandated by C2.5) gives it exactly one home.

**GOOD**

```cpp
/**
 * @brief Reads one record batch from the currently open file.
 * @param sectionName Name of the section to read.
 * @return The parsed batch on success, or an ReadError describing why the read failed.
 */
[[nodiscard]] std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);
```

**BAD**

```cpp
/**
 * @brief Reads one record batch from the currently open file.
 * @param sectionName Name of the section to read.
 * @return The parsed batch, or an ReadError if the read fails.
 * @retval ReadError::FileNotFound The named section does not exist.        // BAD -- duplicates
 * @retval ReadError::InvalidFormat The section format is wrong.      // documentation that
 * @retval ReadError::ReadFailure A read error occurred.              // belongs on the enum
 */
[[nodiscard]] std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);
```

**ENFORCEMENT**  Advisory — code review.

#### C2.3.2 @tparam for every template parameter

**RULE**  A template class or function documents each of its template parameters with @tparam, positioned right after @brief and before @param. Coverage is total — every template parameter gets one, same full-coverage principle as everywhere else in this section.

**GOOD**

```cpp
/**
 * @brief Fixed-capacity buffer for a single element type.
 * @tparam ElementType Type of element stored in the buffer.
 */
template<typename ElementType>
class Buffer
{
    // ...
};

/**
 * @brief Clamps a value to the given inclusive range.
 * @tparam T Integral type being clamped.
 * @param value Value to clamp.
 * @param low Lower bound, inclusive.
 * @param high Upper bound, inclusive.
 * @return The clamped value.
 */
template<typename T>
requires std::integral<T>
T clamp(T value, T low, T high);
```

**BAD**

```cpp
/**
 * @brief Fixed-capacity buffer for a single element type.  // BAD -- missing @tparam for ElementType
 */
template<typename ElementType>
class Buffer
{
    // ...
};
```

**ENFORCEMENT**  Doxygen WARN_IF_UNDOCUMENTED (Manual MR checklist).

## Placement and special cases

### C2.4 Namespaces are documented once, in a dedicated doc-only header

**RULE**  Each namespace gets exactly one Doxygen block, using the @namespace command, living in a dedicated file — docs/namespaces.h in this project, per C-31 — that contains nothing but namespace documentation — no actual code. Namespaces are never documented inline at the point they're opened in an ordinary header, since a namespace is typically reopened across many files and there'd be no single obvious place to put its one canonical description.

**RATIONALE**  A namespace is reopened in dozens of files; documenting it inline in “whichever header happened to be first” is exactly the kind of ambiguity this document exists to remove. A dedicated doc-only file makes it mechanical: one namespace, one block, one obvious location to look. It's still a tracked .h file, so it carries the same file header as any other (P3.1).

**GOOD**

```cpp
// UNCLASSIFIED

/**
 * @file namespaces.h
 * @brief Doxygen-only namespace documentation; contains no code, never #included.
 * @export_control This file is not subject to export control regulations.
 */

/**
 * @namespace core::io
 * @brief File I/O and format-specific readers and writers for core.
 */
```

**ENFORCEMENT**  Advisory — code review; Doxygen will warn if a namespace has no @namespace documentation anywhere in the project.

### C2.5 Enum documentation: @brief on the enum class, and on every enumerator

**RULE**  The enum class itself gets a standard multi-line @brief block above it. Every enumerator also gets its own multi-line block above it — never an inline single-line trailing comment — with no exception for enumerators whose name might seem self-explanatory. This follows the same full-coverage requirement as C2.2 and the same multi-line-always convention as everywhere else in this document.

**RATIONALE**  Skipping enumerators whose name “seems obvious” is exactly the kind of judgment call C2.2's full-coverage rule exists to remove — what counts as obvious to the author isn't necessarily obvious to a new dev six months later, and a partially-documented enum leaves a reader unsure whether the missing docs were a deliberate choice or an oversight.

**GOOD**

```cpp
/**
 * @brief Severity level for a log entry.
 */
enum class LogLevel : uint8_t
{
    /**
     * @brief Unrecoverable; the application cannot continue.
     */
    Critical = 0,

    /**
     * @brief Recoverable, but the current operation failed.
     */
    Error,

    /**
     * @brief Non-fatal issue worth surfacing to the user or log.
     */
    Warning,

    /**
     * @brief Informational message with no actionable severity.
     */
    Info
};
```

**BAD**

```cpp
/** @brief Severity level for a log entry. */  // BAD -- single-line block
enum class LogLevel : uint8_t
{
    Critical = 0,  /**< Unrecoverable */  // BAD -- inline single-line comment
    Error,         // BAD -- undocumented
    Warning,       // BAD -- undocumented, even though the name seems obvious
    Info           // BAD -- undocumented
};
```

**ENFORCEMENT**  Doxygen WARN_IF_UNDOCUMENTED catches missing enumerator docs the same as any other entity (C2.2); Advisory — code review for the multi-line formatting.

### C2.6 Documentation lives at the declaration, not the definition

**RULE**  For anything with a separate declaration and definition (a member or free function declared in a .h and defined in the matching .cpp, an out-of-line static member, etc.), the Doxygen block goes on the declaration only. The definition carries no Doxygen block — a plain // comment there is fine if something implementation-specific needs explaining, but @brief/@param/@return/etc. are never repeated. If something is declared and defined in the same place (an inline function in a header, a function-local to one .cpp with no header declaration), the documentation goes wherever that single declaration+definition is.

**RATIONALE**  Documenting both the declaration and the definition creates two sources of truth that can silently drift out of sync as the function changes — the declaration is what a reader consults first (it's what the header/interface shows), so that's the one canonical place.

**GOOD**

```cpp
// recordreader.h
/**
 * @brief Reads one record batch from the currently open file.
 * @param sectionName Name of the section to read.
 * @return The parsed batch, or an ReadError if the read fails.
 */
std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);

// recordreader.cpp
std::expected<RecordBatch, ReadError> RecordReader::readBatch(const std::string& sectionName)
{
    // implementation notes, if any, as a plain comment -- no Doxygen block here
}
```

**BAD**

```cpp
// recordreader.cpp
/**
 * @brief Reads one record batch from the currently open file.  // BAD -- duplicated
 * @param sectionName Name of the section to read.            // from the header,
 * @return The parsed batch, or an ReadError if the read fails.    // now two sources of truth
 */
std::expected<RecordBatch, ReadError> RecordReader::readBatch(const std::string& sectionName)
{
    // ...
}
```

**ENFORCEMENT**  Advisory — code review.
