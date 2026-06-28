def chunk_text(
    text: str, page_number: int, chunk_size: int = 800, overlap: int = 150
) -> list[dict]:
    """Splits text into chunks using a character-based sliding window."""
    chunks = []
    text = text.strip()
    if not text:
        return chunks

    start = 0
    chunk_idx = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_text = text[start:end]
        chunks.append(
            {"text": chunk_text, "page_number": page_number, "chunk_index": chunk_idx}
        )
        chunk_idx += 1
        start += chunk_size - overlap
        if start >= text_len or end == text_len:
            break

    return chunks