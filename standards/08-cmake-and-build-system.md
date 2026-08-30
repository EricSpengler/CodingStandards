# 8. CMake & Build System

The build is the one piece of this project every developer touches on their first day and then tries never to touch again. That makes it exactly the place where undocumented convention costs the most: a build file that works but nobody understands is a build file nobody dares change. This section describes modern, target-based CMake — everything is expressed as properties on named targets, and nothing is expressed as global state.

The single organizing idea, from which most rules below follow: **a target describes its own requirements, and anything that links it inherits them automatically.** If you find yourself setting something globally so that some other directory can see it, that is the signal you have reached for the wrong tool.

## 8.1 Project structure

#### 8.1.1 One CMakeLists.txt per target directory; the top-level file sets policy only

**RULE**  The repository root CMakeLists.txt does four things and nothing else: `cmake_minimum_required`, `project()`, project-wide settings that genuinely apply to every target (C++ standard, output directories, `CTest` inclusion), and `add_subdirectory()` calls. It never defines a target, never lists a source file, and never sets a compile flag for a specific target. Every target is defined in a CMakeLists.txt in its own directory.

**RATIONALE**  A root file that also defines targets grows into the file everyone edits, which makes it the file that always conflicts in a merge — the same problem that motivated splitting this guide itself into per-section documents. Keeping definitions next to the sources they build also means the answer to "where is this target defined" is always "in the directory it builds," with no searching.

**GOOD**

```cpp
# CMakeLists.txt (repository root)
cmake_minimum_required(VERSION 3.25)
project(crna_pa VERSION 0.5.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(CTest)

add_subdirectory(core)
add_subdirectory(gui)
add_subdirectory(app)
add_subdirectory(tests)
```

**BAD**

```cpp
# CMakeLists.txt (repository root)
project(crna_pa)

add_library(core                          # BAD -- target defined in the root file
    core/io/hdf5reader.cpp
    core/io/record_batch.cpp
)
include_directories(${CMAKE_SOURCE_DIR})  # BAD -- global state, see 8.2.1
```

**ENFORCEMENT**  Advisory — code review.

#### 8.1.2 Four top-level targets: core, gui, app, tests

**RULE**  The tree has exactly four top-level build targets, and a new one is added only by amending this rule. `core` is a static library containing all data extraction, parsing, and analysis logic, and is Qt-free (10.1). `gui` is a static library containing all Qt widgets, models, and view logic, and links `core`. `app` is the executable, and is thin — argument parsing, application bootstrap, and wiring `gui` to `core`, with no domain logic of its own. `tests` builds the test binaries (Section 12). `core` never links `gui` or `app`; `gui` never links `app`.

**RATIONALE**  The dependency direction is the point: because it only ever flows one way (app depends on gui depends on core), `core` can be built, tested, and reasoned about with no Qt present at all, which is what makes the Qt-free boundary in 10.1 mechanically enforceable rather than aspirational. Keeping `app` thin means the executable is not a place logic can hide from tests — anything worth testing lives in a library target that a test can link.

**GOOD**

```cpp
# core/CMakeLists.txt -- no Qt anywhere
target_link_libraries(core PUBLIC HDF5::HDF5 PRIVATE ZLIB::ZLIB)

# gui/CMakeLists.txt
target_link_libraries(gui PUBLIC crna::core Qt6::Widgets)

# app/CMakeLists.txt
target_link_libraries(app PRIVATE crna::gui CLI11::CLI11)
```

**BAD**

```cpp
# core/CMakeLists.txt
target_link_libraries(core PUBLIC Qt6::Core)  # BAD -- core must stay Qt-free, see 10.1

# gui/CMakeLists.txt
target_link_libraries(gui PUBLIC crna::app)   # BAD -- inverts the dependency direction
```

**ENFORCEMENT**  Build failure is the real gate for the dependency direction — a cycle is a hard CMake error. The Qt-free constraint on `core` is enforced per 10.1.

#### 8.1.3 Out-of-source builds only

**RULE**  The build directory is never the source directory. Every preset (8.4.1) writes to `build/<preset-name>/`, which is gitignored per 1.6.1. A configure run that would write CMakeCache.txt into the source tree is rejected outright.

**RATIONALE**  In-source builds scatter generated files through the tree, which makes `git status` unreadable and makes a clean rebuild a matter of deleting the right files rather than deleting one directory. Rejecting it at configure time is better than gitignoring the debris, because the debris is the symptom.

**GOOD**

```cpp
# in the root CMakeLists.txt, immediately after project()
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR
        "In-source builds are not supported (8.1.3). Configure with a preset instead: "
        "cmake --preset windows-msvc-debug")
endif()
```

**ENFORCEMENT**  The FATAL_ERROR guard above (actual gate — it is a hard configure failure).

## 8.2 Target definition

#### 8.2.1 target_* commands only — never a directory-scope command

**RULE**  `include_directories`, `add_definitions`, `add_compile_options`, `link_libraries`, and `link_directories` are never used. Their target-scoped equivalents — `target_include_directories`, `target_compile_definitions`, `target_compile_options`, `target_link_libraries` — are used exclusively, and always with an explicit `PUBLIC`, `PRIVATE`, or `INTERFACE` keyword (8.2.2). `set(CMAKE_CXX_FLAGS ...)` is likewise never used to add flags; see 9.2 for how warning flags are set.

**RATIONALE**  A directory-scope command applies to every target defined in that directory and every subdirectory below it, including ones added later by someone who has no idea the command is there. That is action at a distance: a target picks up an include path or a preprocessor definition with nothing in its own definition saying where it came from. Target-scoped commands make every requirement traceable to the line that set it, and — more importantly — make requirements propagate through linking, which is what lets a consumer get the right include paths just by linking the target.

**GOOD**

```cpp
target_include_directories(core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_definitions(core PRIVATE CRNA_CORE_BUILDING)
```

**BAD**

```cpp
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)  # BAD -- leaks into every target
                                                           # defined here and below
add_definitions(-DCRNA_CORE_BUILDING)                      # BAD -- same problem
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")            # BAD -- see 9.2
```

**ENFORCEMENT**  Advisory — code review; a grep for the banned command names across all CMakeLists.txt files is a trivial CI check once available, and is listed as such in Section 7.

#### 8.2.2 PUBLIC / PRIVATE / INTERFACE means "does this appear in my headers"

**RULE**  Every `target_link_libraries`, `target_include_directories`, and `target_compile_definitions` call names a visibility keyword, chosen by one test: if the dependency appears in this target's *public headers*, it is `PUBLIC`; if it is used only inside this target's .cpp files, it is `PRIVATE`; if this target has no sources of its own and only propagates requirements (a header-only or interface target), it is `INTERFACE`. `PRIVATE` is the default answer when the test is genuinely unclear — over-declaring `PUBLIC` is the failure mode worth avoiding.

**RATIONALE**  This keyword is the single highest-leverage decision in a CMake file, and it is not a style preference: it determines what every consumer of the target is forced to depend on. A dependency marked `PUBLIC` when it should be `PRIVATE` propagates through the whole link graph, so `app` ends up compiling against HDF5 headers it never uses, and a change to a purely internal implementation detail of `core` triggers a rebuild of everything. Defaulting to `PRIVATE` when unsure errs toward the direction that fails loudly — a missing propagation is a compile error the author sees immediately, whereas an unnecessary one is invisible and permanent.

**GOOD**

```cpp
# hdf5.h appears in core's public headers -- consumers need it, so PUBLIC.
# zlib is used only inside core's .cpp files -- consumers never see it, so PRIVATE.
target_link_libraries(core
    PUBLIC  HDF5::HDF5
    PRIVATE ZLIB::ZLIB
)
```

**BAD**

```cpp
target_link_libraries(core HDF5::HDF5 ZLIB::ZLIB)  # BAD -- no visibility keyword; CMake falls
                                                    # back to a legacy mode that behaves like
                                                    # PUBLIC for everything

target_link_libraries(core PUBLIC ZLIB::ZLIB)      # BAD -- zlib is an implementation detail;
                                                    # PUBLIC forces every consumer to depend on it
```

**ENFORCEMENT**  Advisory — code review. This is the CMake rule most worth spending review attention on, since a wrong keyword compiles cleanly and only shows up later as rebuild churn.

#### 8.2.3 Namespaced ALIAS targets for every library; consumers link the alias

**RULE**  Every library target gets an `ALIAS` in the `crna::` namespace, declared immediately after the target itself. Anything linking a first-party library links the namespaced alias, never the bare target name.

**RATIONALE**  A name containing `::` is guaranteed by CMake to be a target — if it does not exist, configuration fails immediately with a clear error naming the missing target. A bare name that does not exist is instead treated as a raw library name to pass to the linker, so a typo in `target_link_libraries(app PRIVATE gui)` produces a link error about `-lgui` at the very end of the build rather than a configure error at the start. This also makes first-party and third-party dependencies read identically at the call site (`crna::core` next to `Qt6::Widgets`), which matters when the target later moves behind a `find_package` for an installed build.

**GOOD**

```cpp
add_library(core STATIC)
add_library(crna::core ALIAS core)

# elsewhere
target_link_libraries(gui PUBLIC crna::core)
```

**BAD**

```cpp
target_link_libraries(gui PUBLIC core)   # BAD -- a typo here becomes a confusing link-stage
                                          # error instead of an immediate configure error
```

**ENFORCEMENT**  Configure-time failure is the real gate once aliases are used consistently; Advisory — code review to confirm aliases are declared and linked.

#### 8.2.4 Source files are listed explicitly — never file(GLOB)

**RULE**  Every source and header file is named individually in `target_sources`. `file(GLOB)` and `file(GLOB_RECURSE)` are never used to collect sources, including with `CONFIGURE_DEPENDS`. Headers are listed alongside sources so they appear in IDE project trees.

**RATIONALE**  A glob is evaluated at configure time, so adding a file does not change any input CMake tracks — the build does not reconfigure, the new file is silently not compiled, and the failure surfaces as a confusing link error rather than anything pointing at the real cause. `CONFIGURE_DEPENDS` mitigates this by re-globbing on every build, but at the cost of a filesystem scan per build and with no guarantee across generators, which trades a reliable failure for an unreliable one. The explicit list also makes adding a file a visible line in a diff — a reviewer can see that a new file joined the build, which matters given every file also has to carry a classification header (4.1).

**GOOD**

```cpp
target_sources(core PRIVATE
    io/hdf5reader.cpp
    io/hdf5reader.h
    io/record_batch.cpp
    io/record_batch.h
)
```

**BAD**

```cpp
file(GLOB_RECURSE CORE_SOURCES "*.cpp")   # BAD -- new files silently skipped until someone
target_sources(core PRIVATE ${CORE_SOURCES})  # reconfigures by hand
```

**ENFORCEMENT**  Advisory — code review; a grep for `file(GLOB` across CMakeLists.txt files is a trivial CI check once available.

#### 8.2.5 CMake identifier naming

**RULE**  Target names are lowercase snake_case, matching the directory they live in (`core`, `gui`, `app`), with a `crna::` alias per 8.2.3. Local variables inside a CMakeLists.txt or module are lowercase snake_case. Cache variables and options visible to the person configuring the build are `CRNA_`-prefixed SCREAMING_SNAKE_CASE (`CRNA_BUILD_TESTS`, `CRNA_ENABLE_SANITIZERS`). Functions and macros defined in `cmake/` modules are `crna_`-prefixed lowercase snake_case (`crna_add_test_target`).

**RATIONALE**  CMake has a single flat variable namespace with no scoping to protect you, so the prefix on anything cached or globally defined is the only thing preventing a collision with a variable set by CMake itself, by a `find_package` module, or by a vcpkg toolchain file — and such a collision produces no error, just wrong behavior. The lowercase/uppercase split follows the same principle Section 3 applies to C++: casing signals scope and lifetime, so a reader can tell a throwaway local from a user-facing knob without looking either one up.

**GOOD**

```cpp
option(CRNA_BUILD_TESTS "Build the test suite" ON)
set(crna_generated_dir "${CMAKE_CURRENT_BINARY_DIR}/generated")

function(crna_add_test_target target_name)
    # ...
endfunction()
```

**BAD**

```cpp
option(BUILD_TESTS "Build the test suite" ON)   # BAD -- unprefixed; collides with the same
                                                 # option name in vendored dependencies
set(GENERATED_DIR "...")                         # BAD -- looks like a cache variable, is not
function(add_test_target target_name)            # BAD -- unprefixed, and shadows nothing
endfunction()                                     # visibly but reads like a built-in
```

**ENFORCEMENT**  Advisory — code review.

#### 8.2.6 Prefer functions over macros in cmake/ modules

**RULE**  Reusable build logic lives in a `.cmake` module under `cmake/` and is written as a `function()`, not a `macro()`. A macro is used only when the code genuinely must set a variable in the caller's scope, and when it does, the reason is stated in a comment above it. A function returning a value does so via `PARENT_SCOPE` or CMake 3.25's `return(PROPAGATE)`, explicitly.

**RATIONALE**  A macro does not create a scope: its variables leak into the caller, and its arguments are textually substituted rather than bound, so `${ARGN}` and any unquoted argument behave differently than they look. Functions get their own scope, so a helper cannot accidentally clobber a caller's variable — the same reasoning behind 6.1.19's preference for anonymous namespaces over file-scope statics in C++.

**GOOD**

```cpp
function(crna_set_warnings target_name)
    # see 9.2 for the flag lists themselves
    target_compile_options(${target_name} PRIVATE ${crna_warning_flags})
endfunction()
```

**BAD**

```cpp
macro(crna_set_warnings target_name)   # BAD -- no scope; every variable set inside leaks
    set(flags -Wall -Wextra)            # into whatever CMakeLists.txt called this
    target_compile_options(${target_name} PRIVATE ${flags})
endmacro()
```

**ENFORCEMENT**  Advisory — code review.

## 8.3 Dependencies

#### 8.3.1 vcpkg manifest mode with a pinned baseline; no system-installed dependencies

**RULE**  Every third-party dependency is declared in a `vcpkg.json` manifest at the repository root, with a `builtin-baseline` pinned to a specific vcpkg commit SHA. No dependency is ever resolved from a system package manager, a developer's local install, or a checked-in binary. Changing a dependency version means changing the baseline or adding an explicit `overrides` entry, in a PR, with the reason in the commit body.

**RATIONALE**  A pinned baseline is what makes "it builds on my machine" a meaningful statement: every developer and every build resolves the identical dependency versions from the identical source, so a build difference is a real difference and not a local-environment artifact. This matters more than usual for this project because the manual review process (1.8) has a reviewer build the branch locally — that step only proves anything if the reviewer's build is resolving the same dependencies the author's did. Without a baseline, vcpkg resolves against whatever its registry happens to be at the moment of the build, which means the same commit produces different binaries on different days.

**GOOD**

```cpp
{
  "name": "crna-pa",
  "version-string": "0.5.0",
  "builtin-baseline": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
  "dependencies": [
    "hdf5",
    "zlib",
    { "name": "qtbase", "default-features": false, "features": ["widgets"] },
    "cli11",
    "gtest"
  ]
}
```

**BAD**

```cpp
{
  "dependencies": [ "hdf5", "zlib" ]   # BAD -- no builtin-baseline; versions drift with the
}                                       # registry, so two developers get different builds
                                        # from the same commit
```

**ENFORCEMENT**  Advisory — code review for the manifest contents. The pinned baseline itself is a real gate once present, since vcpkg enforces it during dependency resolution.

#### 8.3.2 find_package plus imported targets; never a raw path or a bare library name

**RULE**  Dependencies enter the build through `find_package(... REQUIRED)` followed by linking the imported target it provides (`HDF5::HDF5`, `Qt6::Widgets`, `ZLIB::ZLIB`). A dependency is never brought in by hard-coded include path, hard-coded library path, a bare `-lfoo` style name, or by a variable like `${HDF5_LIBRARIES}` when a namespaced imported target exists. `REQUIRED` is always present — an optional dependency is expressed with an explicit `if()` on a `CRNA_`-prefixed option (8.2.5), never by silently continuing when a `find_package` fails.

**RATIONALE**  An imported target carries its own include directories, compile definitions, and transitive dependencies as properties, so linking it configures the consumer correctly with one line. A raw path configures only the one thing you remembered — and then breaks on the other developer's machine, or on the toolchain that installs headers somewhere else, which is exactly the cross-toolchain fragility Section 9 is trying to avoid. Requiring `REQUIRED` means a missing dependency fails at configure time with a clear message rather than at link time with an undefined symbol.

**GOOD**

```cpp
find_package(HDF5 REQUIRED COMPONENTS C)
find_package(Qt6 REQUIRED COMPONENTS Widgets)

target_link_libraries(core PUBLIC HDF5::HDF5)
target_link_libraries(gui  PUBLIC Qt6::Widgets)
```

**BAD**

```cpp
target_include_directories(core PUBLIC "C:/dev/hdf5/include")   # BAD -- hard-coded path
target_link_libraries(core PUBLIC "C:/dev/hdf5/lib/hdf5.lib")   # BAD -- same
target_link_libraries(core PUBLIC ${HDF5_LIBRARIES})            # BAD -- variable form; loses
                                                                 # include dirs and transitive deps
```

**ENFORCEMENT**  Advisory — code review; a hard-coded absolute path in a CMakeLists.txt is an easy grep-based CI check once available.

## 8.4 Configuration

#### 8.4.1 CMakePresets.json is the only supported way to configure a build

**RULE**  A committed `CMakePresets.json` at the repository root defines every supported configuration; `CMakeUserPresets.json` is gitignored and is where a developer puts local variations. Documentation, onboarding (Section 23), and the manual review process (1.8) all reference presets by name — no raw `cmake -D...` command line is ever documented as the way to build. Adding a supported configuration means adding a preset in a PR.

**RATIONALE**  A preset is an executable version of the build instructions, which means it cannot drift out of date the way a README code block silently does. It also makes the review step in 1.8 reproducible: "build the `windows-msvc-debug` preset" is unambiguous in a way "build it in Debug" is not, and both IDEs in use read presets natively, so the IDE and the command line configure identically rather than nearly-identically.

**GOOD**

```cpp
cmake --preset windows-msvc-debug
cmake --build --preset windows-msvc-debug
ctest --preset windows-msvc-debug
```

**BAD**

```cpp
mkdir build && cd build                      # BAD -- ad hoc; no record of what flags were used,
cmake .. -DCMAKE_BUILD_TYPE=Debug \          # and the next person guesses differently
    -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
```

**ENFORCEMENT**  Advisory — code review, plus documentation convention. See Appendix E for the preset file itself.

#### 8.4.2 cmake_minimum_required is pinned to a real floor and raised deliberately

**RULE**  `cmake_minimum_required(VERSION 3.25)` is the current floor, chosen because it is the earliest version providing everything this build uses (presets v5, `return(PROPAGATE)`, `target_sources` `FILE_SET`). Raising it is a PR of its own with the reason stated: which feature required the bump. A range form (`VERSION 3.25...3.31`) is used so newer CMake versions run with current policy defaults rather than the compatibility behavior of the floor.

**RATIONALE**  A floor set too low is a lie — it claims support for CMake versions nobody has ever built with, and the failure surfaces on whichever machine actually has the old version. Setting it to the version whose features the build genuinely uses makes the requirement honest. The range form matters separately: without an upper bound, CMake applies the policy defaults of the *minimum* version, so a build pinned at 3.25 keeps getting 3.25-era behavior forever even on CMake 4.x, and quietly accumulates deprecated behavior nobody notices until a policy is finally removed.

**GOOD**

```cpp
cmake_minimum_required(VERSION 3.25...3.31)
```

**BAD**

```cpp
cmake_minimum_required(VERSION 3.10)   # BAD -- nothing has ever been built with 3.10; the
                                        # floor is fiction, and policy defaults stay frozen
                                        # at 3.10-era behavior
```

**ENFORCEMENT**  CMake itself (actual gate — configuring with an older version is a hard error).

*Open item, needs team ratification: the 3.25 floor is derived from the features this section and Appendix E actually use. Confirm it against the CMake version bundled with both supported IDEs before adopting — if either ships something older, the floor moves down and `return(PROPAGATE)` in 8.2.6 needs a `PARENT_SCOPE` rewrite.*
