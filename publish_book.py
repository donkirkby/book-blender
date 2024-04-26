import typing
from itertools import zip_longest
from pathlib import Path

from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfdoc import PDFInfo
from reportlab.platypus import SimpleDocTemplate
from textstat import textstat

from blender_block import BlenderBlock
from block_pair import BlockPair
from footer import FooterCanvas
from svg_diagram import SvgDiagram


def write_blocks(blocks: typing.Sequence[BlenderBlock], out_path: Path) -> None:
    subtitle = blocks[0].subtitle
    subject = 'A word puzzle by Don Kirkby'
    author = 'Don Kirkby'
    if subtitle:
        subtitle_parts = subtitle.split()
        if subtitle_parts[0].lower() == 'by':
            subtitle_parts.pop(0)
            author = ' '.join(subtitle_parts)
        else:
            subject = subtitle

    doc = SimpleDocTemplate(str(out_path),
                            leftMargin=inch * 1.1,
                            rightMargin=inch * 1.1,
                            pagesize=pagesizes.letter,
                            author=author,
                            title=blocks[0].title,
                            subject=subject,
                            keywords=['puzzles',
                                      'word-puzzles',
                                      'games',
                                      'word-games'],
                            creator=PDFInfo.creator)

    blocks_iter = iter(blocks)

    doc.build([SvgDiagram(BlockPair(left, right).as_svg()).to_reportlab()
               for left, right in zip_longest(blocks_iter, blocks_iter)],
              canvasmaker=FooterCanvas)


def find_mod_time(project_path: Path) -> float:
    return max(file_path.stat().st_mtime
               for file_path in project_path.rglob('*.py'))


def main() -> None:
    project_path = Path(__file__).parent
    code_mod_time = find_mod_time(project_path)
    books_path = project_path / 'docs' / 'solutions'
    for in_path in books_path.glob('*.md'):
        name_base = in_path.with_suffix('.pdf').name
        if name_base == 'index.pdf':
            continue
        out_path = project_path / 'docs' / name_base
        is_up_to_date = (out_path.exists() and
                         code_mod_time < out_path.stat().st_mtime)
        source = in_path.read_text()
        level = textstat.text_standard(source)
        word_count = textstat.lexicon_count(source)
        action = 'skipping' if is_up_to_date else 'generating'
        print(f'{word_count} words, {level} in {name_base}, {action}.')

        if is_up_to_date:
            continue
        blocks = BlenderBlock.read(source, width=30, height=6, scale=0.5398)

        write_blocks(blocks, out_path)
    print('Done.')


if __name__ == '__main__':
    main()
