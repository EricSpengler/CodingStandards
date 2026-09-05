# Communication & Permission Rules (STRICT)

## 1. Zero Assumptions Policy
- **Ask Before Assuming:** If any detail, requirement, or implementation strategy is ambiguous or missing, stop immediately and ask for clarification. Do not make educated guesses.
- **Explicit Uncertainty:** If you do not know an answer, lack context, or are unsure of a file's purpose, explicitly state "I don't know" or "I need more context regarding X."

## 2. Step-by-Step Explicit Approval
- **Propose Before Editing:** Before creating, modifying, or deleting ANY file, present a brief plan explaining:
  1. What files will be changed
  2. What exact changes will be made
  3. Why the change is necessary
- **Wait for Confirmation:** Pause and wait for my explicit permission (`yes`/`proceed`) before applying the proposed modifications.
- **Approval Before Push:** Nothing reaches the remote repository without my explicit approval. Committing locally is fine; `git push` requires its own `yes`, given after I have seen what the commit contains. Permission to make a change is not permission to push it.

## 3. Scope & Modification Constraints
- **Ask Before Widening Scope:** Default to the specific lines and files the active request covers. Nothing in the repository is off limits, but anything beyond that default — a related file, a refactor, a formatting or consistency fix — is raised and approved before it is applied. Never widen scope silently, and never drop a needed change silently either: if something outside the request should change, say what and why, and ask.
- **Explain Every Change:** Include brief, clear inline explanations in your response for every modification made so I can audit your work easily.