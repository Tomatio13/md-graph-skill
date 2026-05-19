<h1 align="center">MarkdownGraphRAG Skill</h1>

<p align="center">
  Local Agent Skill for graph-backed Markdown analysis, Q&amp;A, and planning.
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

This repository is an Agent Skill that uses LightRAG to parse and search Markdown documents.

## ✨ Purpose

Markdown GraphRAG turns a local document set into graph storage and uses that graph for analysis.

- `create`
  - build or refresh graph storage for a local document set
- `query`
  - answer document questions from the graph
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

- ask graph-backed questions about text documents

Execution flow, `.env`, and runtime details for `create`, `query`, and `plan` are documented in [`repo-graphrag/SKILL.md`](repo-graphrag/SKILL.md).

## 🧭 Practical Guide

### grep vs Graph Search — When to Use Which

Graph Storage is not a silver bullet. It works best when combined with grep and keyword search.

| Goal | grep | Graph |
|------|------|-------|
| Find files containing a keyword | ✅ | △ |
| Enumerate every occurrence of a string | ✅ | × |
| Discover how X relates to Y | × | ✅ |
| Find connections you didn't think to search for | × | ✅ |
| Cross-document search on abstract themes (security, cost, etc.) | △ | ✅ |
| Trace the propagation path of an impact | × | ✅ |

**Rule of thumb:**

- 10–20 files with clear keywords → grep may be sufficient
- 100+ files or you need relationships → Graph adds real value
- Combining both in a session is the practical best practice

### Practical Use Cases

#### 1. Cross-Document Theme Analysis

Trace how a specific technology evolves across multiple documents over time.

```bash
python3 scripts/run_md_graph.py query \
  --storage-name my-storage \
  --query-mode hybrid \
  --response-mode context \
  --user-request "Organize Codex CLI-related articles chronologically"
```

Combined with date-stamped filenames or metadata, this reveals maturity curves: "introduction → trial → comparison → adoption."

#### 2. Entity-Centered Deep Dive

Focus on a specific technology or concept and retrieve surrounding entities and relationships.

```bash
python3 scripts/run_md_graph.py query \
  --storage-name my-storage \
  --query-mode local \
  --response-mode context \
  --user-request "Show concrete use cases of MCP Server"
```

Connections that keyword search would miss (e.g., "MCP → Unity → game development") surface as graph edges.

#### 3. Impact Propagation Tracing

Track how a problem (security vulnerability, architecture change, etc.) propagates across entities and systems via relationship edges.

```bash
python3 scripts/run_md_graph.py query \
  --storage-name my-storage \
  --query-mode hybrid \
  --response-mode context \
  --user-request "Which systems are affected by MCP security issues?"
```

What looks like unrelated articles individually reveals, on the graph, a single concern propagating from dev tools → production infra → business domains.

#### 4. Incremental Updates

After adding new files, run `create` again to process **only the delta** and update the existing graph.

```bash
# Add new files
cp new_articles/*.md /path/to/documents/

# Incremental update
python3 scripts/run_md_graph.py create \
  --target-repo-path /path/to/documents \
  --storage-name my-storage
```

No full rebuild needed. Even at hundreds-of-files scale, only new additions are processed.

### What Are "Connections"?

The key difference between grep and Graph Search is **what they find**.

- **grep** finds "string matches." It tells you which files contain "MCP" but not how MCP relates to other technologies.
- **Graph** finds "entity relationships" (edges).

Graph Storage represents relationships like this:

```
[Claude Code] → [Unity MCP]     (control Unity via MCP)
[Claude Code] → [MCP Parity]    (parity issues in Codex parallel setup)
[MCP Server]  → [Security Cliff] (production security requirements)
```

Following these edges reveals how a single concept like "MCP" connects to seemingly unrelated areas — game development, parallel tooling, security, financial trading. This is the core value of Graph Search.

### Recommended Workflow

```
1. create  ─ Build storage (first time only)
2. query   ─ Retrieve search context in context mode (default)
3. grep    ─ Supplement with keyword confirmation and chronological sorting
4. create  ─ Incremental update when new files are added
```

The default `query` mode is `context`. It returns structured search context JSON for the calling agent to assemble the final answer. Use `answer` mode only when you want Graph to generate the final response text itself.

## 🙏 Acknowledgments

This skill is based on the ideas and workflow of [`repo-graphrag-mcp`](https://github.com/yumeiriowl/repo-graphrag-mcp), adapted from an MCP server into an Agent Skill oriented package. Thanks to the original project for the graph-backed repository analysis approach and reference implementation.
