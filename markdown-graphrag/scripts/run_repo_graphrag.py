#!/usr/bin/env python3
"""Repo GraphRAG skill runner."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from repo_graphrag.runtime import (  # noqa: E402
    create_graph_storage_entrypoint,
    graph_plan_entrypoint,
    graph_query_entrypoint,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repo GraphRAG skill runner")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    create_parser = subparsers.add_parser("create", help="Create or update graph storage")
    create_parser.add_argument("--target-repo-path", required=True)
    create_parser.add_argument("--storage-name", required=True)
    create_parser.add_argument(
        "--markdown-chunk-heading-level",
        type=int,
        choices=(2, 3),
        help="Max Markdown heading level used for section chunking in this storage",
    )

    query_parser = subparsers.add_parser("query", help="Query existing graph storage")
    query_parser.add_argument("--storage-name", required=True)
    query_parser.add_argument("--user-request", required=True)

    plan_parser = subparsers.add_parser("plan", help="Generate a plan from existing graph storage")
    plan_parser.add_argument("--storage-name", required=True)
    plan_parser.add_argument("--user-request", required=True)

    return parser


async def run_create(
    target_repo_path: str,
    storage_name: str,
    markdown_chunk_heading_level: int | None = None,
) -> int:
    target_repo = Path(target_repo_path).expanduser().resolve()
    if not target_repo.exists():
        print(f"Target repository path does not exist: {target_repo}", file=sys.stderr)
        return 1

    result = await create_graph_storage_entrypoint(
        read_dir_path=str(target_repo),
        storage_name=storage_name,
        base_dir=str(ROOT),
        markdown_chunk_heading_level=markdown_chunk_heading_level,
    )
    print(result)
    return 0 if not result.startswith("An error occurred:") else 1


async def run_query(storage_name: str, user_request: str) -> int:
    result = await graph_query_entrypoint(
        user_query=user_request,
        storage_name=storage_name,
        base_dir=str(ROOT),
    )
    print(result)
    return 0 if not result.startswith("Error:") and not result.startswith("An error occurred:") else 1


async def run_plan(storage_name: str, user_request: str) -> int:
    result = await graph_plan_entrypoint(
        user_request=user_request,
        storage_name=storage_name,
        base_dir=str(ROOT),
    )
    print(result)
    return 0 if not result.startswith("Error:") and not result.startswith("An error occurred:") else 1


async def async_main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "create":
        return await run_create(
            args.target_repo_path,
            args.storage_name,
            args.markdown_chunk_heading_level,
        )
    if args.mode == "query":
        return await run_query(args.storage_name, args.user_request)
    if args.mode == "plan":
        return await run_plan(args.storage_name, args.user_request)

    parser.error(f"Unsupported mode: {args.mode}")
    return 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
