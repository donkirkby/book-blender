import math
import re
import typing
from itertools import chain
from textwrap import wrap

from markdown import Extension, Markdown
from markdown.extensions.meta import MetaExtension
from markdown.treeprocessors import Treeprocessor
from svgwrite import Drawing
from svgwrite.container import Group

LINE_HEIGHT = 20
LETTER_WIDTH = 12
MARGIN = round(LETTER_WIDTH / 1.2)


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
        for child in root:
            if child.text is None:
                print(repr(child))
        texts = (re.sub(r'\s+', ' ', child.text)
                 for child in root)
        lines = (line + ' '*(self.width - len(line))
                 for text in texts
                 for line in wrap(text, self.width))
        metadata = getattr(self.markdown, 'Meta', {})
        titles = metadata.get('title', [])
        subtitles = metadata.get('subtitle', [])
        if titles:
            lines = chain((' ' * self.width, ), lines)
        lines = list(lines)
        lines_left = len(lines)
        groups_left = math.ceil(lines_left / self.height)
        while lines_left > 0:
            group_size = math.ceil(lines_left / groups_left)
            group_start = -lines_left
            group_end = group_start + group_size
            if group_end >= 0:
                group_end = None
            group_lines = lines[group_start:group_end]
            self.blocks.append(BlenderBlock(tuple(group_lines),
                                            scale=self.scale))
            lines_left -= group_size
            groups_left -= 1
        if titles and self.blocks:
            self.blocks[0].title = titles[0]
        if subtitles and self.blocks:
            self.blocks[0].subtitle = subtitles[0]


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
                 scale: float | None = None) -> None:
        self.lines = lines
        self.page = page
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
                                    LINE_HEIGHT*2.5),
                                   text_anchor='middle',
                                   font_family='Helvetica',
                                   font_size=LINE_HEIGHT*1.5))
        if self.subtitle:
            group.add(drawing.text(self.subtitle,
                                   (self.width / 2,
                                    LINE_HEIGHT*3.5),
                                   text_anchor='middle',
                                   font_family='Helvetica',
                                   font_size=LINE_HEIGHT))

        column_letters: list[list[str]] = [[] for _ in range(self.column_count)]
        nbsp = '\xa0'
        for i, line in enumerate(self.lines):
            lower_line = line.lower()
            blanks = re.sub(r'[^a-z]', nbsp, lower_line)
            blanks = re.sub(r'[a-z]', '-', blanks)
            group.add(drawing.text(blanks,
                                   (MARGIN, (i * 3 + 2 + 0.35) * LINE_HEIGHT),
                                   font_family='Courier',
                                   font_size=LINE_HEIGHT))
            punctuation = re.sub(r'[a-z ]', nbsp, lower_line)
            group.add(drawing.text(punctuation,
                                   (MARGIN, (i * 3 + 2) * LINE_HEIGHT),
                                   font_family='Courier',
                                   font_size=LINE_HEIGHT))
            chars = list(re.sub(r'[^a-z]', nbsp, lower_line))
            for j, char in enumerate(chars):
                column_letters[j].append(char)
            for match in re.finditer(r'[a-z]+', lower_line):
                start, end = match.span()
                chars[start:end] = sorted(chars[start:end])
            sorted_line = ''.join(chars)
            group.add(drawing.text(sorted_line,
                                   (MARGIN, (i * 3 + 3) * LINE_HEIGHT),
                                   font_family='Courier',
                                   font_size=LINE_HEIGHT))
        for column in column_letters:
            column.sort()
        for i in range(self.row_count):
            row_letters = ''.join(column[i] for column in column_letters)
            group.add(drawing.text(row_letters,
                                   (MARGIN,
                                    (self.row_count * 3 + 2 + i) * LINE_HEIGHT),
                                   font_family='Courier',
                                   font_size=LINE_HEIGHT))
        group.add(drawing.text('* * *',
                               (self.width / 2,
                                (self.row_count * 3 + 1) * LINE_HEIGHT),
                               text_anchor='middle',
                               font_family='Courier',
                               font_size=LINE_HEIGHT))
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
