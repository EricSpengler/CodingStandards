# 11. Third-Party Libraries & Dependency Management

Every dependency is a permanent commitment: code the team did not write, cannot easily change, and must keep building for as long as the product ships. This section covers what gets in, how it is used once it is in, and what keeps it current.

The mechanics of *declaring* a dependency — vcpkg manifest mode, the pinned baseline, `find_package` and imported targets — are in 8.3 and are not repeated here. This section is about which dependencies and why.

## 11.1 Adopting a dependency

#### 11.1.1 A new dependency is a PR of its own, with the alternatives stated

**RULE**  Adding a third-party library is never a side effect of a feature PR. It is a separate, dependency-only PR that adds the vcpkg manifest entry, wires the `find_package` call, adds the library to the approved list in 11.2, and states in the PR description: what it is for, what the alternatives considered were, its license, and roughly what it costs (binary size, compile time, transitive dependencies). A dependency pulled in to solve one small problem that the standard library already solves is rejected.

**RATIONALE**  A dependency introduced inside a 400-line feature PR gets the review attention of a feature PR, which is to say almost none — the reviewer is reading the feature. Separating it means the decision gets looked at as a decision. Recording the alternatives matters a year later, when someone asks why this library and not the obvious other one; without the record, the answer is always "no idea," and the question gets re-litigated from scratch. This applies with particular force here because every dependency also has to clear export-control and license review (11.4), which is not something to discover after the code is written.

**ENFORCEMENT**  Advisory — code review; the separate-PR requirement is what makes it visible.

#### 11.1.2 Approved libraries are listed here; anything else needs 11.1.1 first

**RULE**  The table in 11.2 is the complete list of third-party libraries permitted in first-party code. A library not on it does not appear in an `#include` until it has been through 11.1.1 and added to the table. Header-only libraries, single-file "just drop it in" libraries, and vendored source copies are subject to exactly the same process — there is no lightweight path.

**RATIONALE**  The single-file carve-out is the loophole worth closing explicitly, because a header-only library feels like it costs nothing to add and therefore tends to skip review entirely. It costs the same as any other dependency in every way that matters later: license obligations, security exposure, compile time, and someone's future maintenance. Vendored copies are worse, since they are invisible to vcpkg and therefore invisible to the update process in 11.4.

**ENFORCEMENT**  Advisory — code review; a new `find_package` or a new top-level include directory is the visible signal.

## 11.2 Approved libraries

| Library | Used for | Layer | Notes |
| --- | --- | --- | --- |
| Qt 6 (Widgets, Gui, Core) | All GUI | `gui`, `app` only | Never in `core` (10.1.1). License review outstanding — see 11.4.3 |
| HDF5 | Primary data format read/write | `core` | C API — must be wrapped per 11.3.1 |
| Vulkan | Accelerated visualization | `gui` | C API — must be wrapped per 11.3.1 |
| DuckDB | Analytical queries over extracted data | `core` | C++ API; wrap query construction, never build SQL by string concatenation (18.4) |
| zlib | Compression | `core` | C API — must be wrapped per 11.3.1 |
| CLI11 | Command-line parsing | `app` only | Never in `core` or `gui` |
| nlohmann/json | Configuration and settings serialization | `core` | See 11.2.1 for why this rather than glaze |
| GoogleTest | Unit and integration tests for `core` | `tests` only | Section 12 |
| QTest | GUI tests | `tests` only | Section 12 |

#### 11.2.1 JSON: nlohmann/json, not glaze

**RULE**  JSON serialization uses nlohmann/json. glaze is not used. JSON is for configuration, settings persistence (19.4), and small structured metadata — it is never the format for bulk record data, which is HDF5's job.

**RATIONALE**  glaze is meaningfully faster than nlohmann, and if JSON were on this project's hot path that would settle it. It is not: the bulk data path is HDF5, and JSON here handles settings files and small metadata blobs measured in kilobytes, where the difference between the two libraries is unmeasurable against the cost of the disk read. With performance off the table, the remaining criteria favor nlohmann clearly — it is the more widely known API (a new team member has likely used it), its documentation and error messages are better, its compile-time cost is lower, and its MSVC support has a much longer track record, which matters given Section 9's note that MSVC is the only toolchain currently exercised. glaze's reflection-heavy design also leans on exactly the C++23 corners that Section 9.1.2 defers for cross-toolchain reasons.

The condition that would reverse this is specific and worth stating: if JSON ever becomes a bulk data path — streaming large record sets as JSON, or parsing JSON in a loop that shows up in a profile — glaze becomes the right answer and this rule should be revisited rather than worked around.

**GOOD**

```cpp
// core/config/settings_store.cpp -- small structured data, human-editable
nlohmann::json document;
document["batchSize"] = settings.batchSize;
document["strictMode"] = settings.strictMode;
```

**BAD**

```cpp
// BAD -- bulk record data does not go through JSON at all, in either library
nlohmann::json output;
for (const auto& record : batch.records)
{
    output["records"].push_back(record.toJson());
}
```

*Open item, needs team ratification: the master topic list records this as an open decision between glaze and nlohmann, so this rule is a reasoned proposal rather than a settled call. The argument above rests entirely on the premise that JSON is not on the hot path — if that premise is wrong for a use case not yet described, the conclusion flips.*

**ENFORCEMENT**  Advisory — code review.

## 11.3 Using a third-party library

#### 11.3.1 Every C API is wrapped in an RAII type at the boundary; handles never escape

**RULE**  A C-style library API — HDF5, Vulkan, zlib — is reachable from exactly one place: a wrapper type in `core` (or `gui`, for Vulkan) whose constructor acquires the resource and whose destructor releases it, per 6.4.4. A raw library handle (`hid_t`, `VkDevice`, `z_stream`) never appears in a function signature outside that wrapper, never appears as a member of any other class, and is never returned to a caller. The wrapper converts the library's error convention to `std::expected` or an exception at that same boundary, exactly as 6.3.2 requires, with no status codes forwarded outward.

**RATIONALE**  This is where 6.3.2, 6.4.2, and 6.4.4 all land at once, and it is worth stating as a single rule because C APIs are precisely where each of them is most tempting to skip. A leaked `hid_t` is an owning raw handle with none of `unique_ptr`'s protections — nothing says who closes it, and a copy of the struct holding it produces a double-close that HDF5 reports as a cryptic error far from the cause. Confining the handle to one type also means the Rule of Five (6.4.2) has to be got right exactly once instead of everywhere the handle is stored.

**GOOD**

```cpp
// core/io/hdf5file.h -- the only place hid_t exists
class Hdf5File
{
public:
    [[nodiscard]] static std::expected<Hdf5File, Hdf5Error> open(const std::filesystem::path& path);

    ~Hdf5File();
    Hdf5File(const Hdf5File&) = delete;
    Hdf5File& operator=(const Hdf5File&) = delete;
    Hdf5File(Hdf5File&&) noexcept;
    Hdf5File& operator=(Hdf5File&&) noexcept;

    [[nodiscard]] std::expected<RecordBatch, Hdf5Error> readBatch(std::string_view datasetName);

private:
    hid_t fileHandle;   // never leaves this class
};
```

**BAD**

```cpp
hid_t openHdf5File(const std::filesystem::path& path);   // BAD -- raw handle returned to a
                                                          // caller; nothing says who closes it

class RecordCache
{
private:
    hid_t sourceFile;   // BAD -- handle stored outside the wrapper; ownership now ambiguous
};

herr_t status = H5Fclose(handle);   // BAD -- status code visible outside the wrapper (6.3.2)
```

**ENFORCEMENT**  Advisory — code review; a grep for `hid_t`, `Vk[A-Z]`, and `z_stream` outside the designated wrapper directories is a straightforward CI check once available.

#### 11.3.2 Third-party types do not appear in first-party interfaces

**RULE**  A type owned by a third-party library does not appear in the public interface of a first-party class or free function, with two deliberate exceptions: Qt types within `gui` (where Qt is the framework, not a dependency), and the wrapper types of 11.3.1 within their own module. Elsewhere, a first-party type carries the data across the boundary.

**RATIONALE**  A third-party type in an interface is a dependency every consumer of that interface inherits, including consumers who had no reason to know the library exists — which is 8.2.2's `PUBLIC`-versus-`PRIVATE` distinction expressed in the source rather than in CMake. It also makes replacing the library a change to every call site rather than to one wrapper, which is the difference between a bounded task and a rewrite.

**ENFORCEMENT**  Advisory — code review.

## 11.4 Keeping dependencies current

#### 11.4.1 Dependencies are reviewed for updates once per sprint, at close-out

**RULE**  At each sprint close-out (2.2), alongside the release cut, someone checks whether the pinned vcpkg baseline (8.3.1) has moved and what changed for the libraries in 11.2. Updating the baseline is a normal PR under the standard process, never bundled into a release-prep branch (2.4.1). A security fix is the one case that may be taken mid-sprint rather than waiting for close-out.

**RATIONALE**  Attaching this to an existing ritual is the same reasoning 2.5.1 uses for the poison-pill rebuild — a dependency review with its own calendar is a dependency review nobody does. Keeping the update out of the release-prep branch matters because a baseline bump can change generated binaries in ways worth reviewing on their own; folding it into the release PR means it ships in the same commit that generates the changelog, with no separate opportunity to catch a regression during the manual build/test step (1.8).

**ENFORCEMENT**  Manual — sprint close-out ritual.

#### 11.4.2 Known-vulnerability scanning is not automated today

**RULE**  There is no automated CVE or vulnerability scanning of dependencies in this project today. Until there is, the sprint review in 11.4.1 includes checking the release notes and security advisories of the libraries in 11.2 for anything security-relevant since the current baseline.

**RATIONALE**  Stated as an explicit gap rather than left unmentioned, for the same reason 1.8 documents the manual review process: an undocumented gap is indistinguishable from an oversight, and the whole point of writing this down is that the team knows which protections it actually has. The realistic fix is `vcpkg`'s SBOM output fed to a scanner in CI, which is blocked on CI existing at all.

*Open item, needs team ratification: whether a manual advisory check at sprint close-out is an acceptable interim control, or whether the export-control context (Section 4) means this needs a real scanner sooner than CI would otherwise arrive. This is a question for whoever owns security compliance for the program, not one the dev team should settle alone.*

**ENFORCEMENT**  Manual — sprint close-out ritual; no tooling exists today.

#### 11.4.3 Licenses are permissive by default; Qt's licensing needs a determination on record

**RULE**  A new dependency is permitted without further review if it is under a permissive license — MIT, BSD-2/3-Clause, Apache-2.0, or Boost Software License. A copyleft license (GPL, AGPL) is not adopted. An LGPL dependency requires a written determination from whoever owns license compliance for the program before it is added, recorded in the 11.1.1 PR. Every shipped build includes a third-party notices file listing each dependency, its version, and its license text (20.4).

**RATIONALE**  The permissive list covers essentially every library a project like this needs and requires no analysis per-library, which is what makes the rule cheap enough to actually follow. The LGPL carve-out is not theoretical: **Qt's open-source licensing is LGPLv3**, which carries obligations around dynamic linking and the ability for a recipient to relink the application against a modified Qt. Those obligations interact directly with how this project ships — a statically-linked Qt in a single-executable installer is the configuration most likely to be non-compliant. Whether the program holds a commercial Qt license, and if not how the installer satisfies LGPLv3, is a determination that needs to exist on paper.

*Open item, needs team ratification — and this one is not a developer decision. Someone with authority over license compliance for this program needs to record (a) whether a commercial Qt license is held, and (b) if not, that the shipping configuration (20.1) satisfies LGPLv3's relinking requirement. Flagged here because it is invisible until it is expensive, and because the packaging decisions in Section 20 depend on the answer. Nothing in this guide should be read as legal advice.*

**ENFORCEMENT**  Advisory — code review for the permissive-license default; the Qt determination is external to this document and is tracked as an open item until recorded.
