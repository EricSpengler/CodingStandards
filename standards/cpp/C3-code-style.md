# C3. Code Style

This project targets C++23, and follows a consistent, modern C++ style throughout — where a newer feature cleanly replaces an older idiom, this document prefers the modern one (concepts over SFINAE, for example) rather than carrying legacy patterns forward out of habit. See the separate References document for the guides this section draws from.

## C3.1 Language Feature Policy

### C3.1.1 Smart pointers vs raw pointers — ownership

**RULE**  std::unique_ptr is the default for any owning pointer. std::shared_ptr is used only when ownership is genuinely shared across multiple independent owners. Raw pointers are always non-owning — never used to express or transfer ownership.

**RATIONALE**  A raw pointer carries no information about who is responsible for freeing it — smart pointers make that ownership question part of the type itself, removing an entire category of leak/double-free bugs.

**GOOD**

```cpp
std::unique_ptr<RecordReader> reader;         // owns the RecordReader
std::shared_ptr<ConnectionPool> pool;       // genuinely shared across owners
RecordReader* activeReader;                   // non-owning reference only
```

**BAD**

```cpp
RecordReader* reader = new RecordReader(path);  // BAD -- raw owning pointer, unclear lifetime
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-owning-memory (Manual MR checklist).

### C3.1.2 No C-style casts

**RULE**  Named casts only — static_cast, dynamic_cast, const_cast, reinterpret_cast — matching whichever conversion is actually intended.

**RATIONALE**  A C-style cast can silently perform any of static/const/reinterpret conversion without telling the reader which one — a named cast makes the intent, and the risk, visible at the call site.

**GOOD**

```cpp
auto* dog = dynamic_cast<Dog*>(animal);
auto x = static_cast<float>(count) / 2.0f;
```

**BAD**

```cpp
auto x = (float)count / 2.0f;  // BAD -- C-style cast, doesn't say which conversion is intended
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-pro-type-cstyle-cast.

### C3.1.3 Macros

**RULE**  Banned except #ifndef include guards (naming C1.3, C1.14). No other use of the preprocessor for constants, inline-like functions, or conditional logic.

**RATIONALE**  Macros bypass the type system and scoping rules entirely, and their errors are notoriously hard to trace back to source — constexpr, templates, and inline functions cover every legitimate case a macro used to handle, with none of the downsides.

**GOOD**

```cpp
#ifndef CORE_IO_RECORDREADER_H
#define CORE_IO_RECORDREADER_H
```

**BAD**

```cpp
#define MAX_RETRIES 3  // BAD -- use constexpr instead
#define SQUARE(x) ((x) * (x))  // BAD -- use a function/template instead
```

**ENFORCEMENT**  Advisory — code review; a grep-based check for #define outside include guards is a good CI candidate later.

### C3.1.4 Multiple inheritance

**RULE**  Banned except pure interfaces — all-abstract base classes where every method is pure virtual and there are no data members, named per the I-prefix convention (naming C1.18).

**RATIONALE**  Multiple inheritance from stateful classes reintroduces the classic C++ diamond-inheritance and initialization-order problems. Pure interfaces sidestep this entirely, since there's no state to conflict.

**GOOD**

```cpp
class IReadable
{
public:
    virtual ~IReadable() = default;
    virtual std::expected<RecordBatch, ReadError> read() = 0;
};

class IWritable
{
public:
    virtual ~IWritable() = default;
    virtual void write(const RecordBatch& batch) = 0;
};

class RecordStore : public IReadable, public IWritable  // ok -- both pure interfaces
{
    // ...
};
```

**BAD**

```cpp
class RecordStore : public FileHandle, public LoggingMixin  // BAD -- neither base is a
{                                                         // pure interface (both have state)
    // ...
};
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.5 friend

**RULE**  Banned by default. When used, requires a one-line justification comment directly above the friend declaration explaining why the public interface can't accomplish the same thing.

**RATIONALE**  friend is a legitimate tool (operator overloads are the classic case) but an easy shortcut to reach for when the real fix is a more complete public interface. Requiring a written justification forces the author to either produce a real reason or realize there wasn't one.

**GOOD**

```cpp
class Matrix
{
    // Justification: operator* needs private element access for performance;
    // a public accessor would allow arbitrary mutation we don't want to expose.
    friend Matrix operator*(const Matrix& a, const Matrix& b);
};
```

**BAD**

```cpp
class Matrix
{
    friend Matrix operator*(const Matrix& a, const Matrix& b);  // BAD -- no justification comment
};
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.6 Template metaprogramming: concepts over SFINAE

**RULE**  Concepts/requires (C++20) are the required way to constrain a template. SFINAE-style enable_if tricks are banned for new code.

**RATIONALE**  SFINAE exploits a compiler quirk to constrain templates and is one of the least readable corners of pre-C++20 code — a reader has to already know the trick to parse it. Concepts express the exact same constraint in plain, readable syntax, with no reason to keep writing the old form now that C++23 is the target.

**GOOD**

```cpp
template<typename T>
requires std::integral<T>
T clamp(T value, T low, T high);
```

**BAD**

```cpp
template<typename T, typename = std::enable_if_t<std::is_integral_v<T>>>
T clamp(T value, T low, T high);  // BAD -- SFINAE trick, use concepts instead
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.7 auto usage

**RULE**  Use auto when the type is obvious from the right-hand side, or would otherwise be unreadably long (iterators, lambdas). Don't use it where it hides a type the reader actually needs to see to understand the code.

**RATIONALE**  auto reduces noise exactly where the type is redundant information, but hiding a genuinely load-bearing type (one that affects overflow behavior, signedness, or an API contract) trades a small typing savings for real ambiguity.

**GOOD**

```cpp
auto reader = std::make_unique<RecordReader>(path);   // type is obvious (ctor call)
auto it = records.begin();                          // iterator type is noise
```

**BAD**

```cpp
auto count = getCount();  // BAD if whether "count" is int vs size_t matters to the reader here
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.8 enum vs enum class

**RULE**  enum class always, matching naming C1.6 — listed here too since it's as much a language-feature rule as a naming one.

**GOOD**

```cpp
enum class LogLevel : uint8_t { Critical, Error, Warning, Info };
```

**BAD**

```cpp
enum LogLevel { Critical, Error, Warning, Info };  // BAD -- unscoped, implicitly converts to int
```

**ENFORCEMENT**  Advisory — code review (see naming C1.6 for the full rule).

### C3.1.9 Range-based for vs index/iterator loops

**RULE**  Range-based for by default. An index or iterator loop is used only when the index itself is needed for something beyond element access.

**GOOD**

```cpp
for (const auto& record : records) { /* ... */ }
```

**BAD**

```cpp
for (size_t i = 0; i < records.size(); ++i) { use(records[i]); }  // BAD -- index isn't needed, prefer range-for
```

**ENFORCEMENT**  clang-tidy modernize-loop-convert (Manual MR checklist).

### C3.1.10 Algorithms/ranges vs hand-rolled loops

**RULE**  Prefer a standard algorithm when it's at least as readable as the loop to someone unfamiliar with it, and when it avoids reimplementing something the standard library already provides correctly. Write the loop when in doubt, or when the algorithm would need a non-obvious lambda to express.

**RATIONALE**  There's no reason to hand-write logic the standard library already implements correctly and efficiently — but a clever one-liner that requires decoding a lambda isn't actually more readable than the loop it replaces, so this stays a judgment call rather than a blanket rule either way.

**GOOD**

```cpp
auto it = std::ranges::find(records, targetId, &Record::id);  // clear, and std::find already exists
```

**BAD**

```cpp
auto it = std::ranges::find_if(records, [&](const auto& r) {  // BAD -- nested lambda obscures
    return r.id() == targetId && r.status() == Status::Active;  // intent more than a loop would
});
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.11 Lambda captures: explicit only, no defaults

**RULE**  Lambda captures are always explicit — name each variable captured, by value or reference. Default captures ([=] or [&]) are never used.

**RATIONALE**  A default capture hides exactly what a lambda depends on, which is also the classic source of dangling-reference bugs when a [&]-captured lambda outlives the variables it references. Explicit captures make both the dependency and the lifetime risk visible at the point of capture.

**GOOD**

```cpp
auto callback = [&recordCount, &errorList](const Record& r) { /* ... */ };
```

**BAD**

```cpp
auto callback = [&](const Record& r) { /* ... */ };  // BAD -- default capture, unclear what's actually captured
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-avoid-capturing-lambda-coroutines catches one related case; explicit-vs-default capture style is otherwise Advisory — code review.

### C3.1.12 const-correctness

**RULE**  Member functions that don't mutate object state are marked const. Parameters passed by reference that aren't modified are const&. Local variables that are never reassigned are const.

**RATIONALE**  const-correctness documents intent directly in the type system — a const member function is a promise the compiler enforces, not just a comment a reader has to trust.

**GOOD**

```cpp
class RecordReader
{
public:
    size_t recordCount() const;                     // const member function
    void processBatch(const RecordBatch& batch);    // const& parameter
};
const size_t maxRetries = 3;                         // const local
```

**BAD**

```cpp
size_t recordCount();  // BAD -- doesn't mutate state, should be const
```

**ENFORCEMENT**  clang-tidy misc-const-correctness (Manual MR checklist).

### C3.1.13 nullptr, never NULL or 0

**RULE**  nullptr is used for every null pointer value.

**RATIONALE**  nullptr is a real, typed null-pointer value; NULL and 0 are integer literals that happen to convert, which can cause overload-resolution ambiguity nullptr doesn't have.

**GOOD**

```cpp
RecordReader* reader = nullptr;
```

**BAD**

```cpp
RecordReader* reader = NULL;  // BAD
RecordReader* reader = 0;     // BAD
```

**ENFORCEMENT**  clang-tidy modernize-use-nullptr.

### C3.1.14 Explicit constructors

**RULE**  Any constructor callable with a single argument is marked explicit, unless implicit conversion is specifically and deliberately desired.

**RATIONALE**  An implicit single-argument constructor lets a raw value silently convert to the class type anywhere a function expects it — explicit forces the conversion to be written out, catching accidental type confusion at compile time.

**GOOD**

```cpp
class RecordId
{
public:
    explicit RecordId(uint64_t value);   // explicit -- prevents accidental implicit conversion
};

class Meters
{
public:
    Meters(double value);   // NOT explicit -- implicit conversion from double is intentional,
                            // e.g. so `Meters distance = 5.0;` reads naturally
};
```

**BAD**

```cpp
class RecordId { public: RecordId(uint64_t value); };  // BAD -- allows silent implicit conversion, e.g. passing a raw uint64_t where a RecordId was expected
```

**ENFORCEMENT**  clang-tidy google-explicit-constructor (Manual MR checklist).

### C3.1.15 override and final

**RULE**  override is required on every virtual override, with no exceptions. final is used when a class or method is deliberately closed to further derivation or overriding.

**RATIONALE**  override makes the compiler verify the function actually overrides something, catching the common bug where a typo'd signature silently creates a new, unrelated function instead of overriding the intended one.

**GOOD**

```cpp
class RecordWriter final : public IWritable   // final -- no further derivation allowed
{
public:
    void write(const RecordBatch& batch) override;
};
```

**BAD**

```cpp
void write(const RecordBatch& batch);  // BAD -- overrides IWritable::write but doesn't say so
```

**ENFORCEMENT**  clang-tidy modernize-use-override.

### C3.1.16 noexcept: required on move operations and swap only

**RULE**  noexcept is required on move constructors, move assignment operators, and swap — the cases where the standard library changes real behavior based on the promise (e.g. std::vector uses moves instead of copies during reallocation only if the move is noexcept). It is not required, and not applied as a matter of habit, anywhere else.

**RATIONALE**  noexcept genuinely earns its cost on move/swap because the standard library's behavior changes based on the promise; everywhere else it's only documentation, with a real downside: if a noexcept function later gains code that can throw, the program calls std::terminate() immediately instead of propagating the exception — a much harder failure to debug. Keeping the rule narrow avoids scattering that footgun through the codebase.

**GOOD**

```cpp
Buffer(Buffer&& other) noexcept;
Buffer& operator=(Buffer&& other) noexcept;
void swap(Buffer& other) noexcept;
```

**BAD**

```cpp
void processRecord(const Record& r) noexcept;  // BAD -- no real payoff here, and if this ever gains a throwing call, it becomes a std::terminate() footgun
```

**ENFORCEMENT**  clang-tidy performance-noexcept-move-constructor (Manual MR checklist).

### C3.1.17 No trailing return types

**RULE**  Traditional return-type-first syntax is used for all functions. Trailing return type (auto foo() -> ReturnType) is not used. In the rare template case where the return type depends on a parameter declared later in the signature, prefer plain auto with the return type deduced from the function body instead of introducing a trailing return type.

**RATIONALE**  Trailing return type only exists to solve a narrow template problem that, in this codebase's style (templates fully defined inline, deduced auto available), essentially never comes up in practice — so there's no reason to introduce a second way to write a function signature.

**GOOD**

```cpp
RecordBatch readBatch(const std::string& name);
template<typename T, typename U>
auto add(T a, U b) { return a + b; }  // deduced from the body, no trailing return type needed
```

**BAD**

```cpp
auto readBatch(const std::string& name) -> RecordBatch;  // BAD -- trailing return type with no reason to need it
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.18 std::string_view for read-only string parameters

**RULE**  A function parameter that only reads a string (never stores it beyond the call, never needs a stable owned copy) takes std::string_view instead of const std::string&. A function that needs to keep the string beyond its own scope (store it in a member, pass it to another thread, etc.) still takes an owned std::string, since string_view doesn't own its data and can dangle.

**RATIONALE**  const std::string& still requires the caller to have (or construct) an actual std::string, which can force an unnecessary allocation when the caller only has a string literal or a substring view. std::string_view accepts any of those without copying, since it's just a non-owning view over existing character data — but that non-ownership is exactly why it's unsafe to store beyond the call it was passed into.

**GOOD**

```cpp
void logMessage(std::string_view message);   // read-only, used and discarded within the call

class RecordReader
{
public:
    explicit RecordReader(std::string initialPath);   // parameter renamed per C1.20; BAD example
                                                    // below shows why this stays std::string
private:
    std::string path;   // stored beyond the constructor call -- needs to own the data
};
```

**BAD**

```cpp
void logMessage(const std::string& message);  // BAD -- forces a std::string to exist/allocate even when the caller only has a string literal or substring
```

**ENFORCEMENT**  clang-tidy performance-unnecessary-value-param / modernize-pass-by-value related checks flag some cases; the read-only-vs-stored distinction itself is Advisory — code review.

### C3.1.19 Internal linkage: anonymous namespace, not static

**RULE**  A function or variable that's local to a single .cpp file (not declared in any header) is given internal linkage via an anonymous namespace, not the static keyword.

**RATIONALE**  static works for a single function or variable, but not for a type, and using two different mechanisms (static for some things, anonymous namespace for others) depending on what's being hidden is one more thing to remember. An anonymous namespace covers every case — functions, variables, and types — with one consistent mechanism.

**GOOD**

```cpp
// recordreader.cpp
namespace
{
    constexpr size_t kChunkSize = 4096;

    bool isRecoverable(ReadError error)
    {
        return error != ReadError::FileNotFound;
    }
}  // namespace
```

**BAD**

```cpp
// recordreader.cpp
static constexpr size_t kChunkSize = 4096;         // BAD -- static, not anonymous namespace
static bool isRecoverable(ReadError error) { /* ... */ }  // BAD -- same issue
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.20 size_t/unsigned for sizes and counts; never mix signed and unsigned in one expression

**RULE**  size_t and other unsigned types remain the default for sizes, counts, and indices, matching what the standard library itself returns (container .size(), etc.) — this codebase does not require signed types for sizes/indices, given the ergonomic cost of casting at every standard-library boundary. However, signed and unsigned values are never compared or combined in arithmetic within the same expression without an explicit, deliberate cast.

**RATIONALE**  Mixing signed and unsigned in a comparison or arithmetic expression silently converts the signed value to unsigned first, which can turn a small negative number into a huge positive one — a classic, hard-to-spot C++ bug (the canonical case is a loop like for (size_t i = count - 1; i >= 0; --i), which never terminates because an unsigned i can never be negative). Requiring signed types everywhere would eliminate this entirely, but at the cost of casting constantly against a standard library that returns size_t everywhere — so this codebase takes the narrower fix (never mix the two types in one expression) rather than banning unsigned types outright.

**GOOD**

```cpp
size_t count = records.size();
if (count > 0) { /* ... */ }              // unsigned-to-unsigned, fine

int delta = -3;
if (delta < 0 && static_cast<size_t>(-delta) <= count) { /* ... */ }  // explicit cast, deliberate
```

**BAD**

```cpp
int delta = -1;
size_t count = records.size();
if (delta < count) { /* BAD -- delta is silently converted to a huge unsigned
                        number; this is false even though -1 < 5 looks obviously true */ }
```

**ENFORCEMENT**  Compiler warning (-Wsign-compare / -Wsign-conversion on GCC/Clang, /W4's C4018/C4245 on MSVC) is the real gate once warnings-as-errors is configured — that belongs to the not-yet-built Toolchain/Build Specifics topic on the master list, so this isn't wired up as an actual gate yet. Advisory — code review in the meantime.

### C3.1.21 Pre-increment (++X), not post-increment (X++), when the returned value isn't used

**RULE**  Use pre-increment/decrement (++x, --x) rather than post-increment/decrement (x++, x--) whenever the expression's own value isn't used by the surrounding statement — loop counters and iterator advancement being the common case. Post-increment is only used when the old value is specifically what's needed.

**RATIONALE**  Post-increment has to produce a copy of the pre-increment value to return, even when nothing uses it. For a plain int the compiler trivially optimizes that copy away, but for an iterator or any type with a non-trivial copy constructor, that copy can be a real, measurable cost the optimizer doesn't always eliminate. Pre-increment is never worse and is sometimes meaningfully better, so it's the default everywhere the returned value isn't actually needed.

**GOOD**

```cpp
for (size_t i = 0; i < count; ++i) { /* ... */ }
++it;

int a = ++x;   // a gets the NEW value -- fine, the return value is actually used and needed
```

**BAD**

```cpp
for (size_t i = 0; i < count; i++) { /* ... */ }  // BAD -- return value discarded, no reason for post-increment
it++;                                              // BAD -- same issue
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.22 No using namespace — explicit namespace prefixes always

**RULE**  using namespace std; and any other using namespace X; directive are never used, in headers or .cpp files. Every identifier from another namespace is written out with its full qualification (std::string, core::io::RecordReader, etc.) at every use.

**RATIONALE**  A using namespace directive in a header pollutes the namespace of every file that includes it, creating name clashes that are hard to trace back to their source. Even confined to a single .cpp file, it makes it unclear at a glance which namespace an identifier actually comes from — explicit prefixes keep that always visible at the point of use, and this codebase applies the same rule everywhere rather than relaxing it for .cpp files specifically.

**GOOD**

```cpp
std::string name;
std::vector<Record> records;
core::io::RecordReader reader(path);
```

**BAD**

```cpp
using namespace std;  // BAD -- never used, in headers or .cpp files
string name;           // BAD -- relies on the banned using-namespace directive above
```

**ENFORCEMENT**  clang-tidy google-build-using-namespace (Manual MR checklist).

### C3.1.23 Virtual destructor required on any polymorphic base class

**RULE**  Any class with at least one virtual function, and that might be deleted through a pointer to that base class, has a virtual destructor.

**RATIONALE**  Deleting a derived object through a base-class pointer with a non-virtual destructor skips the derived destructor entirely — undefined behavior, and in practice a resource leak (any RAII members the derived class owns never get cleaned up). This is directly why every pure interface in this document (C3.1.4) declares its destructor virtual.

**GOOD**

```cpp
class IReadable
{
public:
    virtual ~IReadable() = default;   // virtual -- required
    virtual std::expected<RecordBatch, ReadError> read() = 0;
};
```

**BAD**

```cpp
class IReadable
{
public:
    ~IReadable() = default;   // BAD -- not virtual
    virtual std::expected<RecordBatch, ReadError> read() = 0;
};

std::unique_ptr<IReadable> reader = std::make_unique<RecordReader>(path);
// deleting reader here only runs ~IReadable(), never ~RecordReader() -- undefined behavior
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-virtual-class-destructor.

### C3.1.24 No virtual function calls from constructors or destructors

**RULE**  A constructor or destructor never calls a virtual function on *this, directly or indirectly.

**RATIONALE**  During construction, an object's vtable isn't fully set up for its most-derived type yet — a virtual call from a base class constructor always resolves to the base class's own version, never a derived override, even when constructing a derived object. The same applies in reverse during destruction. This is one of the more surprising C++ behaviors for anyone coming from a language without this restriction, and it fails silently (no compiler error, just the wrong function running).

**BAD**

```cpp
class Base
{
public:
    Base() { init(); }   // BAD -- calls a virtual function during construction
    virtual void init() { /* ... */ }
};

class Derived : public Base
{
public:
    void init() override { /* this override is NEVER called from Base's constructor */ }
};
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.25 No object slicing — pass polymorphic types by reference or pointer, never by value

**RULE**  A polymorphic type (anything with virtual functions) is never passed, returned, or stored by value where a base-class type is used to hold a potentially-derived object. Use a reference, pointer, or smart pointer instead.

**RATIONALE**  Copying a derived object into a base-class-by-value variable or parameter only copies the base-class portion — the derived-specific data and overridden behavior are silently discarded (“sliced off”). The result still compiles and runs, just not as the derived type it was supposed to be, which makes this bug easy to miss until it produces wrong behavior far from where the actual mistake was made.

**GOOD**

```cpp
void process(const IReadable& reader);   // reference -- no slicing
void process(std::unique_ptr<IReadable> reader);   // or ownership transfer via smart pointer
```

**BAD**

```cpp
void process(IReadable reader);   // BAD -- IReadable is polymorphic; passing by value
                                   // slices away everything the derived type added

RecordReader concrete(path);
process(concrete);   // only the IReadable part of concrete is copied in
```

**ENFORCEMENT**  Advisory — code review.

### C3.1.26 Self-assignment must not corrupt the object

**RULE**  A hand-written copy assignment operator must produce a correct result when the source and target are the same object (a = a;).

**RATIONALE**  a = a; must remain a valid, safe operation. A naive assignment operator that releases its own resources before copying from the source will corrupt itself in the self-assignment case, since source and target are the same object — it ends up reading from a resource it just released. This applies to every kind of resource, not just heap memory — a wrapped C API handle (C3.4.4) has exactly the same failure, and since C3.4.1 rules out raw owning memory in first-party code, a handle is the form this actually takes here. This ties directly to the Rule of Five (C3.4.2): any hand-written assignment operator needs this guard.

**GOOD**

```cpp
FileHandle& operator=(const FileHandle& other)
{
    if (this == &other) return *this;   // self-assignment guard

    closeStream(stream);
    stream = duplicateStream(other.stream);
    return *this;
}
```

**BAD**

```cpp
FileHandle& operator=(const FileHandle& other)
{
    closeStream(stream);                        // BAD -- if other is *this, this closes the
    stream = duplicateStream(other.stream);     // very stream being duplicated on the next
    return *this;                               // line -- use-after-close
}
```

**ENFORCEMENT**  clang-tidy bugprone-unhandled-self-assignment.

## C3.2 Complexity & Readability Limits

### C3.2.1 Max function length: 60 lines

**RULE**  A function body, excluding braces and blank lines, does not exceed 60 lines.

**RATIONALE**  Past roughly 60 lines, a function is very likely doing more than one job and should be split — a blunt but effective signal, since almost nothing that's genuinely simple runs that long.

**ENFORCEMENT**  clang-tidy readability-function-size (LineThreshold: 60).

### C3.2.2 Max cyclomatic complexity: 10

**RULE**  Cyclomatic complexity — the count of independent paths through a function, starting at 1 and incrementing for every if/else if/while/for/case/&&/|| — does not exceed 10 for any function.

**RATIONALE**  Cyclomatic complexity is a direct, measurable predictor of how many test cases a function needs to be thoroughly covered — a function with complexity 20 needs 20+ tests just to exercise every branch, which is exactly the kind of function that tends to hide bugs.

**GOOD**

```cpp
void processRecord(const Record& r)
{
    if (r.isValid())            // +1
    {
        if (r.hasData())        // +1
        {
            // complexity so far: 3 (1 base + 2 decisions) -- well within budget
        }
    }
}
```

**ENFORCEMENT**  clang-tidy readability-function-size (BranchThreshold: 10) plus readability-function-cognitive-complexity (Threshold: 25), together — Manual MR checklist. Note that neither check measures McCabe cyclomatic complexity directly; there is no clang-tidy check that does. See Appendix C for what the two actually measure, how closely the pair approximates a ceiling of 10, and the open item this leaves.

### C3.2.3 Max nesting depth: 3, use guard clauses

**RULE**  Nesting depth does not exceed 3 levels. When a function would otherwise nest deeper, restructure using early-return guard clauses for invalid/edge cases at the top of the function.

**RATIONALE**  Guard clauses handle the “get out early” cases up front and leave the main logic flat and immediately visible, instead of squeezed to the right under conditions the reader has to mentally hold open.

**GOOD**

```cpp
void processRecord(const Record& r)
{
    if (!r.isValid()) return;   // guard clause, keeps nesting shallow
    if (r.isEmpty()) return;
    // main logic, unindented
}
```

**BAD**

```cpp
void processRecord(const Record& r)
{
    if (r.isValid())
    {
        if (!r.isEmpty())
        {
            // BAD -- the actual logic is buried 2 levels deep
        }
    }
}
```

**ENFORCEMENT**  clang-tidy readability-function-size (NestingThreshold: 3).

### C3.2.4 Max function parameters: 5, then pass a struct

**RULE**  A function takes at most 5 parameters. Beyond that, group related parameters into a struct.

**RATIONALE**  Beyond a handful of parameters, call sites become error-prone (easy to swap two same-typed arguments) and hard to read at a glance — a named struct makes each value self-documenting at the call site.

**GOOD**

```cpp
struct ReaderOptions
{
    size_t batchSize;
    bool strictMode;
    std::optional<size_t> maxRecords;
};
void configureReader(const ReaderOptions& options);
```

**BAD**

```cpp
void configureReader(size_t batchSize, bool strictMode, size_t maxRecords, bool skipInvalid, bool logErrors, size_t retryCount);  // BAD -- 6 params, easy to pass in the wrong order
```

**ENFORCEMENT**  clang-tidy readability-function-size (ParameterThreshold: 5).

### C3.2.5 Max file length: 1000 lines (advisory)

**RULE**  A file should not exceed 1000 lines. Beyond that, split the class or namespace it contains.

**ENFORCEMENT**  Advisory — code review.

### C3.2.6 Single responsibility: for classes and functions alike

**RULE**  A class or function should have one job. If a class name needs “and” to describe it accurately (e.g. ReaderAndValidator), or a function does multiple unrelated things (e.g. validateAndSave()), that's a signal to split it.

**RATIONALE**  A function or class doing multiple unrelated jobs adds bloat and forces every caller to accept both responsibilities even when they only need one. This is inherently a judgment call with no mechanical check — the “and” naming smell is a useful heuristic, not a hard rule.

**GOOD**

```cpp
void validate(const Record& r);
void save(const Record& r);  // called separately by whoever needs both
```

**BAD**

```cpp
void validateAndSave(const Record& r);  // BAD -- two unrelated jobs bundled into one function
```

**ENFORCEMENT**  Advisory — code review.

## C3.3 Error Handling Strategy

### C3.3.1 Exceptions for programming errors, std::expected for recoverable failures

**RULE**  Throw an exception when a function is called with arguments that violate a documented precondition or invariant, or when the program reaches a state that should be impossible if the rest of the codebase is correct — including constructor validation for classes with invariants (C3.4.5). Use std::expected<T, E> when a function's failure is a normal, anticipated outcome the caller is expected to handle explicitly — file I/O, parsing untrusted input, network calls, user-facing validation.

**RATIONALE**  Exceptions unwind the stack automatically and can't be silently ignored, which matters most exactly when the program has already reached an impossible state. std::expected keeps genuinely normal, anticipated failures visible in the type system without paying the cost of an exception for something that isn't exceptional.

**GOOD**

```cpp
class RecordBatch
{
public:
    explicit RecordBatch(size_t count)
    {
        if (count == 0)
        {
            throw std::invalid_argument("RecordBatch requires count > 0");  // programming error
        }
    }
};

std::expected<RecordBatch, ParseError> parseCsvFile(const std::filesystem::path& path);  // expected failure, see C3.3.4 for [[nodiscard]]
```

**ENFORCEMENT**  Advisory — code review.

### C3.3.2 No error codes or bool success flags, anywhere, with no exceptions

**RULE**  First-party code never returns an int/bool status code communicated via an out-parameter or errno-style global — zero exceptions to this, including the boundary layer that wraps any third-party C-style API (a compression, database, graphics, or file-format library, for example). That wrapper layer's entire job is to convert the underlying library's error convention into std::expected or an exception right at the boundary, before anything else in the codebase ever sees it — the wrapper does not inherit or forward the C API's own convention.

**RATIONALE**  Boolean/int status codes are the easiest error-handling mechanism to silently ignore. Allowing them inside a wrapper “because the underlying library uses them” would just relocate the ambiguity this rule exists to remove — the conversion has to happen exactly at the boundary, not be deferred past it.

**GOOD**

```cpp
[[nodiscard]] std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);  // see C3.3.4
```

**BAD**

```cpp
bool tryReadBatch(RecordBatch& out);  // BAD -- error-code style, banned even inside a wrapper layer
```

**ENFORCEMENT**  Advisory — code review.

### C3.3.3 assert() only for invariant checks in identified hot paths

**RULE**  assert() is permitted only for invariant checks inside identified hot paths — code that runs many times per second in a tight loop (a render loop, the inner loop of large batch processing) — and only for a condition that would otherwise be routed to an exception under C3.3.1, where paying that cost every iteration is measurably expensive. A hot path must be identified by profiling, not by feel. Everywhere else, invariant violations are exceptions, per C3.3.1, with no assert() carve-out.

**RATIONALE**  assert() is compiled out entirely in release builds, so it's genuinely free at runtime — but that also means it silently disappears in production if misused as a general validation tool. Scoping it strictly to profiling-justified hot paths keeps it from becoming a way to skip real error handling anywhere a dev feels like it's “just a debug check.”

**GOOD**

```cpp
// Hot path, identified by profiling: called per-vertex in the render loop.
void transformVertex(Vertex& v, const Matrix& m)
{
    assert(m.isValid() && "transform matrix must be valid");
    // ...
}
```

**BAD**

```cpp
void setBatchSize(size_t size)  // BAD -- not a hot path, should throw per C3.3.1
{
    assert(size > 0 && "batch size must be positive");
}
```

**ENFORCEMENT**  Advisory — code review; reviewer should ask for the profiling justification when assert() appears.

### C3.3.4 [[nodiscard]] on every function returning std::expected

**RULE**  Every function that returns std::expected<T, E> is marked [[nodiscard]], with no exceptions.

**RATIONALE**  Without [[nodiscard]], nothing stops a caller from invoking the function and discarding the returned std::expected entirely — silently ignoring a possible failure with no compiler warning. This directly undermines the whole point of C3.3.1's split: std::expected only keeps failures visible in the type system if something actually forces the caller to look at the return value.

**GOOD**

```cpp
[[nodiscard]] std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);
```

**BAD**

```cpp
std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);  // BAD -- missing [[nodiscard]], caller can silently drop the error
```

**ENFORCEMENT**  Compiler warning (real gate, [[nodiscard]] is a language feature enforced by every compiler) once applied; Advisory — code review to confirm it's applied everywhere it should be.

## C3.4 Memory Management & Ownership

### C3.4.1 No manual memory management

**RULE**  new, delete, malloc, and free never appear in first-party code. Use stack-allocated variables and RAII wrappers (smart pointers, containers) exclusively.

**RATIONALE**  It's easy to forget a delete on an early-return or exception path; it's impossible to forget to release a stack-owned resource.

**GOOD**

```cpp
auto reader = std::make_unique<RecordReader>(path);
```

**BAD**

```cpp
RecordReader* reader = new RecordReader(path);  // BAD
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-no-malloc, cppcoreguidelines-owning-memory.

### C3.4.2 Rule of five, explicit

**RULE**  If a class declares a custom destructor, it must also explicitly declare (or explicitly = default / = delete) the copy constructor, copy assignment, move constructor, and move assignment operators.

**RATIONALE**  The compiler-generated copy/move operations are frequently wrong once a custom destructor exists — leaving them implicit is a latent double-free or slicing bug waiting for someone to trigger it.

**GOOD**

```cpp
class RecordReader
{
public:
    ~RecordReader();
    RecordReader(const RecordReader&) = delete;
    RecordReader& operator=(const RecordReader&) = delete;
    RecordReader(RecordReader&&) noexcept;
    RecordReader& operator=(RecordReader&&) noexcept;
};
```

**BAD**

```cpp
class RecordReader { public: ~RecordReader(); };  // BAD -- compiler-generated copy/move left implicit, likely wrong once the class owns a resource
```

**ENFORCEMENT**  clang-tidy cppcoreguidelines-special-member-functions.

### C3.4.3 Passing ownership: unique_ptr by value; non-owning by pointer or reference

**RULE**  Ownership is transferred by passing a std::unique_ptr by value. Non-owning access is expressed with a raw pointer or reference — never a raw owning pointer.

**RATIONALE**  A raw pointer parameter is ambiguous about ownership transfer; std::unique_ptr by value makes the transfer explicit and compiler-checked (the caller can't accidentally keep using it afterward).

**GOOD**

```cpp
void takeOwnership(std::unique_ptr<RecordReader> reader);
void useReader(const RecordReader& reader);
```

**BAD**

```cpp
void takeOwnership(RecordReader* reader);  // BAD -- unclear whether this takes ownership or just uses it
```

**ENFORCEMENT**  Advisory — code review.

### C3.4.4 RAII for every resource, not just heap memory

**RULE**  Every resource that must be explicitly acquired and released — file handles, locks, network/database connections, handles from a wrapped C API — is wrapped in an RAII type whose constructor acquires it and whose destructor releases it. Nothing is manually released.

**RATIONALE**  Manual acquire/release pairs are exactly as fragile as manual new/delete (C3.4.1), just for a different kind of resource — an exception or early return between acquire and release leaves the resource held forever. RAII guarantees the release runs via the destructor, regardless of how the scope is exited.

**GOOD**

```cpp
{
    std::lock_guard<std::mutex> lock(bufferMutex);   // constructor locks
    doSomething();                               // if this throws...
}                                                 // ...destructor still runs, unlocking automatically
```

**BAD**

```cpp
mutex_.lock();
doSomething();       // BAD -- if this throws or returns early, unlock() never runs
mutex_.unlock();
```

**ENFORCEMENT**  Advisory — code review.

### C3.4.5 struct vs class: presence of any function beyond data

**RULE**  struct is for a pure container of variables — no member functions beyond perhaps an aggregate initializer. The moment a type has any member function, it's a class.

**RATIONALE**  This is a deliberately simpler, mechanically-checkable version of the more common “struct for no-invariant data, class when an invariant must be protected” rule — every invariant-protecting type necessarily has a constructor with logic, so this rule is a safe subset of that reasoning: it can never misclassify a type that needs protecting as a struct, it only occasionally classifies a function-only, no-invariant type (e.g. a Point with a distanceFromOrigin() query method) as a class when it strictly didn't need to be, which is a safe direction to err in.

**GOOD**

```cpp
struct RecordBatch       // pure data, no functions
{
    std::vector<Record> records;
    size_t batchId;
};

class RecordReader          // has functions (and an invariant the constructor protects)
{
    // ...
};
```

**ENFORCEMENT**  Advisory — code review.

## C3.5 Formatting

### C3.5.1 Brace style: Allman

**RULE**  Opening braces go on their own new line, for every block — functions, control statements, classes.

**GOOD**

```cpp
void readBatch()
{
    if (isValid)
    {
        // ...
    }
}
```

**BAD**

```cpp
void readBatch() {  // BAD -- K&R style, not Allman
    if (isValid) {
    }
}
```

**ENFORCEMENT**  clang-format (BreakBeforeBraces: Allman).

### C3.5.2 Indentation: 4 spaces, never tabs

**RULE**  4 spaces per indentation level. Tabs are never committed.

**ENFORCEMENT**  clang-format (IndentWidth: 4, UseTab: Never).

### C3.5.3 Column limit: 100

**RULE**  Lines wrap at 100 columns.

**ENFORCEMENT**  clang-format (ColumnLimit: 100).

### C3.5.4 Pointer/reference alignment: left

**RULE**  The * or & binds to the type, not the variable name.

**GOOD**

```cpp
int* pointer;
const std::string& name;
```

**BAD**

```cpp
int *pointer;  // BAD
```

**ENFORCEMENT**  clang-format (PointerAlignment: Left).

### C3.5.5 Access modifiers: flush with the class keyword, no indent

**RULE**  public:/private:/protected: are flush with the class declaration's indentation — not indented an extra level.

**RATIONALE**  Access modifiers act more like section dividers within the class than genuine nested scope — keeping them flush avoids an extra visual nesting level for no real benefit, consistent with this document's general preference for flat, low-nesting code (C3.2.3).

**GOOD**

```cpp
class RecordReader
{
public:
    void readBatch();
private:
    std::FILE* fileHandle;
};
```

**BAD**

```cpp
class RecordReader
{
    public:  // BAD -- indented, adds a nesting level with no readability payoff
        void readBatch();
};
```

**ENFORCEMENT**  clang-format (AccessModifierOffset: -4, IndentAccessModifiers: false).

### C3.5.6 Space before parens in control statements

**RULE**  A space always separates a control keyword from its parenthesis: if (x), never if(x).

**GOOD**

```cpp
if (isValid) { /* ... */ }
```

**BAD**

```cpp
if(isValid) { }  // BAD
```

**ENFORCEMENT**  clang-format (SpaceBeforeParens: ControlStatements).

### C3.5.7 Single-line function bodies: trivial getters/setters only

**RULE**  Only a trivial inline getter/setter may collapse to one line. Every other function body spans multiple lines regardless of how short its content is — the same multi-line-always principle already applied to Doxygen blocks (C2.3).

**GOOD**

```cpp
size_t recordCount() const { return count; }  // ok -- trivial getter
```

**BAD**

```cpp
bool isValid() const { if (!ptr) return false; return ptr->check(); }  // BAD -- not trivial, must be multi-line
```

**ENFORCEMENT**  clang-format (AllowShortFunctionsOnASingleLine: InlineOnly); Advisory — code review for the “trivial” judgment call.

### C3.5.8 Include order: own header, first-party, third-party, C system + standard library

**RULE**  A .cpp file's #includes are grouped and ordered: (1) the matching header for this file (e.g. recordreader.cpp includes recordreader.h first), (2) this project's other first-party headers, (3) third-party library headers, whichever the project depends on (see C-32), (4) C system headers and C++ standard library headers, combined into one group. Each group is separated by a blank line and alphabetized within itself.

**RATIONALE**  Putting the file's own matching header first is what actually proves that header is self-contained — if recordreader.h secretly depends on something included earlier in recordreader.cpp, including it first is what makes that compile failure show up immediately, rather than being masked by whatever happened to be included before it. The remaining three groups reflect this codebase's existing convention (own header, first-party, third-party, then system/stdlib combined), rather than importing a different split from elsewhere.

**GOOD**

```cpp
// recordreader.cpp
#include "recordreader.h"                     // 1: own header first

#include "core/io/record_batch.h"           // 2: first-party (alphabetical)
#include "gui/docking/dock_manager.h"

#include <dataformat/reader.h>               // 3: third-party (alphabetical, case-insensitive)
#include <GuiToolkit/Window.h>

#include <optional>                          // 4: C system + standard library, combined (alphabetical)
#include <string>
#include <unistd.h>
```

**BAD**

```cpp
// recordreader.cpp
#include <string>                            // BAD -- own header should come first, not stdlib
#include "recordreader.h"
#include <dataformat/reader.h>               // BAD -- third-party before first-party
#include "core/io/record_batch.h"
```

**ENFORCEMENT**  clang-format (IncludeBlocks: Regroup, SortIncludes: CaseInsensitive, IncludeCategories — see Appendix B). The CaseInsensitive setting matters for the alphabetization claim above: clang-format's default ASCII sort would place every capitalised third-party header ahead of every lowercase one, which is not what the example shows.

### C3.5.9 Member order: public/protected/private, then types → constants → factory functions → constructors → assignment operators → destructor → other methods → data members

**RULE**  A class's access-level blocks appear in the order public, then protected, then private — each access level as one contiguous block, never scattered (e.g. two separate public: sections with something else between them). Within each access-level block, declarations follow this order: types (nested typedefs/using/structs/classes), constants, factory functions, constructors, assignment operators, destructor, all other methods, data members. Within any one of those 8 groups — e.g. among the “other methods” — declarations are NOT required to be alphabetical; group related declarations together instead. For data members specifically, declaration order follows initialization dependencies, not alphabetical order or grouping — C++ always initializes members in declaration order regardless of constructor initializer-list order, so a member that depends on another member already being initialized must be declared after it.

**RATIONALE**  A conventional, predictable member order means a reader always knows roughly where to look for a constructor vs. a data member, without having to scan the whole class first.

**GOOD**

```cpp
class RecordReader
{
public:
    using RecordCallback = std::function<void(const RecordBatch&)>;   // 1: types

    static constexpr size_t DEFAULT_BATCH_SIZE = 1024;                // 2: constants

    static RecordReader open(const std::filesystem::path& path);        // 3: factory function

    explicit RecordReader(const std::filesystem::path& path);           // 4: constructors
    RecordReader(RecordReader&&) noexcept;
    RecordReader& operator=(RecordReader&&) noexcept;                     // 5: assignment operators
    ~RecordReader();                                                     // 6: destructor

    std::expected<RecordBatch, ReadError> readBatch(const std::string& sectionName);  // 7: other methods
    size_t recordCount() const;

private:
    std::FILE* fileHandle;                                                  // 8: data members
};
```

**BAD**

```cpp
class RecordReader
{
public:
    std::FILE* fileHandle;                    // BAD -- data member before constructors/methods
    explicit RecordReader(const std::filesystem::path& path);
private:
    void logError(const std::string& msg);
public:                                  // BAD -- a second public: block, scattered from the first
    size_t recordCount() const;
};
```

**ENFORCEMENT**  Advisory — code review; a custom clang-tidy check could enforce ordering later if this becomes a recurring review comment.
