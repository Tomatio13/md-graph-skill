<h1 align="center">MarkdownGraphRAG Skill</h1>

<p align="center">
  グラフベースのMarkdown解析、Q&A、実装計画のためのローカル Agent Skill
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/uv-required-green" alt="uv required">
  <img src="https://img.shields.io/badge/interface-skill--first-black" alt="skill first">
</p>

<p align="center">
  <a href="README_JP.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
  <a href="README.md"><img src="https://img.shields.io/badge/english-document-white.svg" alt="EN doc"></a>
</p>

このリポジトリは、LightRAGを使ってMarkdownを解析・検索するたためのAgent Skillsです。

## ✨ 用途

Markdown GraphRAG は、ローカルリポジトリをグラフストレージ化し、そのグラフを使ってリポジトリ解析を行います。

- `create`
  - ローカルリポジトリのグラフストレージを作成または更新する
- `query`
  - グラフを使ってリポジトリに関する質問へ回答する
- `plan`
  - 変更要求に対してグラフに基づく実装計画を生成する

ランタイムパッケージと Skill ローカル用ファイルはこのリポジトリに同梱されているため、`skills` ディレクトリへそのまま配置できます。

## 🚀 インストール

このリポジトリをローカルの `skills` ディレクトリへ直接 clone してください。

```bash
git clone <REPOSITORY_URL> ~/.codex/skills/repo-graphrag
```

別の Coding Agnet を使っている場合は、`<AGENT_HOME>/skills/repo-graphrag` に clone してください。

## 📘 使い方

次のような場面でこの Skill を使います。

- テキストドキュメントについてグラフベースで質問したい

`create`、`query`、`plan` の実行フロー、`.env`、ランタイム設定の詳細は [`repo-graphrag/SKILL.md`](repo-graphrag/SKILL.md) を参照してください。

## 🧭 実践ガイド

### grep vs Graph Search — いつどちらを使うか

Graph Storage は万能ではなく、grep やキーワード検索と使い分けることで最も効果を発揮します。

| 目的 | grep | Graph |
|------|------|-------|
| キーワードが含まれるファイルを探す | ✅ | △ |
| 特定文字列の出現箇所を全列挙 | ✅ | × |
| 「〇〇と××がどう繋がっているか」を知りたい | × | ✅ |
| 検索キーワードを思いつかない繋がりを発見 | × | ✅ |
| 抽象テーマ（セキュリティ、コスト等）で横断検索 | △ | ✅ |
| 影響範囲の波及経路を追跡 | × | ✅ |

**使い分けの目安:**

- ファイル数が 10〜20 でキーワードが明確 → grep で十分な場合がある
- ファイル数が 100+ または関係性を知りたい → Graph の価値が増す
- セッションで両方を併用するのが実践的なベストプラクティス

### 実践ユースケース

#### 1. 横断テーマ分析

複数ドキュメントをまたいで、特定技術のトレンド変遷や話題の変化を追う。

```bash
python3 scripts/run_md_graph.py query \
  --storage-name my-storage \
  --query-mode hybrid \
  --response-mode context \
  --user-request "Codex CLI関連記事の内容を時系列で整理して"
```

各ドキュメントの日付ファイル名やメタデータと組み合わせることで、技術の「導入期 → 試用期 → 比較検討 → 定着」といった成熟曲線を可視化できる。

#### 2. エンティティ中心の深掘り

特定の技術・概念に絞って、周辺エンティティと関係性を集中的に取得する。

```bash
python3 scripts/run_md_graph.py query \
  --storage-name my-storage \
  --query-mode local \
  --response-mode context \
  --user-request "MCP Serverの具体的な活用事例を教えて"
```

キーワード検索では拾えない繋がり（例: 「MCP → Unity → ゲーム開発」）が、グラフのエッジとして見つかる。

#### 3. 影響範囲の追跡

ある問題（セキュリティ脆弱性、アーキテクチャ変更など）が、どのエンティティやシステムに波及するかを関係性エッジで追跡する。

```bash
python3 scripts/run_md_graph.py query \
  --storage-name my-storage \
  --query-mode hybrid \
  --response-mode context \
  --user-request "MCPのセキュリティ問題がどのシステムに影響を与えるか"
```

個別の記事としてはバラバラに見えても、グラフ上では一つの懸念が開発ツール → 本番インフラ → ビジネス領域まで波及している構造が見える。

#### 4. 差分アップデート

新規ファイルを追加した後、再度 `create` を実行すると**差分のみ**を取り込んで既存グラフを更新する。

```bash
# 新しいファイルを追加
cp new_articles/*.md /path/to/documents/

# 差分更新
python3 scripts/run_md_graph.py create \
  --target-repo-path /path/to/documents \
  --storage-name my-storage
```

ストレージの再構築は不要。数百ファイルの規模でも追加分だけが処理される。

### 「繋がり」とは何か

grep と Graph Search の最大の違いは、\*\*「何を見つけるか」\*\*にある。

- **grep** は「文字列の一致」を見つける。「MCP」という文字がどのファイルにあるかは分かるが、「MCPが他の技術とどう関係しているか」は分からない。
- **Graph** は「エンティティ間の関係性（エッジ）」を見つける。

Graph Storage が構築する関係性は、次のような形で表現される:

```
[Claude Code] → [Unity MCP]     （UnityをMCP経由で操作）
[Claude Code] → [MCP Parity]    （Codex並走時のパリティ問題）
[MCP Server]  → [Security Cliff]（本番運用時のセキュリティ要件）
```

このエッジを追うことで、「MCP」という一つの概念が、ゲーム開発・並走運用・セキュリティ・金融取引など、一見無関係に見える領域とどう繋がっているかが見える。これが Graph Search の価値の核心。

### 推奨ワークフロー

```
1. create  ─ ストレージ構築（初回のみ）
2. query   ─ context モードで検索コンテキスト取得（デフォルト）
3. grep    ─ 具体的なキーワード確認や時系列整理は併用
4. create  ─ 新ファイル追加時に差分更新
```

`query` のデフォルトは `context` モード。構造化された検索コンテキスト JSON を取得し、呼び出し側のエージェントが最終回答を組み立てる。`answer` モードは Graph 自身に回答生成させたい場合にのみ使用する。

## 🙏 謝辞

この Skill は [`repo-graphrag-mcp`](https://github.com/yumeiriowl/repo-graphrag-mcp) の考え方とワークフローをベースに、MCP サーバから Agent Skill 向けの構成へ適応したものです。グラフベースのリポジトリ解析アプローチと参照実装を公開している元プロジェクトに感謝します。
