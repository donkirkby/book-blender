import random
from dataclasses import dataclass
from pathlib import Path

from markdown import Markdown
from markdown.extensions.meta import MetaExtension
from reportlab.lib import pagesizes
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from font_set import register_fonts
from quote_reader import find_quote_by_length


@dataclass
class StoryPanel:
    paragraphs: list[Paragraph]
    answer_segment: str | None = None

    @property
    def height(self) -> float:
        return sum(paragraph.height for paragraph in self.paragraphs)


# noinspection PyUnresolvedReferences
def draw_title_page(metadata: dict[str, list[str]],
                    styles: dict[str, ParagraphStyle],
                    canvas: Canvas,
                    full_width: float,
                    full_height: float,
                    page_count: int,
                    quote_author: str):
    """ Draw the title page in the top-left quarter of a canvas.

    Doesn't add a new page.
    :param metadata: metadata dict from markdown header
    :param styles: styles dict from Reportlab
    :param canvas: canvas to draw on
    :param full_width: full width of the page
    :param full_height: full height of the page
    :param page_count: number of pages in the story, including the title page.
    :param quote_author: author of the answer quote
    """
    title_style = styles['Heading1']
    title_list = metadata.get('title')
    if not title_list:
        title = 'Some Book'
    else:
        title = title_list[0]
    # noinspection PyUnresolvedReferences
    canvas.setFont(title_style.fontName, title_style.fontSize)
    x = full_width / 4
    y = full_height * 3 / 4
    canvas.drawCentredString(x, y, title)
    y -= title_style.leading
    subtitle_list = metadata.get('subtitle')
    if subtitle_list:
        subtitle = subtitle_list[0]
        subtitle_style = styles['Heading2']
        # noinspection PyUnresolvedReferences
        canvas.setFont(subtitle_style.fontName, subtitle_style.fontSize)
        canvas.drawCentredString(x, y, subtitle)
    body_style = styles['BodyText']
    introduction = Paragraph(f'''Oh no! My word processor mixed up pages
    2 to {page_count} of this book. Can you put them in the right order and
    figure out what {quote_author} did to the page numbers?''', body_style)
    introduction.canv = canvas
    introduction.wrap(full_width*0.4, full_height)
    introduction.drawOn(canvas,
                        full_width * 0.05,
                        y - introduction.height - body_style.leading)

    canvas.setFont(body_style.fontName, body_style.fontSize)
    canvas.drawCentredString(full_width/4,
                             full_height/2 + 3*body_style.fontSize,
                             'https://donkirkby.github.io/book-blender')


def shuffle_pages(source_path: Path, dest_path: Path):
    markdown_source = source_path.read_text(encoding="utf-8")
    markdown_paragraphs = markdown_source.split("\n\n")
    meta_extension = MetaExtension()
    random.seed(len(markdown_source))
    register_fonts()

    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        if hasattr(style, 'fontSize'):
            scale = 0.49
            if style.name.startswith('Heading'):
                scale *= 2
                style.fontName = 'Heading'
            else:
                scale *= 2
                style.fontName = 'Body'
            style.fontSize *= scale
            style.leading *= scale
    body_style: ParagraphStyle = styles['BodyText']  # or Normal?
    body_style.alignment = TA_JUSTIFY
    # noinspection PyUnresolvedReferences
    body_style.firstLineIndent = body_style.fontSize

    converter = Markdown(extensions=[meta_extension])

    metadata = {}
    pdf_paragraphs = []
    for markdown_paragraph in markdown_paragraphs:
        html_paragraph = converter.convert(markdown_paragraph)
        metadata.update(converter.Meta)  # type: ignore
        pdf_paragraph = Paragraph(html_paragraph, style=body_style)
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
    full_width, full_height = pagesize
    vertical_margin = 0.5 * inch
    side_margin = 0.5 * inch
    panel_width = full_width / 2 - side_margin * 2
    panel_height = full_height / 2 - vertical_margin * 2
    # canvas.drawBoundary('black',
    #                     0, vertical_margin*2 + panel_height,
    #                     panel_width+2*side_margin, panel_height+2*vertical_margin)
    split_paragraphs = []
    for paragraph in pdf_paragraphs:
        paragraph.canv = canvas
        paragraph.wrap(panel_width, panel_height)
        paragraph_pieces = paragraph.split(panel_width, panel_height)
        for piece_index, paragraph_piece in enumerate(paragraph_pieces):
            paragraph_piece.wrap(panel_width, panel_height)
            split_paragraphs.append(paragraph_piece)
    panels = split_panels(split_paragraphs, panel_height)
    story_page_count = len(panels)
    total_page_count = story_page_count + 1  # Includes title page.
    quote = find_quote_by_length(story_page_count)
    draw_title_page(metadata,
                    styles,
                    canvas,
                    full_width,
                    full_height,
                    total_page_count,
                    quote.author)
    answer = quote.letters
    for letter, panel in zip(answer, panels):
        panel.answer_segment = letter
    random.shuffle(panels)

    corner_coords = [
        (side_margin, full_height - vertical_margin),
        (side_margin*3 + panel_width, full_height - vertical_margin),
        (side_margin, full_height - vertical_margin*3 - panel_height),
        (side_margin*3 + panel_width,
         full_height - vertical_margin*3 - panel_height)]
    for panel_num, panel in enumerate(panels, 1):
        if panel_num > 0 and panel_num % 4 == 0:
            canvas.showPage()
        x, y = corner_coords[panel_num % 4]
        next_y = y
        for paragraph in panel.paragraphs:
            next_y -= paragraph.height
            paragraph.drawOn(canvas, x, next_y)
        # noinspection PyUnresolvedReferences
        canvas.setFont(body_style.fontName, body_style.fontSize)
        # noinspection PyUnresolvedReferences
        canvas.drawRightString(
            x + panel_width,
            y - panel_height - (vertical_margin + body_style.leading)/3,
            panel.answer_segment)
        title_list = metadata.get('title')
        if title_list:
            title = title_list[0]
            # noinspection PyUnresolvedReferences
            canvas.drawRightString(x + panel_width,
                                   y + (vertical_margin - body_style.leading)/3,
                                   title)
    canvas.save()
    print(f'Saved as a {total_page_count} page PDF.')


def split_panels(pdf_paragraphs, panel_height) -> list[StoryPanel]:
    remaining_height = 0
    panels: list[StoryPanel] = []
    for paragraph in pdf_paragraphs:
        if paragraph.height <= remaining_height:
            panels[-1].paragraphs.append(paragraph)
        else:
            panels.append(StoryPanel(paragraphs=[paragraph]))
            remaining_height = panel_height
        remaining_height -= paragraph.height
    while True:
        has_changed = False
        panel: StoryPanel
        next_panel: StoryPanel
        for panel, next_panel in zip(panels[:-1], panels[1:]):
            this_height = panel.height
            next_height = next_panel.height
            current_diff = (max(this_height, next_height) -
                            min(this_height, next_height))
            last_paragraph_height = panel.paragraphs[-1].height
            if last_paragraph_height + next_height > panel_height:
                next_diff = panel_height
            else:
                this_height2 = this_height - last_paragraph_height
                next_height2 = next_height + last_paragraph_height
                next_diff = (max(this_height2, next_height2) -
                             min(this_height2, next_height2))
            if next_diff < current_diff:
                next_panel.paragraphs.insert(0, panel.paragraphs.pop())
                has_changed = True
        if not has_changed:
            break

    return panels


def main():
    dest_path = Path('docs/the-signal-man.pdf')
    shuffle_pages(Path('docs/shuffle-solutions/the-signal-man.md'),
                  dest_path)
    if __name__ == '__live_coding__':
        from test.live_pdf import LivePdf

        LivePdf(dest_path, dpi=72).display()


if __name__ in ('__main__', '__live_coding__'):
    main()
