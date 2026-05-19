import os
from dotenv import load_dotenv


# Load .env file
load_dotenv()

# Helper: get env var and cast to type
def get_config_value(key: str, default="__REQUIRED__", var_type=str):
    """Get env var and cast to the specified type."""
    value = os.getenv(key)
    
    # If not set
    if value is None:
        if default == "__REQUIRED__":
            raise ValueError(f"Environment variable {key} is not set. Please check your .env file.")
        # If default already matches the type, return as is
        if var_type != str and not isinstance(default, str):
            return default
        # Cast string default to the specified type
        if var_type == bool:
            # Bool: treat 'true', '1', 'yes', 'on' as True
            return str(default).lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            # Int: cast default
            return int(default)
        elif var_type == float:
            # Float: cast default
            return float(default)
        else:
            # String/other: return default as is
            return default
    
    # Cast provided value
    if var_type == bool:
        # Bool: 'true', '1', 'yes', 'on' => True
        return value.lower() in ('true', '1', 'yes', 'on')
    elif var_type == int:
        # Int: cast string to int
        return int(value)
    elif var_type == float:
        # Float: cast string to float
        return float(value)
    else:
        # String/other: return string
        return value


def require_allowed_int(name: str, value: int, allowed_values: tuple[int, ...]) -> int:
    """Validate that an integer config value is one of the allowed choices."""
    if value not in allowed_values:
        allowed_text = ", ".join(str(item) for item in allowed_values)
        raise ValueError(f"{name} must be one of: {allowed_text}. Got: {value}")
    return value

# ==============================================================================
# API Keys & Provider Settings
# ==============================================================================
# LLM providers (separate for CREATE and ANALYSIS)
graph_create_provider = get_config_value("GRAPH_CREATE_PROVIDER", str)  # "anthropic" or "azure_openai" or "openai" or "gemini"
graph_analysis_provider = get_config_value("GRAPH_ANALYSIS_PROVIDER", str)  # "anthropic" or "azure_openai" or "openai" or "gemini"

# API keys per provider
anthropic_api_key = get_config_value("ANTHROPIC_API_KEY", None, str)
azure_openai_api_key = get_config_value("AZURE_OPENAI_API_KEY", None, str)
openai_api_key = get_config_value("OPENAI_API_KEY", None, str)
openai_base_url = get_config_value("OPENAI_BASE_URL", None, str)
gemini_api_key = get_config_value("GEMINI_API_KEY", None, str)

# Azure endpoint and API version (when using Azure provider)
azure_endpoint = get_config_value("AZURE_OPENAI_ENDPOINT", None, str)
azure_api_version = get_config_value("AZURE_API_VERSION", None, str)

# Providers in use
used_providers = {graph_create_provider, graph_analysis_provider}

# Validate required API keys for used providers
for provider in used_providers:
    if provider == "anthropic" and not anthropic_api_key:
        raise ValueError(f"Provider '{provider}' is selected but ANTHROPIC_API_KEY is not set.")
    elif provider == "azure_openai" and not azure_openai_api_key:
        raise ValueError(f"Provider '{provider}' is selected but AZURE_OPENAI_API_KEY is not set.")
    elif provider == "openai" and not (openai_api_key or openai_base_url):
        raise ValueError(f"Provider '{provider}' is selected but neither OPENAI_API_KEY nor OPENAI_BASE_URL is set.")
    elif provider == "gemini" and not gemini_api_key:
        raise ValueError(f"Provider '{provider}' is selected but GEMINI_API_KEY is not set.")

# ==============================================================================
# LLM Settings
# ==============================================================================
# Model names
graph_create_model_name = get_config_value("GRAPH_CREATE_MODEL_NAME")

graph_analysis_model_name = get_config_value("GRAPH_ANALYSIS_MODEL_NAME")

# Max output tokens for CREATE (entity extraction, summaries, etc.)
graph_create_max_token_size = get_config_value("GRAPH_CREATE_MAX_TOKEN_SIZE", "4096", int)

# Max output tokens for ANALYSIS (plans, answers, etc.)
graph_analysis_max_token_size = get_config_value("GRAPH_ANALYSIS_MAX_TOKEN_SIZE", "8192", int)

# ==============================================================================
# Embedding Settings
# ==============================================================================
embedding_model_name = get_config_value("EMBEDDING_MODEL_NAME", "BAAI/bge-m3", str)
embedding_dim = get_config_value("EMBEDDING_DIM", "1024", int)
embedding_max_token_size = get_config_value("EMBEDDING_MAX_TOKEN_SIZE", "2048", int)

# Optional Hugging Face Hub token (for authenticated/private models)
huggingface_hub_token = get_config_value("HUGGINGFACE_HUB_TOKEN", None, str)

# ==============================================================================
# Performance Settings
# ==============================================================================
# Concurrency
parallel_num = get_config_value("PARALLEL_NUM", "3", int)

# Chunk max tokens
chunk_max_tokens = get_config_value("CHUNK_MAX_TOKENS", "2048", int)

# Min request interval (sec)
rate_limit_min_interval = get_config_value("RATE_LIMIT_MIN_INTERVAL", "1.0", float)

# Wait time on rate-limit errors (sec)
rate_limit_error_wait_time = get_config_value("RATE_LIMIT_ERROR_WAIT_TIME", "3.0", float)

# Wait time between document batches (sec)
doc_batch_wait_seconds = get_config_value("DOC_BATCH_WAIT_SECONDS", "0.0", float)

# Maximum Markdown heading level that starts a new chunk
markdown_chunk_max_heading_level = require_allowed_int(
    "MARKDOWN_CHUNK_MAX_HEADING_LEVEL",
    get_config_value("MARKDOWN_CHUNK_MAX_HEADING_LEVEL", "2", int),
    (2, 3),
)

# Minimum section body length required to keep a Markdown chunk
markdown_chunk_min_section_chars = get_config_value("MARKDOWN_CHUNK_MIN_SECTION_CHARS", "120", int)

# Whether to skip table-of-contents style sections
markdown_chunk_skip_toc_sections = get_config_value("MARKDOWN_CHUNK_SKIP_TOC_SECTIONS", "true", bool)

# ==============================================================================
# Planning/Query Settings
# ==============================================================================
# Retrieval/Search (GraphRAG)
search_top_k = get_config_value("SEARCH_TOP_K", "40", int)
search_mode = get_config_value("SEARCH_MODE", "mix", str)

# Token budgets (applied to both planning and query)
# Maximum total token budget for a single query context (entities + relations + chunks + system prompt)
max_total_tokens = get_config_value("MAX_TOTAL_TOKENS", "30000", int)

# Optional advanced budgets for entity and relation contexts
entity_max_tokens = get_config_value("MAX_ENTITY_TOKENS", "6000", int)
relation_max_tokens = get_config_value("MAX_RELATION_TOKENS", "8000", int)

# ==============================================================================
# Document Extensions
# ==============================================================================
# Extensions treated as documents
doc_ext_text_files_env = get_config_value("DOC_EXT_TEXT_FILES", "md,mdx,markdown", str)
doc_ext_text_files = [ext.strip() for ext in doc_ext_text_files_env.split(",") if ext.strip()]

# Special file names without extension
doc_ext_special_files_env = get_config_value("DOC_EXT_SPECIAL_FILES", "readme,changelog", str)
doc_ext_special_files = [file.strip().lower() for file in doc_ext_special_files_env.split(",") if file.strip()]

# Group non-code/doc files
doc_ext_dict = {
    "text_file": doc_ext_text_files,
    "special_files": doc_ext_special_files
}

# ==============================================================================
# Document Entity Extraction Settings
# ==============================================================================
# Entity types to extract from documents
document_definition_list_env = get_config_value("DOC_DEFINITION_LIST", "class_name,function_name,method_name", str)
document_definition_list = [item.strip() for item in document_definition_list_env.split(",") if item.strip()]

# ==============================================================================
# File/Directory Exclusion Settings
# ==============================================================================
# Files/directories to exclude
no_process_list_env = get_config_value("NO_PROCESS_LIST", "", str)
no_process_file_list = no_process_list_env.split(",") if no_process_list_env else [
    "__pycache__",
    ".git",
    ".github",
    ".venv", 
    "node_modules",
    ".DS_Store",
    "Thumbs.db",
    "robots.txt",
    "bac",
    "backup",
    "temp",
    "tmp"
]

# Remove empty entries
no_process_file_list = [item.strip() for item in no_process_file_list if item.strip()]

# ==============================================================================
# LLM/Embedding Max Async Settings
# ==============================================================================
# Max concurrent requests for LLM and embedding match parallel_num
llm_model_max_async = parallel_num
embedding_func_max_async = parallel_num
