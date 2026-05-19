import gc
import logging
import os
from logging.handlers import RotatingFileHandler

from repo_graphrag.prompts import (
    GENERAL_ERROR_TEMPLATE,
    GRAPH_STORAGE_RESULT_TEMPLATE,
    PLAN_PROMPT_TEMPLATE,
    PLAN_RESPONSE_TEMPLATE,
    QUERY_RESPONSE_TEMPLATE,
    STORAGE_NOT_FOUND_ERROR_TEMPLATE,
)


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.getMessage().strip() in ("", "\n"):
            return ""
        return super().format(record)


_LOGGER_CONFIGURED = False


def configure_logging(base_dir: str | None = None, log_filename: str = "mcp_server.log") -> logging.Logger:
    global _LOGGER_CONFIGURED

    logger = logging.getLogger()
    if _LOGGER_CONFIGURED:
        return logger

    root_dir = base_dir or os.getcwd()
    log_dir = os.path.join(root_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        os.path.join(log_dir, log_filename),
        maxBytes=1048576,
        backupCount=5,
    )
    formatter = CustomFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    _LOGGER_CONFIGURED = True
    return logger


def log_newline(base_dir: str | None = None, log_filename: str = "mcp_server.log") -> None:
    root_dir = base_dir or os.getcwd()
    log_dir = os.path.join(root_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, log_filename), "a", encoding="utf-8") as f:
        f.write("\n")


def resolve_storage_dir(base_dir: str, storage_name: str) -> str:
    return os.path.join(base_dir, storage_name)


def _load_runtime_dependencies():
    try:
        from lightrag import QueryParam

        from repo_graphrag.config.settings import (
            entity_max_tokens,
            max_total_tokens,
            relation_max_tokens,
            search_mode,
            search_top_k,
        )
        from repo_graphrag.graph_storage_creator import create_graph_storage
        from repo_graphrag.initialization.initializer import initialize_rag
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "Missing runtime dependency. Run `uv sync` and ensure the repository environment is configured."
        ) from e

    return {
        "QueryParam": QueryParam,
        "entity_max_tokens": entity_max_tokens,
        "max_total_tokens": max_total_tokens,
        "relation_max_tokens": relation_max_tokens,
        "search_mode": search_mode,
        "search_top_k": search_top_k,
        "create_graph_storage": create_graph_storage,
        "initialize_rag": initialize_rag,
    }


async def create_graph_storage_entrypoint(
    read_dir_path: str,
    storage_name: str = "storage",
    base_dir: str | None = None,
    markdown_chunk_heading_level: int | None = None,
) -> str:
    runtime_base_dir = base_dir or os.getcwd()
    logger = configure_logging(runtime_base_dir)
    log_newline(runtime_base_dir)
    logger.info("=" * 80)
    logger.info("graph_create tool start")
    logger.info("=" * 80)

    try:
        deps = _load_runtime_dependencies()
        storage_dir_path = resolve_storage_dir(runtime_base_dir, storage_name)
        storage_exists = os.path.exists(storage_dir_path)
        action = "updated" if storage_exists else "created"

        await deps["create_graph_storage"](
            read_dir_path,
            storage_dir_path,
            markdown_chunk_heading_level=markdown_chunk_heading_level,
        )

        result_message = GRAPH_STORAGE_RESULT_TEMPLATE.format(
            read_dir_path=read_dir_path,
            storage_dir_path=storage_dir_path,
            action=action,
        )

        logger.info("")
        logger.info("=" * 80)
        logger.info("graph_create tool completed")
        logger.info("=" * 80)
        log_newline(runtime_base_dir)
        return result_message
    except Exception as e:
        error_message = GENERAL_ERROR_TEMPLATE.format(error=str(e))
        logger.info("")
        logger.error("=" * 80)
        logger.error("graph_create tool error")
        logger.error("=" * 80)
        log_newline(runtime_base_dir)
        return error_message


async def graph_plan_entrypoint(
    user_request: str,
    storage_name: str = "storage",
    base_dir: str | None = None,
) -> str:
    runtime_base_dir = base_dir or os.getcwd()
    logger = configure_logging(runtime_base_dir)
    log_newline(runtime_base_dir)
    logger.info("=" * 80)
    logger.info("graph_plan tool start")
    logger.info("=" * 80)

    storage_dir_path = resolve_storage_dir(runtime_base_dir, storage_name)
    if not os.path.exists(storage_dir_path):
        logger.info("")
        logger.error("=" * 80)
        logger.error("graph_plan tool error: storage not found")
        logger.error("=" * 80)
        log_newline(runtime_base_dir)
        return STORAGE_NOT_FOUND_ERROR_TEMPLATE.format(storage_name=storage_name)

    deps = _load_runtime_dependencies()
    create_plan_prompt = PLAN_PROMPT_TEMPLATE.format(user_request=user_request)
    rag = await deps["initialize_rag"](storage_dir_path)
    query_param = deps["QueryParam"](
        mode=deps["search_mode"],
        user_prompt=create_plan_prompt,
        top_k=deps["search_top_k"],
        max_total_tokens=deps["max_total_tokens"],
        max_entity_tokens=deps["entity_max_tokens"],
        max_relation_tokens=deps["relation_max_tokens"],
    )
    try:
        plan = await rag.aquery(query=user_request, param=query_param)
    finally:
        await rag.finalize_storages()
        await rag.llm_response_cache.drop()
        del rag
        gc.collect()

    result_message = PLAN_RESPONSE_TEMPLATE.format(
        user_request=user_request,
        plan=plan,
        storage_name=storage_name,
    )
    logger.info("")
    logger.info("=" * 80)
    logger.info("graph_plan tool completed")
    logger.info("=" * 80)
    log_newline(runtime_base_dir)
    return result_message


async def graph_query_entrypoint(
    user_query: str,
    storage_name: str = "storage",
    base_dir: str | None = None,
) -> str:
    runtime_base_dir = base_dir or os.getcwd()
    logger = configure_logging(runtime_base_dir)
    log_newline(runtime_base_dir)
    logger.info("=" * 80)
    logger.info("graph_query tool start")
    logger.info("=" * 80)

    storage_dir_path = resolve_storage_dir(runtime_base_dir, storage_name)
    if not os.path.exists(storage_dir_path):
        logger.info("")
        logger.error("=" * 80)
        logger.error("graph_query tool error: storage not found")
        logger.error("=" * 80)
        log_newline(runtime_base_dir)
        return STORAGE_NOT_FOUND_ERROR_TEMPLATE.format(storage_name=storage_name)

    deps = _load_runtime_dependencies()
    rag = await deps["initialize_rag"](storage_dir_path)
    query_param = deps["QueryParam"](
        mode=deps["search_mode"],
        top_k=deps["search_top_k"],
        max_total_tokens=deps["max_total_tokens"],
        max_entity_tokens=deps["entity_max_tokens"],
        max_relation_tokens=deps["relation_max_tokens"],
    )
    try:
        response = await rag.aquery(query=user_query, param=query_param)
    finally:
        await rag.finalize_storages()
        await rag.llm_response_cache.drop()
        del rag
        gc.collect()

    result_message = QUERY_RESPONSE_TEMPLATE.format(
        user_query=user_query,
        response=response,
        storage_name=storage_name,
    )
    logger.info("")
    logger.info("=" * 80)
    logger.info("graph_query tool completed")
    logger.info("=" * 80)
    log_newline(runtime_base_dir)
    return result_message
