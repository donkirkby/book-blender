import re
import typing
from itertools import zip_longest
from textwrap import wrap

from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor
from svgwrite import Drawing
from svgwrite.container import Group


class BlenderBlockProcessor(Treeprocessor):
    def __init__(self, width: int, height: int, scale: float | None = None):
        super().__init__()
        self.blocks: list[BlenderBlock] = []
        self.width = width
        self.height = height
        self.scale = scale

    def run(self, root):
        for child in root:
            if child.text is None:
                print(repr(child))
        texts = (re.sub(r'\s+', ' ', child.text)
                 for child in root)
        lines = (line + ' '*(self.width - len(line))
                 for text in texts
                 for line in wrap(text, self.width))
        groups = zip_longest(*([lines] * self.height))
        for page, group in enumerate(groups, 1):
            group_lines = (line
                           for line in group
                           if line is not None)
            self.blocks.append(BlenderBlock(tuple(group_lines),
                                            page,
                                            scale=self.scale))


class BlenderBlockExtension(Extension):
    def __init__(self, width: int, height: int, scale: float | None = None):
        super().__init__()
        self.processor = BlenderBlockProcessor(width, height, scale)

    def extendMarkdown(self, md):
        md.treeprocessors.register(self.processor,
                                   'blender_block',
                                   50)


class BlenderBlock:
    @classmethod
    def read(cls,
             file: typing.IO,
             width: int = 40,
             height: int = 8,
             scale: float | None = None) -> list['BlenderBlock']:
        extension = BlenderBlockExtension(width, height, scale)
        Markdown(extensions=[extension]).convert(file.read())
        blocks = extension.processor.blocks
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

    def as_svg(self) -> str:
        column_count = len(self.lines[0])
        row_count = len(self.lines)
        letter_width = 12
        line_height = 20
        margin = round(letter_width / 1.2)
        width = column_count * letter_width + 2 * margin
        height = line_height * (row_count * 4 + 2)
        drawing = Drawing(size=(width*self.scale, height*self.scale + margin))
        group = Group()
        drawing.add(group)
        group.scale(self.scale)
        for i in range(5, column_count, 10):
            shade_width = 5 * letter_width
            if i + 5 == column_count:
                shade_width += margin
            group.add(drawing.rect((i * letter_width + margin, 0),
                                   (shade_width, height),
                                   fill='rgb(240, 240, 240)'))
        group.add(drawing.rect((0, 0),
                               (width, height),
                               fill_opacity=0,
                               stroke='black'))
        group.add(drawing.rect((0, 0),
                               (width, line_height * (row_count * 3 + 1)),
                               fill_opacity=0,
                               stroke='black'))
        column_letters: list[list[str]] = [[] for _ in range(column_count)]
        nbsp = '\xa0'
        for i, line in enumerate(self.lines):
            lower_line = line.lower()
            blanks = re.sub(r'[a-z]', '-', lower_line)
            blanks = re.sub(r'[^\-]', nbsp, blanks)
            group.add(drawing.text(blanks,
                                   (margin, (i*3+2+0.35)*line_height),
                                   font_family='Courier',
                                   font_size=line_height))
            punctuation = re.sub(r'[a-z ]', nbsp, lower_line)
            group.add(drawing.text(punctuation,
                                   (margin, (i*3+2)*line_height),
                                   font_family='Courier',
                                   font_size=line_height))
            chars = list(re.sub(r'[^a-z]', nbsp, lower_line))
            for j, char in enumerate(chars):
                column_letters[j].append(char)
            for match in re.finditer(r'[a-z]+', lower_line):
                start, end = match.span()
                chars[start:end] = sorted(chars[start:end])
            sorted_line = ''.join(chars)
            group.add(drawing.text(sorted_line,
                                   (margin, (i*3+3)*line_height),
                                   font_family='Courier',
                                   font_size=line_height))
        for column in column_letters:
            column.sort()
        for i in range(row_count):
            row_letters = ''.join(column[i] for column in column_letters)
            group.add(drawing.text(row_letters,
                                   (margin, (row_count*3+2+i)*line_height),
                                   font_family='Courier',
                                   font_size=line_height))
        if self.page is not None:
            group.add(drawing.text(str(self.page),
                                   (width-margin, (row_count*4+1)*line_height),
                                   font_family='Courier',
                                   font_size=line_height*1.5,
                                   text_anchor='end'))

        # svglib trims leading nbsps when converting to ReportLab drawing.
        for element in group.elements:
            text = getattr(element, 'text', None)
            if text is None:
                continue
            stripped = text.lstrip(nbsp)
            indent = len(text) - len(stripped)
            if indent:
                element.text = stripped
                element.translate(letter_width*indent)

        return drawing.tostring()
