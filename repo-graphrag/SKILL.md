---
name: repo-graphrag
description: Build or refresh Repo GraphRAG storage for a local repository, or use existing storage for graph-backed repository Q&A and implementation planning. Use when the task explicitly needs graph storage creation, graph-backed answers, or graph-backed plans.
compatibility: Requires Python 3.11+, uv, and configured LLM environment variables. The runtime package is bundled in this directory.
metadata:
  product: repo-graphrag
  modes: create,query,plan
---

# Repo GraphRAG

Repo GraphRAG converts repository code and text documents into graph storage, then uses that storage for repository Q&A and implementation planning.

## When to use

- The user wants to build or refresh graph storage for a local repository
- The user wants graph-backed questions answered about a repository
- The user wants graph-backed implementation planning for a repository

## Inputs

Normalize the request into:

- `mode`
  - `create`
  - `query`
  - `plan`
- `target_repo_path`
- `storage_name`
  - default: `storage`
- `user_request`
  - required for `query` and `plan`
  - optional for `create`

## References

- Use [references/modes.md](references/modes.md) for mode-specific behavior
- Use [references/configuration.md](references/configuration.md) for environment and storage rules
- Skill-local publishing files are bundled: `.env.example`, `.gitignore`, `LICENSE`, `agents/openai.yaml`, `pyproject.toml`, and `repo_graphrag/`

## Workflow

1. Normalize the request into `mode`, `target_repo_path`, `storage_name`, and `user_request`.
2. Verify that `.env` exists and that required provider settings are configured.
3. If `mode` is `query` or `plan`, verify that the target storage exists.
4. If the required storage does not exist, recommend running `create` first.
5. Run the local helper:
   `scripts/run_repo_graphrag.py`
6. Return:
   - `create`: storage name, target path, and create or update result
   - `query`: the repository answer
   - `plan`: the stepwise implementation plan

## Execution notes

- Prefer `create` when storage does not exist yet.
- Stop and ask for configuration if `.env` or provider credentials are missing.
- Keep examples and helper behavior aligned with the actual runtime state.

## Examples

- "Create graph storage for this repository"
- "Use this storage to explain the main classes"
- "Create a plan to add authentication to this repository"
