import re
from typing import List
from ..config.settings import (
    markdown_chunk_max_heading_level,
    markdown_chunk_min_section_chars,
    markdown_chunk_skip_toc_sections,
)


_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$", re.MULTILINE)
_TOC_LINE_RE = re.compile(r"^\s*[-*]\s+\[.+\]\(.+\)\s*$", re.MULTILINE)
_NUMBERED_TOC_LINE_RE = re.compile(r"^\s*\d+\.\s+\[.+\]\(.+\)\s*$", re.MULTILINE)


def split_markdown_sections(
    content: str,
    file_path: str,
    max_heading_level: int | None = None,
) -> List[str]:
    """
    Split Markdown content into heading-oriented sections.

    Each chunk includes lightweight metadata so retrieval keeps section context
    even when only a subsection is returned.
    """
    effective_max_heading_level = max_heading_level or markdown_chunk_max_heading_level
    matches = list(_HEADING_RE.finditer(content))
    if not matches:
        return _finalize_chunks([_build_chunk(file_path, "Document", content)])

    chunks: List[str] = []
    heading_stack: List[str] = []

    first_heading = matches[0]
    preamble = content[:first_heading.start()].strip()
    if preamble:
        preamble_chunk = _build_chunk(file_path, "Preamble", preamble)
        if _should_keep_chunk("Preamble", preamble_chunk):
            chunks.append(preamble_chunk)

    for index, match in enumerate(matches):
        level = len(match.group(1))
        heading_text = match.group(2).strip()

        while len(heading_stack) >= level:
            heading_stack.pop()
        heading_stack.append(heading_text)

        if level > effective_max_heading_level:
            continue

        section_start = match.start()
        section_end = _find_section_end(matches, index, len(content), effective_max_heading_level)
        section_text = content[section_start:section_end].strip()
        if not section_text:
            continue

        section_name = " > ".join(heading_stack)
        chunk = _build_chunk(file_path, section_name, section_text)
        if _should_keep_chunk(section_name, chunk):
            chunks.append(chunk)

    return _finalize_chunks(chunks)


def _build_chunk(file_path: str, section_name: str, section_text: str) -> str:
    return (
        f"Source file: {file_path}\n"
        f"Section: {section_name}\n\n"
        f"{section_text.strip()}"
    )


def _find_section_end(
    matches: List[re.Match[str]],
    current_index: int,
    content_length: int,
    max_heading_level: int,
) -> int:
    current_level = len(matches[current_index].group(1))
    for next_match in matches[current_index + 1:]:
        if len(next_match.group(1)) <= current_level and len(next_match.group(1)) <= max_heading_level:
            return next_match.start()
    return content_length


def _should_keep_chunk(section_name: str, chunk_text: str) -> bool:
    body = chunk_text.split("\n\n", 1)[1] if "\n\n" in chunk_text else chunk_text
    stripped_body = body.strip()

    if len(stripped_body) < markdown_chunk_min_section_chars:
        return False

    if markdown_chunk_skip_toc_sections and _looks_like_toc(section_name, stripped_body):
        return False

    return True


def _looks_like_toc(section_name: str, body: str) -> bool:
    normalized_name = section_name.strip().lower()
    if normalized_name in {"toc", "table of contents", "contents", "目次"}:
        return True

    lines = [line for line in body.splitlines() if line.strip()]
    if not lines:
        return False

    toc_like_lines = sum(
        1
        for line in lines
        if _TOC_LINE_RE.match(line) or _NUMBERED_TOC_LINE_RE.match(line)
    )
    return toc_like_lines >= max(3, len(lines) // 2)


def _finalize_chunks(chunks: List[str]) -> List[str]:
    return chunks or []
