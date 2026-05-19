# Configuration

## Environment

- Python 3.11+
- `uv`
- この skill ディレクトリで `uv sync` を実行した依存関係
- この skill ディレクトリ直下の `.env` に設定された LLM provider 関連値

## Storage

- storage はこの skill の実行ディレクトリ基準で作成・参照される
- `create` 実行時は `storage_name` を指定する
- `create` 実行時は `--markdown-chunk-heading-level {2,3}` を指定できる
- `--markdown-chunk-heading-level` を省略した場合は `.env` の `MARKDOWN_CHUNK_MAX_HEADING_LEVEL` を使う
- `MARKDOWN_CHUNK_MAX_HEADING_LEVEL` は `2` または `3` でなければならない
- `query` と `plan` は既存 storage が前提
- `create` 実行時は Markdown 系ファイルだけを対象にする
- Markdown は見出し単位で section chunk に分割して投入する
- workspace には `markdown_file_manifest.json` を保存し、増分更新判定に使う

## Current limitations

- 実行には LLM provider と `.env` 設定が必要
- storage 未作成のまま `query` `plan` を呼ぶと storage not found error を返す
- 初回利用時は `.env.example` から `.env` を作成する必要がある
- source code parsing は行わない
- code/document merge は行わない
- 既存 storage に manifest が無い場合、最初の `create` は全 Markdown を再投入する

## Chunk level guide

- `2`
  - notes
  - meeting logs
  - diaries
  - general prose-oriented Markdown

- `3`
  - link collections
  - article roundups
  - media digest Markdown

## Validation targets

- `SKILL.md` frontmatter が Agent Skills 仕様に沿うこと
- `SKILL.md` から参照する `references/` と `scripts/` が存在すること
- `SKILL.md` の記述が実装済み状態と矛盾しないこと
