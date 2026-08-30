#!/usr/bin/env python3
"""Consistency check for the constants registry (standards/00-constants.md).

Three failure modes it catches, all of which are silent otherwise:

  1. A "Used in" column names a rule that no longer exists -- the usual cause
     is a rule being renumbered or removed without updating the registry.
  2. A constant delegated to the project profile has no value there.
  3. A value that lives in the project profile is written out literally in a
     rule WITHOUT citing its constant id. Stating the value is fine and often
     reads better -- what is not fine is stating it with nothing to tell a
     reader (or a fork) that it is a project value. This check found C-14 and
     C-31.

Run from the repository root:  python3 tools/check_constants.py
Exit status is non-zero if anything fails, so it can gate a merge later.
"""
import glob
import re
import sys

STANDARDS = "standards/*.md"
REGISTRY = "standards/00-constants.md"
PROFILE = "project/PROJECT_PROFILE.md"

# Section numbers deliberately retired rather than reassigned.
RETIRED = {"2.5", "2.5.1"}


def rule_ids():
    ids = set()
    for path in glob.glob(STANDARDS):
        for line in open(path, encoding="utf-8"):
            match = re.match(r"^#{1,6} (\d+(?:\.\d+)*)", line)
            if match:
                ids.add(match.group(1))
    return ids


def registry_rows():
    rows = []
    for line in open(REGISTRY, encoding="utf-8"):
        match = re.match(r"^\| (C-\d+) \| ([^|]+?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \|", line)
        if match:
            rows.append(
                {
                    "id": match.group(1),
                    "name": match.group(2).strip(),
                    "value": match.group(3).strip(),
                    "scope": match.group(4).strip(),
                    "used_in": match.group(5).strip(),
                }
            )
    return rows


def rule_corpus():
    parts = []
    for path in glob.glob(STANDARDS):
        if path.endswith("00-constants.md"):
            continue
        parts.append(open(path, encoding="utf-8").read())
    return "\n".join(parts)


def main():
    ids = rule_ids()
    rows = registry_rows()
    corpus = rule_corpus()
    profile = open(PROFILE, encoding="utf-8").read()
    failures = []

    for row in rows:
        # 1: every referenced rule must exist
        for ref in re.findall(r"\b\d+\.\d+(?:\.\d+)?\b", row["used_in"]):
            if ref not in ids and ref not in RETIRED:
                failures.append(f"{row['id']} ({row['name']}): 'Used in' names rule {ref}, which does not exist")

        # 2: delegated constants must actually be defined in the profile
        if "project profile" in row["value"].lower():
            key = row["name"].split("(")[0].strip()
            if key.lower() not in profile.lower():
                failures.append(f"{row['id']} ({row['name']}): delegated to the project profile, but the profile does not mention it")

    # 3: profile values must not also be written out in a rule
    for line in profile.split("\n"):
        match = re.match(r"^\| (C-\d+) [^|]*\| (.+?) \|", line)
        if not match:
            continue
        value = match.group(2).strip().strip("`")
        if len(value) < 12 or value.startswith("*"):
            continue  # too short to match meaningfully, or a placeholder
        cid = match.group(1)
        for line_no, rule_line in enumerate(corpus.split("\n"), 1):
            if value in rule_line and cid not in rule_line:
                failures.append(
                    f"{cid}: value {value!r} is written in a rule without citing the constant "
                    f"-- either cite {cid} on that line, or remove the literal"
                )
                break

    print(f"registry rows: {len(rows)}   rules defined: {len(ids)}")
    if failures:
        print(f"\n{len(failures)} problem(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
