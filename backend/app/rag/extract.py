import os
import pypdf

def extract_text_from_file(file_path: str) -> list[tuple[int, str]]:
    """Extracts text from PDF or text file.
    Returns a list of tuples: (page_number, text_content)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        pages = []
        try:
            reader = pypdf.PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append((idx + 1, text))
        except Exception as e:
            # Fallback to empty text if corrupted
            print(f"Error reading PDF {file_path}: {e}")
        return pages
    else:
        # Assume plain text file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [(1, text)]