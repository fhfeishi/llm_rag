# LLMRAG Development Notes

This fork keeps the original PageIndex code for reference while developing the new `llmrag` package in `llmrag/`.

## Git Remotes

- `origin`: your fork, `git@github.com:fhfeishi/llm_rag.git`
- `upstream`: original PageIndex, `git@github.com:VectifyAI/PageIndex.git`

## Suggested Workflow

```powershell
# work on feature branches
git switch -c codex/your-feature

# periodically sync original PageIndex changes
.\llmrag_scripts\sync_upstream.ps1

# run local checks
.\llmrag_scripts\dev_check.ps1

# install llmrag extras for CLI/API work
.\llmrag_scripts\install_llmrag_deps.ps1
```

The intent is to keep `pageindex/`, the root `README.md`, and PageIndex's root config files mostly untouched. New package code lives in `llmrag/`; llmrag documentation and packaging metadata live in `llmrag_info/`; local helper scripts live in `llmrag_scripts/`.
