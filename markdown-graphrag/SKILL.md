---
name: markdown-graphrag
description: Build or refresh Markdown GraphRAG storage for a local repository, or use existing storage for graph-backed repository Q&A and implementation planning. Use when the task explicitly needs graph storage creation, graph-backed answers, or graph-backed plans.
compatibility: Requires Python 3.11+, uv, and configured LLM environment variables. The runtime package is bundled in this directory.
metadata:
  product: markdown-graphrag
  modes: create,query,plan
---

# Markdown GraphRAG

Markdown GraphRAG converts repository Markdown documents into graph storage, then uses that storage for repository Q&A and implementation planning.

## When to use

- The user wants to build or refresh graph storage for a local repository
- The user wants graph-backed questions answered about repository documentation
- The user wants graph-backed implementation planning based on repository documentation

## Inputs

Normalize the request into:

- `mode`
  - `create`
  - `query`
  - `plan`
- `target_repo_path`
- `storage_name`
  - default: `storage`
- `markdown_chunk_heading_level`
  - `2` for note-like documents, meeting notes, diaries, and general prose-oriented Markdown
  - `3` for link collections, article digests, media roundups, and Markdown where each `###` heading is a distinct item
- `user_request`
  - required for `query` and `plan`
  - optional for `create`

## References

- Use [references/modes.md](references/modes.md) for mode-specific behavior
- Use [references/configuration.md](references/configuration.md) for environment and storage rules
- Skill-local publishing files are bundled: `agents/openai.yaml`, `pyproject.toml`, and `repo_graphrag/`

## Workflow

1. Normalize the request into `mode`, `target_repo_path`, `storage_name`, `markdown_chunk_heading_level`, and `user_request`.
2. Verify that `.env` exists and that required provider settings are configured.
3. If `mode` is `create`, ask the user what kind of Markdown corpus they are indexing before running the helper.
   - Ask in practical terms, for example: `Is this corpus note-like, or is it more of a link collection or article roundup?`
   - Recommend `level=2` for note-like corpora.
   - Recommend `level=3` for link collections and article roundup corpora.
   - If the user already specified a level explicitly, use it without re-asking.
4. If `mode` is `query` or `plan`, verify that the target storage exists.
5. If the required storage does not exist, recommend running `create` first.
6. Run the local helper:
   `scripts/run_repo_graphrag.py`
7. Return:
   - `create`: storage name, target path, and create or update result
   - `query`: the repository answer
   - `plan`: the stepwise implementation plan

## Execution notes

- Prefer `create` when storage does not exist yet.
- Stop and ask for configuration if `.env` or provider credentials are missing.
- The runtime indexes Markdown-oriented files only; do not describe code parsing behavior.
- For `create`, do not silently choose between heading level `2` and `3` when the corpus shape is unclear; ask the user.
- Keep examples and helper behavior aligned with the actual runtime state.

## Examples

- "Create graph storage for this repository"
- "Use this storage to explain the main documented sections"
- "Create a plan to add authentication to this repository"
