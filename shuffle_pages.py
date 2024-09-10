import random
from functools import partial
from pathlib import Path

from markdown import Markdown
from markdown.extensions.meta import MetaExtension
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfdoc import PDFInfo
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, KeepTogether


class ShufflerCanvas(Canvas):
    def __init__(self, *args, random_seed: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_seed = random_seed
        self.pages: list[dict] = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        random.seed(self.random_seed)
        random.shuffle(self.pages)
        random.seed()
        for page in self.pages:
            self.__dict__.update(page)
            super().showPage()
        super().save()
        self.pages.clear()


def shuffle_pages(source_path: Path, dest_path: Path):
    markdown_source = source_path.read_text(encoding="utf-8")
    markdown_paragraphs = markdown_source.split("\n\n")
    meta_extension = MetaExtension()

    converter = Markdown(extensions=[meta_extension])

    pdf_paragraphs = []
    for markdown_paragraph in markdown_paragraphs:
        html_paragraph = converter.convert(markdown_paragraph)
        pdf_paragraph = Paragraph(html_paragraph)
        pdf_paragraphs.append(KeepTogether(pdf_paragraph))
    title = 'Shuffled Pages'
    subject = 'A word puzzle by Don Kirkby'
    author = 'Don Kirkby'
    page_size = (4.25 * inch, 5.5 * inch)
    vertical_margin = 0.3 * inch
    side_margin = 0.5 * inch

    doc = SimpleDocTemplate(str(dest_path),
                            leftMargin=side_margin,
                            rightMargin=side_margin,
                            topMargin=vertical_margin,
                            bottomMargin=vertical_margin,
                            pagesize=page_size,
                            author=author,
                            title=title,
                            subject=subject,
                            keywords=['puzzles',
                                      'word-puzzles',
                                      'games',
                                      'word-games'],
                            creator=PDFInfo.creator)
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        if hasattr(style, 'fontSize'):
            if style.name.startswith('Heading'):
                scale = 1.5
                style.fontName = 'Heading'
            else:
                scale = 2
                style.fontName = 'Body'
            style.fontSize *= scale
            style.leading *= scale

    doc.build(pdf_paragraphs,
              canvasmaker=partial(ShufflerCanvas,
                                  random_seed=len(markdown_source)))


if __name__ in ('__main__', '__live_coding__'):
    shuffle_pages(Path('docs/shuffle-solutions/the-advocates-wedding-day.md'),
                  Path('docs/the-advocates-wedding-day.pdf'))
