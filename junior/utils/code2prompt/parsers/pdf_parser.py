from pathlib import Path
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import io

def extract_text_from_image(img_bytes):
    """Extract text from an image using easyocr."""
    reader = easyocr.Reader(['en'], gpu=False)
    img = Image.open(io.BytesIO(img_bytes))
    ocr_result = reader.readtext(img, detail=0)
    return "\n".join(ocr_result)

def parse_to_markdown(pdf_path: Path) -> str:
    """Convert a PDF file to Markdown, including metadata and OCR text."""
    doc = fitz.open(pdf_path)
    
    # Extract metadata
    metadata = doc.metadata
    metadata_md = "## PDF Metadata\n"
    for key, value in metadata.items():
        if value:
            metadata_md += f"- **{key}**: {value}\n"
    
    # Extract text and images
    pdf_content = []
    for page_num, page in enumerate(doc.pages(), start=1):
        text = page.get_text("text")
        if text.strip():
            pdf_content.append(f"### Page {page_num}\n{text}")
        else:
            # If no text is found, attempt to use OCR on images
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            ocr_text = extract_text_from_image(img_bytes)
            pdf_content.append(f"### Page {page_num}\n**OCR Data from Image**\n```text\n{ocr_text}\n```")
    
    # Combine metadata and content
    return metadata_md + "\n## PDF Content\n\n" + "\n\n".join(pdf_content)

# Example usage
#pdf_path = Path("example.pdf")
#markdown_content = parse_to_markdown(pdf_path)
#print(markdown_content)
