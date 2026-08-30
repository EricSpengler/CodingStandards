# Appendix D: Example cliff.toml

The git-cliff configuration referenced by 2.4.2. It lives at the repository root and is what actually controls changelog grouping — the release process (2.4.1, step 3) just runs git-cliff against it.

Two things in here exist specifically because of rules elsewhere in this guide, and should not be changed without revisiting those rules: the commit parsers mirror the exact type vocabulary fixed in 1.3.1, and `filter_unconventional = false` is what makes a malformed commit message show up in the changelog as an unfiled entry rather than vanishing from it silently.

```toml
[changelog]
header = """
# Changelog

All notable changes to this project are documented in this file.
Entries are generated from Conventional Commit messages (1.3.1) by git-cliff.
"""

body = """
{% if version %}\
## {{ version | trim_start_matches(pat="v") }} — {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
## Unreleased
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}

### {{ group }}
{% for commit in commits %}
- {% if commit.scope %}**{{ commit.scope }}**: {% endif %}\
{{ commit.message | upper_first }}\
{% if commit.breaking %} — **BREAKING**{% endif %}
{% endfor %}\
{% endfor %}\n
"""

footer = ""
trim = true
postprocessors = []

[git]
conventional_commits = true

# Deliberately false: an unparseable commit message still appears in the
# changelog under "Unfiled" rather than being dropped. A commit that got past
# review with a malformed message (1.3.1) or was silently truncated by GitLab
# at merge time (1.4.3) is exactly the thing we need to SEE in the changelog,
# not have quietly filtered out of it.
filter_unconventional = false

# A commit marked ! or carrying a BREAKING CHANGE: footer (1.3.3) is never
# dropped by a skip rule below.
protect_breaking_commits = true

split_commits = false
filter_commits = false
topo_order = false
sort_commits = "oldest"

# Release tags only (2.4.1, step 8). Any non-release tag the repo may carry
# must never be read as a tag boundary.
tag_pattern = "v[0-9]*"

commit_preprocessors = [
  # Turn the mandatory Jira reference (1.3.1) into a link. Replace the host
  # with the team's actual Jira base URL before first use.
  { pattern = '\\((JIRA-[0-9]+)\\)', replace = "([${1}](https://jira.example.com/browse/${1}))" },
]

# Types are exactly the list fixed in 1.3.1 -- feat, fix, style, chore, docs,
# refactor, test, perf, build, ci, revert. Adding a type here without also
# adding it to 1.3.1 would let a commit type into history that the version-bump
# derivation (2.1) has no rule for.
commit_parsers = [
  { message = "^feat",     group = "Features" },
  { message = "^fix",      group = "Fixes" },
  { message = "^perf",     group = "Performance" },
  { message = "^refactor", group = "Refactoring" },
  { message = "^docs",     group = "Documentation" },
  { message = "^test",     group = "Tests" },
  { message = "^build",    group = "Build System" },
  { message = "^ci",       group = "CI" },
  { message = "^style",    group = "Formatting" },
  { message = "^chore",    group = "Chores" },
  { message = "^revert",   group = "Reverts" },
  { message = ".*",        group = "Unfiled" },
]
```

## Running it

Step 3 of the release process (2.4.1) is this command, run from the release-prep branch:

```bash
git-cliff --unreleased --tag v0.5.0 --prepend CHANGELOG.md
```

`--unreleased` limits output to commits since the last matching tag; `--tag` names the version being cut so the new section gets a heading rather than "Unreleased"; `--prepend` inserts at the top of the existing file, which is what step 4 of 2.4.1 describes as appending the entry.

**Never pass `--first-parent`.** 2.4.2 states this as a rule and it is worth restating next to the command: the umbrella-branch merge exception (1.2.3) is the entire reason individual sub-branch commits are visible on development at all, and first-parent traversal is precisely what would skip them. The changelog would silently lose every commit that came in through an umbrella branch.

## Verifying the version bump

The MINOR-versus-PATCH derivation in 2.1 reads the same commit types this file parses, so git-cliff can be used to check the bump before tagging — if the unreleased section contains a Features group or any entry marked BREAKING, it is a MINOR bump; if it contains only the other groups, it is a PATCH bump:

```bash
git-cliff --unreleased --context | grep -E '"group"|"breaking": true'
```

*Open item, needs team ratification: the Jira base URL in commit_preprocessors is a placeholder and has to be set to the team's real instance before the first release cut, or every ticket link in the changelog will 404. Everything else in this file is usable as written.*
