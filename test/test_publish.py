from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

from blender_block import BlenderBlock
from live_pdf import LivePdf
from publish_book import write_blocks
from svg_diagram import SvgDiagram


def test(tmp_path, image_differ):
    blocks = [BlenderBlock(lines=('Lorem ipsum dolor sit amet,   ',
                                  'consectetur adipiscing elit.  ',
                                  'Mauris lacus augue, sagittis  ',
                                  'at tortor id, condimentum     ',
                                  'mollis nibh. Sed lectus metus,',
                                  'bibendum sit amet finibus     '),
                           page=1,
                           scale=0.58),
              BlenderBlock(lines=('venenatis, vehicula vel ipsum.',
                                  'Donec ultricies magna vitae   ',
                                  'risus vestibulum congue. Morbi',
                                  'sed metus nulla. Nullam ut    ',
                                  'felis non quam auctor euismod.',
                                  'Vestibulum ante ipsum primis  '),
                           page=2,
                           scale=0.58),
              BlenderBlock(lines=('in faucibus orci luctus et    ',
                                  'ultrices posuere cubilia      ',
                                  'curae.                        '),
                           page=3,
                           scale=0.58)]
    expected_path = tmp_path / "expected.pdf"
    expected_doc = BaseDocTemplate(str(expected_path), showBoundary=False)

    # Two Columns
    # noinspection PyUnresolvedReferences
    frame1 = Frame(expected_doc.leftMargin,
                   expected_doc.bottomMargin,
                   expected_doc.width / 2 - 6,
                   expected_doc.height)
    # noinspection PyUnresolvedReferences
    frame2 = Frame(expected_doc.leftMargin + expected_doc.width / 2 + 6,
                   expected_doc.bottomMargin,
                   expected_doc.width / 2 - 6,
                   expected_doc.height)

    expected_doc.addPageTemplates([PageTemplate(id='TwoCol',
                                                frames=[frame1, frame2])])

    expected_doc.build([SvgDiagram(block.as_svg()).to_reportlab()
                        for block in blocks])
    expected_pdf = LivePdf(expected_path)

    actual_path = tmp_path / "actual.pdf"
    write_blocks(blocks, actual_path)
    actual_pdf = LivePdf(actual_path)

    image_differ.assert_equal(actual_pdf, expected_pdf)
