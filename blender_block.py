import re
import typing
from itertools import zip_longest
from textwrap import wrap

from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor


class BlenderBlockProcessor(Treeprocessor):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.blocks = []
        self.width = width
        self.height = height
        
    def run(self, root):
        texts = (re.sub(r'\s+', ' ', child.text)
                 for child in root)
        lines = (line
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
             height: int = 8) -> list[typing.Self]:
        extension = BlenderBlockExtension(width, height)
        Markdown(extensions=[extension]).convert(file.read())
        blocks = extension.processor.blocks
        return blocks

    def __init__(self, lines: tuple[str, ...]) -> None:
        self.lines = lines
