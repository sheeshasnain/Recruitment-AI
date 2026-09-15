from io import BytesIO
from pathlib import Path

import fitz
from docx import Document
from fastapi import HTTPException, UploadFile


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


async def extract_resume_text(
    file: UploadFile,
) -> str:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume filename is missing.",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported resume format. "
                "Allowed formats: PDF, DOCX, TXT."
            ),
        )

    content = await file.read(
        MAX_FILE_SIZE + 1
    )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume exceeds the 5 MB limit.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded resume is empty.",
        )

    try:

        if extension == ".pdf":
            text = _extract_pdf(content)

        elif extension == ".docx":
            text = _extract_docx(content)

        else:
            text = _extract_txt(content)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to read resume file.",
        ) from exc

    text = text.strip()

    if len(text) < 30:
        raise HTTPException(
            status_code=400,
            detail=(
                "Resume does not contain enough readable text."
            ),
        )

    return text


def _extract_pdf(content: bytes) -> str:

    document = fitz.open(
        stream=content,
        filetype="pdf",
    )

    # Prevent enormous documents
    if document.page_count > 30:
        raise ValueError(
            "PDF exceeds maximum page count."
        )

    pages = []

    for page in document:
        pages.append(
            page.get_text()
        )

    document.close()

    return "\n".join(pages)


def _extract_docx(content: bytes) -> str:

    document = Document(
        BytesIO(content)
    )

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def _extract_txt(content: bytes) -> str:

    return content.decode(
        "utf-8",
        errors="ignore",
    )