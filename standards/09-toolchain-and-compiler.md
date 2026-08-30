# 9. Toolchain & Compiler Configuration

One thing has to be said plainly before any rule in this section: **MSVC on Windows is the only toolchain this project actually builds with today.** A Linux build and a GCC/Clang toolchain were discussed and explicitly deferred (see the master topic list), and the manual review process (1.8) notes the same thing about its build step. Every portability rule below is therefore written as a *forward* constraint — code is written so that adding the second toolchain later is a build-configuration task rather than a source-rewriting one — not as a claim that both toolchains are exercised now. Where a rule cannot be verified today, it says so.

## 9.1 Language standard

#### 9.1.1 C++23, standard mode, no compiler extensions

**RULE**  The standard is set once in the root CMakeLists.txt with `CMAKE_CXX_STANDARD 23`, `CMAKE_CXX_STANDARD_REQUIRED ON`, and `CMAKE_CXX_EXTENSIONS OFF`. Compiler-specific language extensions are never used in first-party code: no `__declspec` outside a generated export header, no `#pragma once` in place of the include guards required by 3.3, no GNU statement expressions, no variable-length arrays.

**RATIONALE**  `CMAKE_CXX_STANDARD_REQUIRED ON` is the half people forget: without it, CMake treats the standard as a preference and silently falls back to whatever the compiler supports, so a toolchain without full C++23 produces a confusing cascade of errors about `std::expected` rather than one clear message about the standard. `CMAKE_CXX_EXTENSIONS OFF` selects `/std:c++23` and `-std=c++23` over `-std=gnu++23`, which is what makes "no extensions" a compiler-enforced fact rather than a review item — an extension that never compiles is an extension nobody has to remember not to use.

**GOOD**

```cpp
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
```

**BAD**

```cpp
set(CMAKE_CXX_STANDARD 23)    # BAD -- without STANDARD_REQUIRED this is only a request;
                              # a toolchain lacking C++23 silently builds as C++20
```

**ENFORCEMENT**  Compiler (actual gate) for the extension prohibition, once `CMAKE_CXX_EXTENSIONS OFF` is set. Advisory — code review for `#pragma once` and `__declspec`.

#### 9.1.2 C++23 feature subset: adopted, permitted, and deferred

**RULE**  Not every C++23 feature is available in practice, because "C++23" means different things to MSVC and to GCC's libstdc++. Features fall in three buckets, and moving one between buckets is an amendment to this rule.

**Adopted** — used freely, and preferred over the older idiom they replace:
- `std::expected` (the basis of the entire error-handling strategy in 6.3)
- `if consteval`, `auto(x)` decay-copy
- Deducing `this` (explicit object parameters), where it removes a const/non-const overload pair
- `std::print` / `std::println` — for test and diagnostic output only, never for user-facing output (Section 14) or logging (Section 13)
- `[[assume]]`, subject to the same profiling requirement `assert()` carries in 6.3.3

**Permitted** — fine to use, no preference either way: multidimensional `operator[]`, `static operator()`, literal suffixes for `size_t`, `std::to_underlying`, `std::byteswap`, `std::unreachable`, extended floating-point conversions.

**Deferred** — not used in first-party code today, revisit when the second toolchain lands:
- **C++20/23 modules.** The build is `#include`-based (6.5.8) and stays that way. Module support differs sharply between MSVC and GCC and interacts badly with CMake's dependency scanning at the version floor in 8.4.2.
- **`std::flat_map` / `std::flat_set`, `std::mdspan`, `std::generator`, `std::stacktrace`.** Library support is uneven across the two standard libraries; each is worth revisiting individually once both toolchains are actually built.
- **Coroutines.** Not deferred for support reasons but for architectural ones — see 15.1, which settles the concurrency model without them.

**RATIONALE**  A blanket "we target C++23" invites a developer to reach for a feature that compiles fine on MSVC today and blocks the Linux port entirely a year from now, at which point it is spread through the codebase and expensive to remove. Naming the deferred features explicitly turns that from a discovery made during the port into a decision made now. The `std::print` carve-out matters because it is genuinely the right tool for a test failure message and genuinely the wrong tool for anything a user reads, which Sections 13 and 14 route elsewhere.

**GOOD**

```cpp
[[nodiscard]] std::expected<RecordBatch, Hdf5Error> readBatch(std::string_view datasetName);

std::println("parsed {} records in {} ms", recordCount, elapsedMs);   // test diagnostic only
```

**BAD**

```cpp
import std;   // BAD -- modules are deferred; this build is #include-based (6.5.8)

std::flat_map<RecordId, Record> index;   // BAD -- deferred pending both toolchains

std::println("Could not open {}", path);  // BAD -- user-facing output; see Section 14
```

*Open item, needs team ratification: the three buckets above are a proposal built from what MSVC and libstdc++ each support at the time of writing, not a decision the team has made. The deferred list is the half worth arguing about — in particular, whether `std::flat_map` and `std::stacktrace` are worth their portability cost, since `std::stacktrace` would materially improve crash reporting (Section 21).*

**ENFORCEMENT**  Advisory — code review. Genuinely unverifiable until a second toolchain exists, which is the point: this rule is what keeps the eventual port cheap.

## 9.2 Warnings

#### 9.2.1 Warning flags are set once, per-compiler, in one cmake/ module

**RULE**  Warning flags live in a single `cmake/CrnaWarnings.cmake` module that defines one function, `crna_set_warnings(<target>)`, which selects the flag list by compiler and applies it `PRIVATE` to the named target. Every first-party target calls it exactly once. No warning flag is ever set anywhere else — not in `CMAKE_CXX_FLAGS`, not in a preset, not inline in a target's own CMakeLists.txt.

**RATIONALE**  Warning configuration is the single most-copied block in most CMake projects, and every copy drifts: one target gets a flag the others do not, nobody knows which list is authoritative, and disabling a noisy warning means finding all the copies. One function with one definition makes "what warnings do we build with" a question with exactly one answer. `PRIVATE` is essential — warning flags must not propagate to consumers, because a consumer of `core` should be judged by its own warning policy, not by `core`'s.

**GOOD**

```cpp
# cmake/CrnaWarnings.cmake
function(crna_set_warnings target_name)
    if(MSVC)
        target_compile_options(${target_name} PRIVATE
            /W4             # high warning level, short of the very noisy /Wall
            /permissive-    # conformance mode -- rejects MSVC-specific laxness
            /utf-8          # source and execution charset both UTF-8 (see 22.2)
            /Zc:__cplusplus # report the real __cplusplus value, not 199711L
            /Zc:preprocessor
            /w14242 /w14254 /w14263 /w14265 /w14287   # narrowing, hidden virtuals, slicing
            /w14296 /w14311 /w14545 /w14546 /w14547
            /w14549 /w14555 /w14619 /w14640 /w14826
            /w14905 /w14906 /w14928
        )
    else()
        target_compile_options(${target_name} PRIVATE
            -Wall -Wextra -Wpedantic
            -Wshadow                # 6.1.19-adjacent: a shadowed name is almost always a bug
            -Wnon-virtual-dtor      # 6.1.23
            -Wold-style-cast        # 6.1.2
            -Woverloaded-virtual    # 6.1.15
            -Wsign-conversion       # 6.1.20 -- this is the real gate that rule names
            -Wsign-compare          # 6.1.20
            -Wconversion
            -Wdouble-promotion
            -Wnull-dereference
            -Wformat=2
        )
    endif()
endfunction()

# core/CMakeLists.txt
crna_set_warnings(core)
```

**BAD**

```cpp
# core/CMakeLists.txt
target_compile_options(core PRIVATE /W4)   # BAD -- flags set inline; gui and app now differ
                                            # from core and nobody notices

target_compile_options(core PUBLIC /W4)    # BAD -- PUBLIC propagates the warning policy to
                                            # every consumer
```

**ENFORCEMENT**  Advisory — code review; the single-definition property is what makes it easy to check.

*Note: 6.1.20's ENFORCEMENT line states that its signed/unsigned rule is not wired up as an actual gate because the warning flags "belong to the not-yet-built Toolchain/Build Specifics topic." That is this rule. With `-Wsign-conversion`/`-Wsign-compare` above and warnings-as-errors below, 6.1.20 becomes a real compiler-enforced gate on the GCC/Clang side, and `/W4` covers C4018/C4245 on MSVC. Section 7's row for 6.1.20 is updated accordingly.*

#### 9.2.2 Warnings are errors on first-party targets, and only on first-party targets

**RULE**  `crna_set_warnings` also sets warnings-as-errors — `/WX` on MSVC, `-Werror` on GCC/Clang — for `core`, `gui`, `app`, and the test targets. Third-party code never builds with warnings-as-errors. A warning that must be suppressed is suppressed at the narrowest possible scope with a comment naming what it is and why, never by removing the flag from the list in 9.2.1.

**RATIONALE**  A warning nobody is forced to clear accumulates until the build output is a wall of text people scroll past, at which point a genuinely new warning is indistinguishable from the existing noise and the entire warning system has stopped working. Making them errors keeps the count at zero, which is the only count at which "is there a new warning" is answerable at a glance. Excluding third-party code is not a loophole but a necessity: warnings in code you cannot fix will block your build on someone else's schedule, and that pressure is what eventually gets `-Werror` removed entirely.

**GOOD**

```cpp
# in crna_set_warnings, alongside the flag lists above
if(MSVC)
    target_compile_options(${target_name} PRIVATE /WX)
else()
    target_compile_options(${target_name} PRIVATE -Werror)
endif()
```

**BAD**

```cpp
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /WX")   # BAD -- global (8.2.1); this hits third-party
                                                 # code compiled in the same tree too
```

*Open item, needs team ratification: turning `/WX` on against an existing codebase produces however many errors the codebase currently has, all at once. If that number is large, the realistic path is to enable it per-target — `core` first, since it is the smallest and most portable — rather than everywhere at once. Decide which at review; the rule as written assumes all four targets at once.*

**ENFORCEMENT**  Compiler (actual gate) once applied.

#### 9.2.3 Third-party headers are included as SYSTEM

**RULE**  Every third-party dependency's headers reach first-party code as system includes, so warnings originating inside them are suppressed. With imported targets from `find_package` (8.3.2) this is usually automatic; where it is not, the dependency is linked through a wrapper interface target that marks its includes `SYSTEM`.

**RATIONALE**  This is what makes 9.2.2 survivable. Qt and HDF5 headers generate warnings under `/W4` and `-Wextra` that no amount of first-party discipline can fix, and without `SYSTEM` those warnings become errors in a file nobody on this team can change — which reliably ends with someone lowering the warning level for everyone. Suppressing them at the boundary keeps the strict policy pointed at the code the team actually owns.

**GOOD**

```cpp
# where an imported target does not already mark its includes SYSTEM
add_library(hdf5_system INTERFACE)
target_link_libraries(hdf5_system INTERFACE HDF5::HDF5)
target_include_directories(hdf5_system SYSTEM INTERFACE ${HDF5_INCLUDE_DIRS})
target_link_libraries(core PUBLIC hdf5_system)
```

**ENFORCEMENT**  Advisory — code review; a new warning appearing from a third-party header is the symptom that surfaces it.

## 9.3 Cross-toolchain parity

#### 9.3.1 No compiler-specific conditional compilation in first-party code

**RULE**  `#ifdef _MSC_VER`, `#ifdef __GNUC__`, `#ifdef _WIN32` and equivalents do not appear in `core`, `gui`, or `app` source files. Where behavior genuinely must differ by platform or compiler, the difference is resolved in CMake (a different source file compiled per platform, a compile definition, a different implementation of a narrow interface), not by branching inside a shared file. The one permitted exception is a generated export header, which no human writes by hand.

**RATIONALE**  A file with two `#ifdef` branches is a file where only one branch is ever compiled, which means only one branch is ever compiled *correctly* — the other rots silently until the day the other toolchain is added, and then produces a pile of errors in code nobody has looked at in a year. Pushing the difference into CMake means each platform-specific implementation is a whole file that compiles or does not, and the shared code stays genuinely shared. This matters disproportionately here because the second toolchain does not exist yet: `#ifdef` branches written today would be entirely unverified when the Linux build finally happens.

**GOOD**

```cpp
// core/platform/platform_paths.h  -- one declaration, no conditionals
std::filesystem::path userConfigDirectory();

// core/platform/platform_paths_windows.cpp  -- compiled only on Windows, per CMake
// core/platform/platform_paths_posix.cpp    -- compiled only on POSIX, per CMake
```

```cpp
# core/CMakeLists.txt
if(WIN32)
    target_sources(core PRIVATE platform/platform_paths_windows.cpp)
else()
    target_sources(core PRIVATE platform/platform_paths_posix.cpp)
endif()
```

**BAD**

```cpp
std::filesystem::path userConfigDirectory()
{
#ifdef _WIN32                        // BAD -- the other branch is never compiled and rots
    return getWindowsAppDataPath();
#else
    return getXdgConfigPath();
#endif
}
```

**ENFORCEMENT**  Advisory — code review; a grep for `_MSC_VER`, `__GNUC__`, and `_WIN32` outside `cmake/` and generated headers is a straightforward CI check once available.

#### 9.3.2 Four build configurations, defined by preset

**RULE**  The supported configurations are Debug, Release, RelWithDebInfo, and a sanitizer configuration (12.6). Release and RelWithDebInfo both generate debug symbols; RelWithDebInfo is what ships (20.2), because a stripped Release build cannot produce a usable crash report (Section 21). Optimization and debug-symbol flags come from CMake's own configuration defaults — they are never set by hand in a target's compile options.

**RATIONALE**  Shipping a build with no symbols means every crash report from the field is a hex address nobody can resolve, which is the difference between a bug report that leads somewhere and one that does not. The cost is a larger binary and a separately-archived symbol file (20.3), which is a trade worth making explicitly rather than by default.

**ENFORCEMENT**  Preset definitions (Appendix E) are the real gate for which configurations exist; Advisory — code review that no target sets optimization flags by hand.
