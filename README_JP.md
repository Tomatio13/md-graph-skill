<h1 align="center">Repo GraphRAG Skill</h1>

<p align="center">
  グラフベースのリポジトリ解析、Q&A、実装計画のためのローカル Agent Skill
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

このリポジトリは、Repo GraphRAG を MCP サーバではなくローカル Agent Skill として利用できるようにパッケージしたものです。

## ✨ 用途

Repo GraphRAG は、ローカルリポジトリをグラフストレージ化し、そのグラフを使ってリポジトリ解析を行います。

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

- 解析前にリポジトリのグラフストレージを作成したい
- コードやテキストドキュメントについてグラフベースで質問したい
- リポジトリ構造に基づいた実装計画を作りたい

`create`、`query`、`plan` の実行フロー、`.env`、ランタイム設定の詳細は [`repo-graphrag/SKILL.md`](repo-graphrag/SKILL.md) を参照してください。

## 🙏 謝辞

この Skill は [`repo-graphrag-mcp`](https://github.com/yumeiriowl/repo-graphrag-mcp) の考え方とワークフローをベースに、MCP サーバから Agent Skill 向けの構成へ適応したものです。グラフベースのリポジトリ解析アプローチと参照実装を公開している元プロジェクトに感謝します。
