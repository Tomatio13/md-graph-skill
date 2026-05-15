<h1 align="center">Repo GraphRAG Skill</h1>

<p align="center">
  Local Agent Skill for graph-backed repository analysis, Q&amp;A, and planning.
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

This repository packages Repo GraphRAG as a local Agent Skill instead of an MCP server.

## ✨ Purpose

Repo GraphRAG turns a local repository into graph storage and uses that graph for repository analysis.

- `create`
  - build or refresh graph storage for a local repository
- `query`
  - answer repository questions from the graph
- `plan`
  - generate graph-backed implementation plans for change requests

The runtime package and skill-local files are bundled here so the skill can be installed directly into your `skills` directory.

## 🚀 Install

Clone this repository directly into your local `skills` directory.

```bash
git clone <REPOSITORY_URL> ~/.codex/skills/repo-graphrag
```

If you use a different Coding Agent home, clone into `<AGENT_HOME>/skills/repo-graphrag` instead.

## 📘 Usage

Use this skill when you want to:

- create graph storage for a repository before analysis
- ask graph-backed questions about code and text documents in a repository
- generate implementation plans grounded in repository structure

Execution flow, `.env`, and runtime details for `create`, `query`, and `plan` are documented in [`repo-graphrag/SKILL.md`](repo-graphrag/SKILL.md).

## 🙏 Acknowledgments

This skill is based on the ideas and workflow of [`repo-graphrag-mcp`](https://github.com/yumeiriowl/repo-graphrag-mcp), adapted from an MCP server into an Agent Skill oriented package. Thanks to the original project for the graph-backed repository analysis approach and reference implementation.
