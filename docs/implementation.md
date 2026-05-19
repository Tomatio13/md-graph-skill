# Markdown GraphRAG Skill 実装方式

このドキュメントは、現在の Markdown GraphRAG Skill が LightRAG をどう初期化し、どの Markdown を投入し、`create` / `query` / `plan` をどう実行するかを説明する。

## 全体像

- この Skill は、ローカルディレクトリ内の Markdown 系ドキュメントを LightRAG ストレージへ変換する。
- 現在の実装は Markdown 専用であり、コードファイルの構文解析や独自 Knowledge Graph 登録は行わない。
- `create` は Markdown を収集し、見出し単位で section chunk を作り、LightRAG の `ainsert(...)` に渡す。
- `query` と `plan` は、作成済みストレージを LightRAG で検索し、グラフとベクトル検索を使って回答を生成する。
- storage ごとに Markdown chunking の最大見出しレベルを選べる。
  - `2`: note、議事録、日記、一般的な prose-oriented Markdown 向け。
  - `3`: リンク集、記事まとめ、媒体別 roundup 向け。

## 実行モード

- `create`
  - 対象ディレクトリを読み込む。
  - Markdown 系ファイルだけを LightRAG ストレージへ登録する。
  - 既存ストレージがある場合は manifest を使って差分更新する。
  - `--markdown-chunk-heading-level {2,3}` で storage ごとの chunk 粒度を指定できる。

- `query`
  - 既存ストレージを読み込む。
  - ユーザーの質問を `rag.aquery(...)` に渡す。
  - LightRAG がグラフとベクトル検索を使って回答を生成する。

- `plan`
  - 既存ストレージを読み込む。
  - ユーザー要求を計画作成用プロンプトに変換する。
  - そのプロンプトを `QueryParam.user_prompt` として渡す。
  - LightRAG がグラフを参照して計画を生成する。

## CLI エントリポイント

実装箇所:

- `markdown-graphrag/scripts/run_repo_graphrag.py`
- `markdown-graphrag/repo_graphrag/runtime.py`

`create` の引数:

- `--target-repo-path`
  - 読み込み対象ディレクトリ。

- `--storage-name`
  - ストレージ名。

- `--markdown-chunk-heading-level {2,3}`
  - その storage に対して使う Markdown chunking の最大見出しレベル。
  - 未指定時は環境設定の既定値を使う。

`query` / `plan` の引数:

- `--storage-name`
- `--user-request`

## LightRAG 初期化

実装箇所:

- `markdown-graphrag/repo_graphrag/initialization/initializer.py`

初期化時に渡している主要な値:

- `working_dir`
  - ストレージディレクトリ。
  - 例: `<skill実行ディレクトリ>/<storage_name>`

- `workspace`
  - LightRAG 内のワークスペース名。
  - `storage_name + "_work"` で作られる。

- `vector_storage`
  - `FaissVectorDBStorage`
  - ベクトル検索用に Faiss を使う。

- `llm_model_func`
  - `complete_graph_create`
  - エンティティ抽出、関係抽出、要約生成に使われる LLM 関数。

- `embedding_func`
  - Hugging Face モデルを使う埋め込み関数。
  - 埋め込みモデルと tokenizer は一度ロードした後に再利用される。

- `addon_params`
  - `language`
    - `english`
  - `entity_types`
    - ドキュメントから抽出するエンティティ種別。
    - 環境変数 `DOC_DEFINITION_LIST` で制御する。

補足:

- `max_parallel_insert=parallel_num`
- `llm_model_max_async=parallel_num`
- `embedding_func_max_async=parallel_num`
- `summary_max_tokens=GRAPH_CREATE_MAX_TOKEN_SIZE`

## LLM プロバイダ

実装箇所:

- `markdown-graphrag/repo_graphrag/llm/llm_client.py`
- `markdown-graphrag/repo_graphrag/llm/openai_client.py`
- `markdown-graphrag/repo_graphrag/llm/azure_openai_client.py`
- `markdown-graphrag/repo_graphrag/llm/anthropic_client.py`
- `markdown-graphrag/repo_graphrag/llm/gemini_client.py`

対応プロバイダ:

- `openai`
- `azure_openai`
- `anthropic`
- `gemini`

主要設定値:

- `GRAPH_CREATE_PROVIDER`
- `GRAPH_ANALYSIS_PROVIDER`
- `GRAPH_CREATE_MODEL_NAME`
- `GRAPH_ANALYSIS_MODEL_NAME`

注意点:

- 現在の `initialize_rag(...)` は `llm_model_func=complete_graph_create` を渡している。
- そのため、LightRAG 内部の抽出系処理は create 系の LLM 関数を使う。
- `plan` は Skill 側で専用プロンプトを付与するが、RAG 実行自体は `rag.aquery(...)` を使う。

## ファイル収集

実装箇所:

- `markdown-graphrag/repo_graphrag/utils/file_reader.py`
- `markdown-graphrag/repo_graphrag/config/settings.py`

現在の処理対象:

- `md`
- `mdx`
- `markdown`
- `DOC_EXT_TEXT_FILES` に追加した拡張子
- special file として設定した無拡張ファイル

現在の除外対象:

- `__pycache__`
- `.git`
- `.github`
- `.venv`
- `node_modules`
- `.DS_Store`
- `Thumbs.db`
- `robots.txt`
- `bac`
- `backup`
- `temp`
- `tmp`

エンコーディング処理:

- まず `utf-8` で読む。
- 失敗した場合は `shift_jis` を試す。
- それでも失敗した場合はそのファイルをスキップする。

## Markdown chunking

実装箇所:

- `markdown-graphrag/repo_graphrag/utils/markdown_chunker.py`
- `markdown-graphrag/repo_graphrag/processors/document_processor.py`

現在の方式:

- Markdown は見出しベースで section chunk に分割する。
- chunk には軽量メタデータを付ける。
  - `Source file: ...`
  - `Section: ...`
- 先頭に見出し前の本文がある場合は `Preamble` として別 chunk にする。

chunk 粒度:

- `max_heading_level=2`
  - `#` / `##` を section 境界に使う。
- `max_heading_level=3`
  - `###` まで section 境界に使う。
- `create --markdown-chunk-heading-level` を指定した場合は、その値を storage 単位で使う。

現在の最適化:

- `MARKDOWN_CHUNK_MIN_SECTION_CHARS`
  - 短すぎる section を除外する。

- `MARKDOWN_CHUNK_SKIP_TOC_SECTIONS`
  - 目次に見える section を除外する。

投入処理:

```python
chunks = split_markdown_sections(
    str(doc_content),
    doc_path,
    max_heading_level=markdown_chunk_heading_level,
)
await rag.ainsert(chunks, file_paths=[doc_path] * len(chunks))
```

LightRAG 側で行われる処理:

- 文書 chunk の保持。
- LLM によるエンティティ抽出。
- LLM による関係抽出。
- 埋め込み生成。
- Key-Value ストレージ、ベクトルストレージ、グラフストレージへの保存。

## 差分更新

実装箇所:

- `markdown-graphrag/repo_graphrag/graph_storage_creator.py`

目的:

- 既存ストレージがある場合に、変更のない Markdown を再処理しない。
- 削除されたファイルや対象外になったファイルの古いデータを消す。
- storage ごとの chunking 設定が変わった場合は、その storage を再構築する。

判定方法:

- 各ドキュメント本文を正規化して `doc-...` 形式の hash を作る。
- `markdown_file_manifest.json` に以下を保存する。
  - `version`
  - `chunking.max_heading_level`
  - `documents` の hash 一覧
- `kv_store_text_chunks.json` から `file_path -> full_doc_id` の対応を読む。
- manifest と現在の hash を比較し、未変更ファイルをスキップする。

再構築条件:

- manifest が存在しない。
- 以前の manifest が旧形式である。
- `chunking.max_heading_level` が今回指定値と異なる。

削除処理:

```python
await rag.adelete_by_doc_id(doc_id)
```

## `create` の実行フロー

実装箇所:

- `markdown-graphrag/repo_graphrag/runtime.py`
- `markdown-graphrag/repo_graphrag/graph_storage_creator.py`

処理の流れ:

1. `storage_name` から storage directory を解決する。
2. LightRAG を初期化する。
3. 対象ディレクトリから Markdown を収集する。
4. manifest と既存 chunk metadata を使って差分判定する。
5. 変更分だけを section chunk 化して `rag.ainsert(...)` へ渡す。
6. 新しい manifest を保存する。
7. storage を finalize し、LLM response cache を drop する。

## `query` の処理

実装箇所:

- `markdown-graphrag/repo_graphrag/runtime.py`

処理:

```python
response = await rag.aquery(query=user_query, param=query_param)
```

`QueryParam` に渡す主要値:

- `mode`
  - `SEARCH_MODE`
  - 既定値は `mix`

- `top_k`
  - `SEARCH_TOP_K`

- `max_total_tokens`
  - `MAX_TOTAL_TOKENS`

- `max_entity_tokens`
  - `MAX_ENTITY_TOKENS`

- `max_relation_tokens`
  - `MAX_RELATION_TOKENS`

特徴:

- Skill 側には query 専用の独自プロンプトはない。
- ユーザー質問をそのまま LightRAG へ渡す。
- storage が存在しない場合は `STORAGE_NOT_FOUND_ERROR_TEMPLATE` を返す。

## `plan` の処理

実装箇所:

- `markdown-graphrag/repo_graphrag/runtime.py`
- `markdown-graphrag/repo_graphrag/prompts.py`

処理:

```python
create_plan_prompt = PLAN_PROMPT_TEMPLATE.format(user_request=user_request)
plan = await rag.aquery(query=user_request, param=query_param)
```

`plan` の特徴:

- `PLAN_PROMPT_TEMPLATE` を `QueryParam.user_prompt` として渡す。
- `query` と同じ storage を検索する。
- 出力は `PLAN_RESPONSE_TEMPLATE` でラップして返す。

## 現在の設計上のポイント

- 実装は Markdown 専用であり、コードパースや Tree-sitter 依存は削除済み。
- グラフの価値は維持するため、文書 chunk は raw text ではなく section 構造を保って投入する。
- 初回 `create` は LightRAG の entity / relation 抽出コストにより重くなり得る。
- 一方で、manifest ベースの差分更新により 2 回目以降の更新コストは抑えられる。
- `level=2` と `level=3` は storage 単位で選べるため、文書コーパスの性質に応じて粒度を分けられる。
  - note、議事録、日記: `level=2`
  - リンク集、記事 roundup、媒体別まとめ: `level=3`
