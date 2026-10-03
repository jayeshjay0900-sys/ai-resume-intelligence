import pymupdf


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from every page of a PDF resume.
    """

    document = pymupdf.open(file_path)

    text = []

    for page in document:

        page_text = page.get_text()

        if page_text.strip():
            text.append(page_text)

    document.close()

    return "\n".join(text).strip()