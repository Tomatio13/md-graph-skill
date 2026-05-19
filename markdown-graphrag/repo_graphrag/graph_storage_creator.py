import gc
import logging
import os
import json
from typing import Dict
from lightrag import LightRAG
from lightrag.utils import compute_mdhash_id, sanitize_text_for_encoding
from .initialization.initializer import initialize_rag
from .config.settings import markdown_chunk_max_heading_level
from .utils.file_reader import read_dir
from .processors.document_processor import doc_to_storage


logger = logging.getLogger(__name__)
_DOC_MANIFEST_FILENAME = "markdown_file_manifest.json"
_MANIFEST_VERSION = 2

async def create_graph_storage(
    read_dir_path: str,
    storage_dir_path: str,
    markdown_chunk_heading_level: int | None = None,
):
    """
    Create or update GraphRAG storage.

    Args:
        read_dir_path: Target directory path to read from
        storage_dir_path: Storage directory path
    """
    rag = None
    try:
        effective_heading_level = (
            markdown_chunk_heading_level or markdown_chunk_max_heading_level
        )

        # Initialize LightRAG
        rag = await initialize_rag(storage_dir_path)

        # Get workspace path
        storage_name = os.path.basename(storage_dir_path.rstrip('/'))
        workspace_dir_path = os.path.join(storage_dir_path, storage_name + "_work")

        # Extract Markdown-oriented documents from the given directory
        doc_dict = read_dir(read_dir_path)

        # If storage exists, delete stale/out-of-scope entries and identify files to process this run
        current_process_doc_dict = await _cleanup_and_prepare_documents(
            rag,
            workspace_dir_path,
            doc_dict,
            read_dir_path,
            markdown_chunk_heading_level=effective_heading_level,
        )

        # Chunk and graph documents (only the files to be processed this run)
        await doc_to_storage(
            rag,
            current_process_doc_dict,
            markdown_chunk_heading_level=effective_heading_level,
        )
        _write_document_manifest(
            workspace_dir_path,
            doc_dict,
            markdown_chunk_heading_level=effective_heading_level,
        )
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
    finally:
        if rag:
            await rag.finalize_storages()
            
            # Drop caches
            await rag.llm_response_cache.drop()
            
            # Delete instance
            del rag
            
            # Attempt global GC
            gc.collect()

async def _cleanup_and_prepare_documents(
    rag: LightRAG, 
    workspace_dir_path: str, 
    doc_dict: dict, 
    read_dir_path: str = None,
    markdown_chunk_heading_level: int | None = None,
) -> dict:
    """
    Delete stale/out-of-scope files from storage and determine the set of
    Markdown documents to process in this run.

    Args:
        rag: LightRAG instance
        workspace_dir_path: Workspace directory path
        doc_dict: Current document file dictionary
        read_dir_path: Target directory path to read from

    Returns:
        document_dict_to_process
    """
    try:
        # Build path to kv_store_text_chunks.json
        text_chunks_path = os.path.join(workspace_dir_path, "kv_store_text_chunks.json")
        manifest_path = os.path.join(workspace_dir_path, _DOC_MANIFEST_FILENAME)
        current_doc_hashes = _build_document_hashes(doc_dict)
        
        # If the file doesn't exist, treat as a new storage; process all files
        if not os.path.exists(text_chunks_path):
            return doc_dict

        # Load existing storage chunk metadata
        with open(text_chunks_path, "r", encoding="utf-8") as f:
            storage_chunks_json = json.load(f)

        if not os.path.exists(manifest_path):
            logger.info("Document manifest not found. Rebuilding all Markdown chunks for this storage.")
            all_doc_ids = {
                storage_chunk_data["full_doc_id"]
                for storage_chunk_data in storage_chunks_json.values()
            }
            await _delete_doc_ids(rag, all_doc_ids, out_of_scope_count=0, changed_count=len(all_doc_ids))
            return doc_dict

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_payload = json.load(f)

        previous_doc_hashes, previous_chunk_heading_level = _parse_manifest_payload(manifest_payload)

        if previous_chunk_heading_level != markdown_chunk_heading_level:
            logger.info(
                "Markdown chunk heading level changed for this storage. "
                "Rebuilding all Markdown chunks."
            )
            all_doc_ids = {
                storage_chunk_data["full_doc_id"]
                for storage_chunk_data in storage_chunks_json.values()
            }
            await _delete_doc_ids(
                rag,
                all_doc_ids,
                out_of_scope_count=0,
                changed_count=len(previous_doc_hashes),
            )
            return doc_dict

        previous_paths = set(previous_doc_hashes.keys())
        current_paths = set(current_doc_hashes.keys())
        unchanged_files = {
            path for path in current_paths
            if previous_doc_hashes.get(path) == current_doc_hashes[path]
        }
        changed_files = current_paths - unchanged_files
        removed_or_out_of_scope_files = previous_paths - current_paths

        doc_ids_by_file_path: Dict[str, set[str]] = {}
        for storage_chunk_data in storage_chunks_json.values():
            storage_chunk_file_path = storage_chunk_data["file_path"]
            doc_ids_by_file_path.setdefault(storage_chunk_file_path, set()).add(
                storage_chunk_data["full_doc_id"]
            )

        # Select files to process this run (exclude unchanged files)
        current_process_doc_dict = {k: v for k, v in doc_dict.items() if k not in unchanged_files}

        logger.info("=" * 50)
        logger.info(f"Documents to process this run: {len(current_process_doc_dict)}")

        all_docs_to_delete = set()
        for file_path in changed_files | removed_or_out_of_scope_files:
            all_docs_to_delete.update(doc_ids_by_file_path.get(file_path, set()))

        await _delete_doc_ids(
            rag,
            all_docs_to_delete,
            out_of_scope_count=len(removed_or_out_of_scope_files),
            changed_count=len(changed_files),
        )
        
        logger.info("=" * 50)
        logger.info("")
        
        return current_process_doc_dict
            
    except Exception as e:
        logger.error(f"Error during document cleanup: {e}")
        # On error, process all files
        return doc_dict


def _build_document_hashes(doc_dict: dict) -> Dict[str, str]:
    current_doc_hashes: Dict[str, str] = {}
    for doc_file_path, doc_content in doc_dict.items():
        cleaned_content = sanitize_text_for_encoding(doc_content) if doc_content else ""
        current_doc_hashes[doc_file_path] = compute_mdhash_id(cleaned_content, prefix="doc-")
    return current_doc_hashes


def _write_document_manifest(
    workspace_dir_path: str,
    doc_dict: dict,
    markdown_chunk_heading_level: int | None = None,
) -> None:
    manifest_path = os.path.join(workspace_dir_path, _DOC_MANIFEST_FILENAME)
    os.makedirs(workspace_dir_path, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": _MANIFEST_VERSION,
                "chunking": {
                    "max_heading_level": markdown_chunk_heading_level,
                },
                "documents": _build_document_hashes(doc_dict),
            },
            f,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )


def _parse_manifest_payload(manifest_payload: dict) -> tuple[Dict[str, str], int | None]:
    if "documents" not in manifest_payload:
        return manifest_payload, None

    chunking = manifest_payload.get("chunking", {})
    return manifest_payload.get("documents", {}), chunking.get("max_heading_level")


async def _delete_doc_ids(
    rag: LightRAG,
    doc_ids: set[str],
    out_of_scope_count: int,
    changed_count: int,
) -> None:
    if doc_ids:
        logger.info(
            "Deleting %s documents (out-of-scope: %s, changed: %s)",
            len(doc_ids),
            out_of_scope_count,
            changed_count,
        )
        for doc_id in doc_ids:
            try:
                await rag.adelete_by_doc_id(doc_id)
            except Exception as e:
                logger.error(f"Delete error {doc_id}: {e}")
        logger.info("Completed deletion of stale documents")
        return

    logger.info("No documents to delete")
