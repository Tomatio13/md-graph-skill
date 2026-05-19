# markdown-graphrag

Markdown-focused GraphRAG skill for building and querying LightRAG storage from repository documentation.

## Scope

- Indexes Markdown-oriented documents such as `.md`, `.mdx`, and `.markdown`
- Skips source-code parsing and code/document entity merging
- Supports `create`, `query`, and `plan` modes through `scripts/run_repo_graphrag.py`

## Behavior

- `create` reads Markdown files, updates storage incrementally, and inserts document content into LightRAG
- `query` answers questions against an existing storage
- `plan` generates implementation plans against an existing storage
- `create` accepts `--markdown-chunk-heading-level {2,3}` per storage
- If `--markdown-chunk-heading-level` is omitted, the runtime uses `.env` value `MARKDOWN_CHUNK_MAX_HEADING_LEVEL`

## Notes

- The default document extensions are `md`, `mdx`, and `markdown`
- `MARKDOWN_CHUNK_MAX_HEADING_LEVEL` must be `2` or `3`
- Recommended default:
  - `2` for notes, meeting logs, diaries, and prose-oriented Markdown
  - `3` for link collections, article roundups, and media digest Markdown
- Batch wait between document inserts defaults to `0.0` seconds
- Code-oriented dependencies and processors have been removed from this package
