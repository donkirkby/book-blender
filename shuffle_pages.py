import random
from dataclasses import dataclass
from itertools import product
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
from padded_paragraph import PaddedParagraph
from publisher import Publisher
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


def pop_panel(paragraphs: list[PaddedParagraph],
              avail_width: int,
              avail_height: int) -> StoryPanel:
    """ Create a panel with the first set of paragraphs from a list.

    Choose the extra padding for each paragraph that breaks the panel at the end
    of a sentence, if possible. If it has to use fewer lines, it will leave up
    to 10% of the lines unused. If more than one option is available, choose the
    one that uses the most lines. If there is a tie, choose the one where the
    maximum extra padding is smallest.

    :param paragraphs: list of paragraphs to group into a panel. The ones that
        are used have been popped of the start of the list. If the last one used
        had to be split, then the unused portion is inserted back to the start
        of the list.
    :param avail_width: width to fit the panel in
    :param avail_height: height to fit the panel in
    :return: A StoryPanel with the paragraphs added. They have all had their
        extra padding set, and been wrapped.
    """
    avail_width = round(avail_width)
    avail_height = round(avail_height)
    max_lines = avail_height // round(paragraphs[0].style.leading) - 6
    min_lines = max_lines * 9 // 10
    active_paragraphs = []
    remaining_lines = max_lines
    while remaining_lines > 0 and paragraphs:
        paragraph = paragraphs.pop(0)
        if not paragraph.all_line_endings:
            paragraph.find_all_line_endings(avail_width)
        paragraph_min_lines = len(paragraph.all_line_endings[0][1])
        remaining_lines -= paragraph_min_lines
        active_paragraphs.append(paragraph)
    active_line_endings = [paragraph.all_line_endings
                           for paragraph in active_paragraphs]
    best_score: tuple[bool, int, int] = (False, -max_lines, 0)
    best_choices = None
    for padding_choices in product(*active_line_endings):
        all_line_endings = ''.join(
            line_endings
            for extra_padding, line_endings in padding_choices)
        total_line_count = len(all_line_endings)
        line_count = total_line_count
        is_clean_break = True
        if total_line_count > max_lines:
            is_clean_break = False
            for line_count in reversed(range(min_lines, max_lines + 1)):
                if all_line_endings[line_count-1] == '.':
                    is_clean_break = True
                    break
        unused_lines = max_lines - line_count
        score: tuple[bool, int, int] = (is_clean_break, -unused_lines, max(
            extra_padding
            for extra_padding, line_endings in padding_choices))
        # noinspection PyTypeChecker
        if score > best_score:
            best_score = score
            best_choices = padding_choices
    _, unused_lines, _ = best_score
    assert best_choices is not None
    panel_paragraphs = []
    inserted_count = 0
    remaining_lines = max_lines - unused_lines
    for (extra_padding, line_endings), paragraph in zip(best_choices,
                                                        active_paragraphs):
        if remaining_lines <= 0:
            # Put it back for the next panel.
            paragraphs.insert(inserted_count, paragraph)
            inserted_count += 1
            continue
        paragraph.extra_padding = extra_padding
        paragraph.wrap(avail_width, avail_height)
        remaining_lines -= len(line_endings)
        avail_height -= paragraph.height
        if remaining_lines >= 0:
            panel_paragraphs.append(paragraph)
            continue
        used_lines = len(line_endings) + remaining_lines
        avail_height = paragraph.style.leading * used_lines
        pieces = paragraph.split(avail_width, avail_height+1)
        pieces[0].wrap(avail_width, avail_height)
        paragraphs.insert(inserted_count, pieces[1])
        inserted_count += 1
        panel_paragraphs.append(pieces[0])

    return StoryPanel(panel_paragraphs)


def shuffle_pages(markdown_source: str, dest_path: Path) -> str:
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
    # body_style.firstLineIndent = body_style.fontSize
    body_style.allowOrphans = True

    converter = Markdown(extensions=[meta_extension])

    metadata = {}
    pdf_paragraphs = []
    for markdown_paragraph in markdown_paragraphs:
        html_paragraph = converter.convert(markdown_paragraph)
        if not html_paragraph:
            continue
        metadata.update(converter.Meta)  # type: ignore
        pdf_paragraph = PaddedParagraph(html_paragraph, style=body_style)
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
    panels = split_panels(pdf_paragraphs, panel_width, panel_height)
    # canvas.drawBoundary('black',
    #                     0, vertical_margin*2 + panel_height,
    #                     panel_width+2*side_margin, panel_height+2*vertical_margin)

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
    return f'{total_page_count} pages'


def split_panels(pdf_paragraphs, panel_width, panel_height):
    panels = []
    while pdf_paragraphs:
        panels.append(pop_panel(pdf_paragraphs, panel_width, panel_height))
    return panels


class ShuffledPagesPublisher(Publisher):
    def __init__(self):
        super().__init__()
        self.books_path = self.project_path / 'docs' / 'shuffle-solutions'

    def write(self, source: str, out_path: Path) -> None:
        self.content_summary = shuffle_pages(source, out_path)


def main():
    source_path = Path('docs/shuffle-solutions/the-signal-man.md')
    dest_path = Path('docs/the-signal-man.pdf')
    markdown_source = source_path.read_text(encoding="utf-8")
    shuffle_pages(markdown_source, dest_path)
    if __name__ == '__live_coding__':
        from test.live_pdf import LivePdf

        LivePdf(dest_path, dpi=72, page=7).display((-300, 400))


if __name__ in ('__main__', '__live_coding__'):
    main()
