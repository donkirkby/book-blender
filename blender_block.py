import re
import typing
from itertools import zip_longest
from textwrap import wrap

from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor
from svgwrite import Drawing
from svgwrite.shapes import Rect
from svgwrite.text import Text


class BlenderBlockProcessor(Treeprocessor):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.blocks: list[BlenderBlock] = []
        self.width = width
        self.height = height
        
    def run(self, root):
        texts = (re.sub(r'\s+', ' ', child.text)
                 for child in root)
        lines = (line + ' '*(self.width - len(line))
                 for text in texts
                 for line in wrap(text, self.width))
        groups = zip_longest(*([lines] * self.height))
        for group in groups:
            group_lines = (line
                           for line in group
                           if line is not None)
            self.blocks.append(BlenderBlock(tuple(group_lines)))


class BlenderBlockExtension(Extension):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.processor = BlenderBlockProcessor(width, height)

    def extendMarkdown(self, md):
        md.treeprocessors.register(self.processor,
                                   'blender_block',
                                   50)


class BlenderBlock:
    @classmethod
    def read(cls,
             file: typing.IO,
             width: int = 40,
             height: int = 8) -> list['BlenderBlock']:
        extension = BlenderBlockExtension(width, height)
        Markdown(extensions=[extension]).convert(file.read())
        blocks = extension.processor.blocks
        return blocks

    def __init__(self, lines: tuple[str, ...]) -> None:
        self.lines = lines

    def as_svg(self) -> str:
        column_count = len(self.lines[0])
        row_count = len(self.lines)
        letter_width = 14
        line_height = 20
        margin = letter_width / 1.4
        width = column_count * letter_width + 2 * margin
        height = line_height * (row_count * 5)
        drawing = Drawing(size=(width, height))
        for i in range(5, column_count, 10):
            drawing.add(Rect((i * letter_width + margin, 0),
                             (5 * letter_width, height),
                             fill='rgb(200, 200, 200)'))
        drawing.add(Rect((0, 0),
                         (width, height),
                         fill_opacity=0,
                         stroke='black'))
        drawing.add(Rect((0, 0),
                         (width, line_height * (row_count * 4 - 1)),
                         fill_opacity=0,
                         stroke='black'))
        column_letters: list[list[str]] = [[] for _ in range(column_count)]
        for i, line in enumerate(self.lines):
            lower_line = line.lower()
            blanks = re.sub(r'[a-z]', '_', lower_line)
            drawing.add(Text(blanks,
                             (margin, (i*3+2)*line_height),
                             font_family='Courier',
                             font_size=line_height,
                             letter_spacing=line_height/10))
            nbsp = '\xa0'
            chars = list(re.sub(r'[^a-z]', nbsp, lower_line))
            for j, char in enumerate(chars):
                column_letters[j].append(char)
            for match in re.finditer(r'[a-z]+', lower_line):
                start, end = match.span()
                chars[start:end] = sorted(chars[start:end])
            sorted_line = ''.join(chars)
            drawing.add(Text(sorted_line,
                             (margin, (i*3+3)*line_height),
                             font_family='Courier',
                             font_size=line_height,
                             letter_spacing=line_height/10))
        for column in column_letters:
            column.sort()
        for i in range(row_count):
            row_letters = ''.join(column[i] for column in column_letters)
            drawing.add(Text(row_letters,
                             (margin, (row_count*3+2+i)*line_height),
                             font_family='Courier',
                             font_size=line_height,
                             letter_spacing=line_height/10))

        return drawing.tostring()
