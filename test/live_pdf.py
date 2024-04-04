from pathlib import Path

import fitz
from space_tracer import LiveImage


class LivePdf(LiveImage):
    def __init__(self, pdf_path: Path, page: int = 0, dpi: int = 24) -> None:
        self.pdf_path = pdf_path
        self.page = page
        self.dpi = dpi

    def convert_to_png(self) -> bytes:
        fitz_doc = fitz.open(self.pdf_path)
        page = fitz_doc.load_page(self.page)
        pixmap: fitz.Pixmap = page.get_pixmap(dpi=self.dpi)
        return pixmap.tobytes()
