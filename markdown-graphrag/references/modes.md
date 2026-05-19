# Modes

## create

### Purpose

指定したローカル repository の Markdown 文書を解析し、graph storage を作成または更新する。

### Required inputs

- `target_repo_path`
- `storage_name`

### Current implementation

`scripts/run_repo_graphrag.py create ...` は同梱された `repo_graphrag.runtime` の entrypoint を呼び出す。

### Behavior

- Markdown 系ファイルのみ読み込む
- 見出し単位で section chunk に分割する
- `markdown_file_manifest.json` を使って増分更新する

### Example

```bash
python3 scripts/run_repo_graphrag.py create \
  --target-repo-path /absolute/path/to/repo \
  --storage-name my-storage
```

## query

### Purpose

既存 storage を使って repository の Markdown 文書に関する質問に答える。

### Required inputs

- `storage_name`
- `user_request`

### Current implementation

shared runtime を通して実行できる。

### Behavior

- storage 存在確認
- graph-backed Q&A 実行
- 回答文返却

### Example

```bash
python3 scripts/run_repo_graphrag.py query \
  --storage-name my-storage \
  --user-request "主要なセクションを説明して"
```

## plan

### Purpose

既存 storage を使って repository 文書を踏まえた実装計画を返す。

### Required inputs

- `storage_name`
- `user_request`

### Current implementation

shared runtime を通して実行できる。

### Behavior

- storage 存在確認
- graph-backed planning 実行
- 計画文返却

### Example

```bash
python3 scripts/run_repo_graphrag.py plan \
  --storage-name my-storage \
  --user-request "認証を追加したい"
```
