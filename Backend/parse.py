# RAG.py
import os
import re
from typing import List, Dict, Tuple

import fitz  
from PIL import Image
import pytesseract

# If Tesseract is not on your PATH, set the full executable path:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_resume_text(pdf_path: str) -> str:
    """
    Extract raw text and image-based OCR text from a PDF resume using PyMuPDF and Tesseract.
    Returns a single combined string.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Resume file not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    full_text = []

    for page_num, page in enumerate(doc, start=1):
        # 1. Extract plain text
        text = page.get_text("text")
        if text.strip():
            full_text.append(f"[Page {page_num} Text]\n{text}")

        # 2. Extract images and run OCR
        images = page.get_images(full=True)
        for img_index, img_info in enumerate(images, start=1):
            xref = img_info[0]
            pix = fitz.Pixmap(doc, xref)
            # Convert pixmap to PIL Image
            mode = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            pix = None  

            # OCR the image
            try:
                ocr_text = pytesseract.image_to_string(img).strip()
                if ocr_text:
                    full_text.append(f"[Page {page_num} Image {img_index} OCR]\n{ocr_text}")
            except Exception as e:
                full_text.append(f"[Page {page_num} Image {img_index} OCR ERROR: {e}]")
            img.close()

    doc.close()
    return "\n\n".join(full_text)


def split_into_sections(raw_text: str) -> Dict[str, str]:
    """
    Splits resume text into sections by common headings.
    Returns a dict mapping section name to that section's text.
    """
    heading_patterns = [
        r"(Education)",
        r"(Experience)",
        r"(Skills)",
        r"(Projects?)",
        r"(Certifications?)",
        r"(Summary|Profile)",
        r"(Contact)",
        r"(Objective)"
    ]
    pattern = re.compile(r"^" + r"|^".join(heading_patterns),
                         re.IGNORECASE | re.MULTILINE)

    # Locate headings
    sections: List[Tuple[str, int]] = []
    for match in pattern.finditer(raw_text):
        heading = match.group(0).strip()
        start = match.start()
        sections.append((heading, start))

    # Add end sentinel
    sections.append(("END_OF_RESUME", len(raw_text)))

    # Extract each section
    section_texts: Dict[str, str] = {}
    for i in range(len(sections) - 1):
        heading, start = sections[i]
        _, end = sections[i + 1]
        content = raw_text[start:end].strip()
        section_texts[heading] = content

    return section_texts


def chunk_section_text(section_text: str, max_tokens: int = 500) -> List[str]:
    """
    Splits a section's text into chunks of approximately max_tokens words.
    """
    words = section_text.split()
    return [" ".join(words[i : i + max_tokens])
            for i in range(0, len(words), max_tokens)]


def build_resume_chunks(pdf_path: str, max_tokens: int = 500) -> List[Dict[str, str]]:
    """
    End-to-end: extract resume text (with OCR), split into labeled sections, then chunk each section.
    Returns a list of dicts: { "section": section_name, "chunk_index": index, "text": chunk_text }.
    """
    raw_text = extract_resume_text(pdf_path)
    sections = split_into_sections(raw_text)

    resume_chunks = []
    for section, text in sections.items():
        if not text:
            continue
        chunks = chunk_section_text(text, max_tokens=max_tokens)
        for idx, chunk in enumerate(chunks, start=1):
            resume_chunks.append({
                "section": section,
                "chunk_index": str(idx),
                "text": chunk
            })
    return resume_chunks


# --- Example usage ---
if __name__ == "__main__":
    import json
    pdf_file = r"Resume_Prathamesh_Dhote.pdf"
    chunks = build_resume_chunks(pdf_file, max_tokens=400)
    print(json.dumps(chunks, indent=2))
