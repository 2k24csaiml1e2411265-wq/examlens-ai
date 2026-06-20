import pdfplumber
import io


def extract_text_from_multiple_pdfs(uploaded_files: list) -> str:
    combined = ""
    for i, f in enumerate(uploaded_files):
        try:
            pdf_bytes = f.read()
            text = ""
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            combined += f"\n\n===== PAPER {i+1}: {f.name} =====\n\n{text.strip()}"
        except Exception as e:
            combined += f"\n\n===== PAPER {i+1}: {f.name} — Error reading: {str(e)} =====\n\n"
    return combined.strip()
