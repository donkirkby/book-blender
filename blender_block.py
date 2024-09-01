import math
import re
from textwrap import wrap

from markdown import Extension, Markdown
from markdown.extensions.meta import MetaExtension
from markdown.inlinepatterns import SMART_EMPHASIS_RE, EMPHASIS_RE, STRONG_RE, \
    SMART_STRONG_RE
from markdown.treeprocessors import Treeprocessor
from svgwrite import Drawing
from svgwrite.container import Group

LINE_HEIGHT = 20
LETTER_WIDTH = 12
MARGIN = round(LETTER_WIDTH / 1.2)
DINKUS = '* * *'


class BlenderBlockProcessor(Treeprocessor):
    def __init__(self,
                 width: int,
                 height: int,
                 scale: float | None = None) -> None:
        super().__init__()
        self.blocks: list[BlenderBlock] = []
        self.width = width
        self.height = height
        self.scale = scale
        self.markdown: Markdown | None = None

    def run(self, root):
        descendants = []
        for child in root:
            if child.tag == 'pre':
                descendants.extend(child)
            else:
                descendants.append(child)
        for child in descendants:
            if child.text is None and child.tag != 'hr':
                print(repr(child))
        all_lines = []
        all_headings = []
        for child in descendants:
            if child.tag == 'h1':
                all_headings.append(child.text)
                all_lines.append(' ' * self.width)
            elif child.tag == 'hr':
                all_headings.append(DINKUS)
                all_lines.append(' ' * self.width)
            elif child.text is not None:
                if child.tag == 'code':
                    prefix = '  '
                else:
                    prefix = ''
                width = self.width - len(prefix)
                text = self.normalize_text(child.text)
                all_lines.extend(prefix + line + ' '*(width - len(line))
                                 for line in wrap(text, width))
                all_headings.extend([''] * (len(all_lines) - len(all_headings)))

        metadata = getattr(self.markdown, 'Meta', {})
        titles = metadata.get('title', [])
        subtitles = metadata.get('subtitle', [])
        if titles:
            all_lines.insert(0, ' ' * self.width)
            all_headings.insert(0, '')
        lines_left = len(all_lines)
        while lines_left > 0:
            groups_left = math.ceil(lines_left / self.height)
            group_size = math.ceil(lines_left / groups_left)
            group_start = -lines_left
            group_end = group_start + group_size

            # Keep headings with following line.
            while (group_end < 0 and
                   all_headings[group_end-1] and
                   group_end < group_start + self.height):
                group_end += 1
            while group_end < 0 and all_headings[group_end-1]:
                group_end -= 1

            # Check for end of lines.
            if group_end >= 0:
                group_end = None
                lines_left = 0
            else:
                lines_left -= group_end - group_start

            group_lines = all_lines[group_start:group_end]
            group_headings = all_headings[group_start:group_end]
            self.blocks.append(BlenderBlock(tuple(group_lines),
                                            scale=self.scale,
                                            headings=group_headings))
        if titles and self.blocks:
            self.blocks[0].title = titles[0]
        if subtitles and self.blocks:
            self.blocks[0].subtitle = subtitles[0]

    @staticmethod
    def normalize_text(text: str) -> str:
        """ Clean up whitespace, and get rid of simple styling. """
        normalized_spaces = re.sub(r'\s+', ' ', text)
        normalized_dasters = re.sub(STRONG_RE, r'\2', normalized_spaces)
        normalized_asterisks = re.sub(EMPHASIS_RE,
                                      r'\2',
                                      normalized_dasters)
        normalized_dunders = re.sub(SMART_STRONG_RE,
                                    r'\2',
                                    normalized_asterisks)
        normalized_underscores = re.sub(SMART_EMPHASIS_RE,
                                        r'\2',
                                        normalized_dunders)
        return normalized_underscores


class BlenderBlockExtension(Extension):
    def __init__(self, width: int, height: int, scale: float | None = None):
        super().__init__()
        self.processor = BlenderBlockProcessor(width, height, scale)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.processor.markdown = md
        md.treeprocessors.register(self.processor,
                                   'blender_block',
                                   50)


class BlenderBlock:
    @classmethod
    def read(cls,
             source: str,
             width: int = 40,
             height: int = 8,
             scale: float | None = None) -> list['BlenderBlock']:
        blender_extension = BlenderBlockExtension(width, height, scale)
        meta_extension = MetaExtension()

        Markdown(extensions=[blender_extension,
                             meta_extension]).convert(source)
        blocks = blender_extension.processor.blocks
        return blocks

    def __init__(self,
                 lines: tuple[str, ...],
                 page: int | None = None,
                 scale: float | None = None,
                 headings: list[str] | None = None) -> None:
        self.lines = lines
        self.page = page
        if headings:
            self.headings = headings
        else:
            self.headings = [''] * self.row_count
        if scale is None:
            self.scale = 0.5
        else:
            self.scale = scale
        self.title: str | None = None
        self.subtitle: str | None = None
        self.width = self.column_count * LETTER_WIDTH + 2 * MARGIN
        self.height = LINE_HEIGHT * (self.row_count * 4 + 2)

    def as_svg(self) -> str:
        drawing = Drawing(size=(self.width * self.scale, self.height * self.scale + MARGIN))
        self.draw(drawing)

        return drawing.tostring()

    @property
    def row_count(self) -> int:
        return len(self.lines)

    @property
    def column_count(self) -> int:
        return len(self.lines[0])

    def draw(self, drawing: Drawing) -> Group:
        group = Group()
        drawing.add(group)
        group.scale(self.scale)
        for i in range(5, self.column_count, 10):
            shade_width = 5 * LETTER_WIDTH
            group.add(drawing.rect((i * LETTER_WIDTH + MARGIN, LINE_HEIGHT/2),
                                   (shade_width, self.height - LINE_HEIGHT),
                                   fill='rgb(240, 240, 240)'))

        if self.title:
            group.add(drawing.text(self.title,
                                   (self.width / 2,
                                    LINE_HEIGHT*2.25),
                                   text_anchor='middle',
                                   font_family='Helvetica',
                                   font_size=LINE_HEIGHT*1.35))
        if self.subtitle:
            group.add(drawing.text(self.subtitle,
                                   (self.width / 2,
                                    LINE_HEIGHT*3.5),
                                   text_anchor='middle',
                                   font_family='Helvetica',
                                   font_size=LINE_HEIGHT))
        for heading_row, heading in enumerate(self.headings):
            if not heading:
                continue
            if heading == DINKUS:
                x = self.width / 2
                anchor = 'middle'
            else:
                x = MARGIN
                anchor = 'start'
            group.add(drawing.text(heading,
                                   (x,
                                    (heading_row * 3 + 2 + 0.35) * LINE_HEIGHT),
                                   text_anchor=anchor,
                                   font_family='Helvetica',
                                   font_size=LINE_HEIGHT))

        column_letters: list[list[str]] = [[] for _ in range(self.column_count)]
        nbsp = '\xa0'
        for i, line in enumerate(self.lines):
            lower_line = line.lower()
            blanks = ''.join('-' if c.isalpha() else nbsp
                             for c in lower_line)
            group.add(drawing.text(blanks,
                                   (MARGIN, (i * 3 + 2 + 0.35) * LINE_HEIGHT),
                                   font_family='Courier',
                                   font_size=LINE_HEIGHT))
            punctuation = ''.join(nbsp if c.isalpha() or c == ' ' else c
                                  for c in lower_line)
            group.add(drawing.text(punctuation,
                                   (MARGIN, (i * 3 + 2) * LINE_HEIGHT),
                                   font_family='Courier',
                                   font_size=LINE_HEIGHT))
            chars = [c if c.isalpha() else nbsp
                     for c in lower_line]
            for j, char in enumerate(chars):
                column_letters[j].append(char)
            for match in re.finditer(r'\w+', ''.join(chars)):
                start, end = match.span()
                chars[start:end] = sorted(chars[start:end])
            sorted_line = ''.join(chars)
            group.add(drawing.text(sorted_line,
                                   (MARGIN, (i * 3 + 3) * LINE_HEIGHT),
                                   font_family='Courier',
                                   font_size=LINE_HEIGHT))
        for column in column_letters:
            column.sort(key=lambda c: (c == nbsp, c))
        for i in range(self.row_count):
            row_letters = ''.join(column[i] for column in column_letters)
            group.add(drawing.text(row_letters,
                                   (MARGIN,
                                    (self.row_count * 3 + 2 + i) * LINE_HEIGHT),
                                   font_family='Courier',
                                   font_size=LINE_HEIGHT))
        divider_y = round((self.row_count * 3 + 0.75) * LINE_HEIGHT)
        group.add(drawing.line(((self.width-LETTER_WIDTH*15)/2, divider_y),
                               ((self.width+LETTER_WIDTH*15)/2, divider_y),
                               stroke='black'))
        # svglib trims leading nbsps when converting to ReportLab drawing.
        for element in group.elements:
            text = getattr(element, 'text', None)
            if text is None:
                continue
            stripped = text.lstrip(nbsp)
            indent = len(text) - len(stripped)
            if indent:
                element.text = stripped
                element.translate(LETTER_WIDTH * indent)

        return group
