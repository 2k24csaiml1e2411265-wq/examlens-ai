"""PDF extraction helpers for ExamLens AI."""
import io
import pdfplumber


def extract_text_from_multiple_pdfs(uploaded_files: list) -> tuple[str, list[dict]]:
    """Extract text from all uploaded PDFs and return combined text + quality metadata."""
    combined = []
    metadata = []

    for i, f in enumerate(uploaded_files, start=1):
        try:
            raw = f.read()
            page_texts = []
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                for page_no, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    if text.strip():
                        page_texts.append(text.strip())

            text = "\n\n".join(page_texts)
            metadata.append({
                "name": getattr(f, "name", f"paper_{i}.pdf"),
                "pages": len(page_texts),
                "characters": len(text),
                "status": "ok" if text.strip() else "empty",
            })
            combined.append(
                f"===== PAPER {i}: {getattr(f, 'name', f'paper_{i}.pdf')} =====\n{text}"
            )
        except Exception as exc:
            name = getattr(f, "name", f"paper_{i}.pdf")
            metadata.append({
                "name": name, "pages": 0, "characters": 0,
                "status": f"error: {exc}",
            })
            combined.append(f"===== PAPER {i}: {name} =====\n[Extraction failed: {exc}]")

    return "\n\n".join(combined).strip(), metadata
