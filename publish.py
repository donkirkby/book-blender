import typing
from itertools import zip_longest
from pathlib import Path
from tempfile import NamedTemporaryFile

from fitz import fitz
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfdoc import PDFInfo
from reportlab.platypus import SimpleDocTemplate
from textstat import textstat

from blender_block import BlenderBlock
from block_pair import BlockPair
from footer import FooterCanvas
from svg_diagram import SvgDiagram


def write_blocks(blocks: typing.Sequence[BlenderBlock], out_path: Path) -> bool:
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

    with NamedTemporaryFile(prefix='book-blender',
                            suffix='.pdf',
                            delete_on_close=False) as tmp_ctx:
        tmp_ctx.file.close()
        doc = SimpleDocTemplate(tmp_ctx.name,
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
        is_changed = False
        if not out_path.exists():
            is_changed = True
        else:
            new_doc = fitz.open(tmp_ctx.name)
            old_doc = fitz.open(out_path)
            if new_doc.page_count != old_doc.page_count:
                is_changed = True
            else:
                dpi = 72
                for i in range(new_doc.page_count):
                    new_page = new_doc.load_page(i).get_pixmap(dpi=dpi)
                    old_page = old_doc.load_page(i).get_pixmap(dpi=dpi)
                    if new_page.tobytes() != old_page.tobytes():
                        is_changed = True
                        break
        if is_changed:
            Path(tmp_ctx.name).rename(out_path)
        return is_changed


def find_mod_time(project_path: Path) -> float:
    return max(file_path.stat().st_mtime
               for file_path in project_path.rglob('*.py'))


def main() -> None:
    project_path = Path(__file__).parent
    code_mod_time = find_mod_time(project_path)
    books_path = project_path / 'docs' / 'solutions'
    for in_path in sorted(books_path.glob('*.md')):
        name_base = in_path.with_suffix('.pdf').name
        if name_base == 'index.pdf':
            continue
        in_mod_time = in_path.stat().st_mtime
        out_path = project_path / 'docs' / name_base
        out_mod_time = out_path.stat().st_mtime
        is_changed = (not out_path.exists() or
                      out_mod_time < in_mod_time or
                      out_mod_time < code_mod_time)
        source = in_path.read_text()
        level = textstat.text_standard(source)
        word_count = textstat.lexicon_count(source)

        if is_changed:
            blocks = BlenderBlock.read(source, width=30, height=6, scale=0.5398)
            is_changed = write_blocks(blocks, out_path)
        action = 'generated' if is_changed else 'skipped'
        print(f'{word_count} words, {level} in {name_base}, {action}.')

    print('Done.')


if __name__ == '__main__':
    main()
