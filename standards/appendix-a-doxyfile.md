# Appendix A: Example Doxyfile

```ini
PROJECT_NAME           = "<project name>"        # C-46, from the project profile
OUTPUT_DIRECTORY       = docs/generated
INPUT                  = core gui docs/namespaces.h   # C-28, C-31: project source roots
RECURSIVE              = YES

# Comment style: explicit /** @brief ... */ everywhere (5.1) -- don't infer
# a brief from the first sentence of an undecorated comment block.
JAVADOC_AUTOBRIEF      = NO

# Full-codebase documentation coverage (5.2) -- extract and warn on private/protected members too, not just public.
EXTRACT_ALL            = NO
EXTRACT_PRIVATE        = YES
EXTRACT_PRIV_VIRTUAL   = YES
EXTRACT_STATIC         = YES
EXTRACT_LOCAL_CLASSES  = YES

# Surface every undocumented entity as a warning (5.2, 5.3).
WARN_IF_UNDOCUMENTED   = YES
WARN_IF_INCOMPLETE_DOC = YES
WARN_NO_PARAMDOC       = YES  # 5.3: every parameter requires @param, no exceptions

GENERATE_HTML          = YES
GENERATE_LATEX         = NO
GENERATE_XML           = NO
```
