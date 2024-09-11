import random
from dataclasses import dataclass
from pathlib import Path

from markdown import Markdown
from markdown.extensions.meta import MetaExtension
from reportlab.lib import pagesizes
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph


@dataclass
class StoryPanel:
    paragraphs: list[Paragraph]
    answer_segment: str


def shuffle_pages(source_path: Path, dest_path: Path):
    markdown_source = source_path.read_text(encoding="utf-8")
    markdown_paragraphs = markdown_source.split("\n\n")
    meta_extension = MetaExtension()
    random.seed(len(markdown_source))

    converter = Markdown(extensions=[meta_extension])

    pdf_paragraphs = []
    for markdown_paragraph in markdown_paragraphs:
        html_paragraph = converter.convert(markdown_paragraph)
        pdf_paragraph = Paragraph(html_paragraph)
        pdf_paragraphs.append(pdf_paragraph)
    pagesize = pagesizes.letter
    canvas = Canvas(str(dest_path), pagesize)
    canvas.setTitle('Shuffled Pages')
    canvas.setSubject('A Mystery Word Puzzle')
    canvas.setAuthor('Don Kirkby')
    canvas.setKeywords(['puzzles',
                        'word-puzzles',
                        'games',
                        'word-games'])
    answer = list('THISMESSAGEISABITTOOLONG')
    full_width, full_height = pagesize
    vertical_margin = 0.25 * inch
    side_margin = 0.5 * inch
    panel_width = full_width / 2 - side_margin * 2
    panel_height = full_height / 2 - vertical_margin * 2
    remaining_height = 0
    panels = []
    for paragraph in pdf_paragraphs:
        paragraph.canv = canvas
        paragraph.wrap(panel_width, panel_height)
        if paragraph.height > panel_height:
            raise ValueError(
                f'Paragraph is too big for the page: {paragraph.text[:100]}')
        if paragraph.height > remaining_height:
            panels.append(StoryPanel(paragraphs=[paragraph],
                                     answer_segment=answer.pop(0)))
            remaining_height = panel_height
        else:
            panels[-1].paragraphs.append(paragraph)
        remaining_height -= paragraph.height
    random.shuffle(panels)

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

    corner_coords = [
        (side_margin, full_height - vertical_margin),
        (side_margin*3 + panel_width, full_height - vertical_margin),
        (side_margin, full_height - vertical_margin*3 - panel_height),
        (side_margin*3 + panel_width,
         full_height - vertical_margin*3 - panel_height)]
    for panel_num, panel in enumerate(panels):
        if panel_num > 0 and panel_num % 4 == 0:
            canvas.showPage()
        x, y = corner_coords[panel_num % 4]
        next_y = y
        for paragraph in panel.paragraphs:
            next_y -= paragraph.height
            paragraph.drawOn(canvas, x, next_y)
        canvas.drawString(x + panel_width,
                          y - panel_height,
                          panel.answer_segment)
    canvas.save()


if __name__ in ('__main__', '__live_coding__'):
    shuffle_pages(Path('docs/shuffle-solutions/the-advocates-wedding-day.md'),
                  Path('docs/the-advocates-wedding-day.pdf'))
