import typing
from itertools import zip_longest
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate

from blender_block import BlenderBlock
from block_pair import BlockPair
from footer import FooterCanvas
from svg_diagram import SvgDiagram


def write_blocks(blocks: typing.Sequence[BlenderBlock], out_path: Path) -> None:
    doc = SimpleDocTemplate(str(out_path),
                            leftMargin=inch * 0.75,
                            rightMargin=inch * 0.75)

    blocks_iter = iter(blocks)

    doc.build([SvgDiagram(BlockPair(left, right).as_svg()).to_reportlab()
               for left, right in zip_longest(blocks_iter, blocks_iter)],
              canvasmaker=FooterCanvas)


def main() -> None:
    project_path = Path(__file__).parent
    books_path = project_path / 'docs' / 'solutions'
    for in_path in books_path.glob('*.md'):
        name_base = in_path.with_suffix('.pdf').name
        if name_base == 'index.pdf':
            continue
        out_path = project_path / 'docs' / name_base
        if out_path.exists():
            continue
        with in_path.open('r') as f:
            blocks = BlenderBlock.read(f, width=30, height=6, scale=0.58)

        write_blocks(blocks, out_path)
        print(f'Wrote {out_path.relative_to(project_path)}.')
    print('Done.')


if __name__ == '__main__':
    main()
