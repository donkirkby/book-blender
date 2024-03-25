from pathlib import Path

from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

from blender_block import BlenderBlock
from svg_diagram import SvgDiagram


def write_blocks(blocks, out_path):
    doc = BaseDocTemplate(str(out_path))
    # Two Columns
    # noinspection PyUnresolvedReferences
    frame1 = Frame(doc.leftMargin,
                   doc.bottomMargin,
                   doc.width / 2 - 6,
                   doc.height,
                   id='col1')
    # noinspection PyUnresolvedReferences
    frame2 = Frame(doc.leftMargin + doc.width / 2 + 6,
                   doc.bottomMargin,
                   doc.width / 2 - 6,
                   doc.height,
                   id='col2')
    doc.addPageTemplates([PageTemplate(id='TwoCol', frames=[frame1, frame2]), ])
    doc.build([SvgDiagram(block.as_svg()).to_reportlab()
               for block in blocks])


def main():
    in_path = Path(__file__).parent / 'books' / 'luck.md'
    name_base = in_path.with_suffix('.pdf').name
    out_path = Path(__file__).parent / 'docs' / name_base
    with in_path.open('r') as f:
        blocks = BlenderBlock.read(f, width=30, height=6, scale=0.58)

    write_blocks(blocks, out_path)


if __name__ == '__main__':
    main()
