# Configuration

## Environment

- Python 3.11+
- `uv`
- この skill ディレクトリで `uv sync` を実行した依存関係
- この skill ディレクトリ直下の `.env` に設定された LLM provider 関連値

## Storage

- storage はこの skill の実行ディレクトリ基準で作成・参照される
- `create` 実行時は `storage_name` を指定する
- `query` と `plan` は既存 storage が前提

## Current limitations

- 実行には LLM provider と `.env` 設定が必要
- storage 未作成のまま `query` `plan` を呼ぶと storage not found error を返す
- 初回利用時は `.env.example` から `.env` を作成する必要がある

## Validation targets

- `SKILL.md` frontmatter が Agent Skills 仕様に沿うこと
- `SKILL.md` から参照する `references/` と `scripts/` が存在すること
- `SKILL.md` の記述が実装済み状態と矛盾しないこと
