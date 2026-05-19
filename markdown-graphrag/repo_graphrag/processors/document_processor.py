import logging
import asyncio
from typing import Dict, List, Tuple, Union
from lightrag import LightRAG
from ..config.settings import doc_batch_wait_seconds, parallel_num
from ..utils.markdown_chunker import split_markdown_sections


logger = logging.getLogger(__name__)
    
async def doc_to_storage(
    rag: LightRAG,
    doc_dict: Dict[str, Union[str, bytes]],
    markdown_chunk_heading_level: int | None = None,
) -> None:
    """
    Chunk documents, build graph, and store them in the backend.
    
    Args:
        rag: LightRAG instance
        doc_dict: Mapping of file path -> file content
    """

    logger.info("=" * 50)
    logger.info("Graphing document files")
    logger.info(f"Starting document processing: {len(doc_dict)} files")

    # Batch processing
    batch_size = parallel_num
    
    doc_items = list(doc_dict.items())
    total_batches = len(doc_items) // batch_size + (1 if len(doc_items) % batch_size > 0 else 0)
    
    for i, batch_start in enumerate(range(0, len(doc_items), batch_size)):
        batch_end = min(batch_start + batch_size, len(doc_items))
        batch_items = doc_items[batch_start:batch_end]
        
        logger.info(f"Processing batch {i+1}/{total_batches}: {len(batch_items)} files")
        
        # Process each batch
        await _process_document_batch(
            rag,
            batch_items,
            markdown_chunk_heading_level=markdown_chunk_heading_level,
        )
        
        # Optional pacing between batches for rate-limited providers
        if i < total_batches - 1 and doc_batch_wait_seconds > 0:
            logger.info(f"Waiting {doc_batch_wait_seconds} seconds before next batch...")
            await asyncio.sleep(doc_batch_wait_seconds)

    logger.info("All document processing completed")
    logger.info("=" * 50 + "\n")

async def _process_document_batch(
    rag: LightRAG,
    batch_items: List[Tuple[str, Union[str, bytes]]],
    markdown_chunk_heading_level: int | None = None,
) -> None:
    """
    Process a batch of documents.
    
    Args:
        rag: LightRAG instance
        batch_items: List of tuples (file_path, file_content)
    """
    for doc_path, doc_content in batch_items:
        try:
            logger.info(f"Processing: {doc_path}")
            chunks = split_markdown_sections(
                str(doc_content),
                doc_path,
                max_heading_level=markdown_chunk_heading_level,
            )
            logger.info(f"Prepared {len(chunks)} section chunks: {doc_path}")
            await rag.ainsert(chunks, file_paths=[doc_path] * len(chunks))
            logger.info(f"Done: {doc_path}")
        except Exception as e:
            logger.error(f"Document processing error ({doc_path}): {e}")
            raise
