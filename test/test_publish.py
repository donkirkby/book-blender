from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate

from blender_block import BlenderBlock
from block_pair import BlockPair
from footer import FooterCanvas
from live_pdf import LivePdf
from publish import write_blocks
from svg_diagram import SvgDiagram


def test(tmp_path, image_differ):
    scale = 0.5398
    blocks = [BlenderBlock(lines=('Lorem ipsum dolor sit amet,   ',
                                  'consectetur adipiscing elit.  ',
                                  'Mauris lacus augue, sagittis  ',
                                  'at tortor id, condimentum     ',
                                  'mollis nibh. Sed lectus metus,',
                                  'bibendum sit amet finibus     '),
                           scale=scale),
              BlenderBlock(lines=('venenatis, vehicula vel ipsum.',
                                  'Donec ultricies magna vitae   ',
                                  'risus vestibulum congue. Morbi',
                                  'sed metus nulla. Nullam ut    ',
                                  'felis non quam auctor euismod.',
                                  'Vestibulum ante ipsum primis  '),
                           scale=scale),
              BlenderBlock(lines=('in faucibus orci luctus et    ',
                                  'ultrices posuere cubilia      ',
                                  'curae.                        ',
                                  'Ut vestibulum lectus et       ',
                                  'aliquam sollicitudin.Integer  ',
                                  'egestas neque sed lacus cursus'),
                           scale=scale),
              BlenderBlock(lines=('porttitor.Ut quis blandit     ',
                                  'justo. Nulla vel hendrerit    ',
                                  'leo, vitae vehicula est.      '),
                           scale=scale)]
    pairs = [BlockPair(blocks[0], blocks[1]),
             BlockPair(blocks[2], blocks[3])]
    expected_path = tmp_path / "expected.pdf"
    expected_doc = SimpleDocTemplate(str(expected_path),
                                     leftMargin=inch * 1.1,
                                     rightMargin=inch * 1.1,
                                     showBoundary=False,
                                     pagesize=pagesizes.letter)

    expected_doc.build([SvgDiagram(pair.as_svg()).to_reportlab()
                        for pair in pairs],
                       canvasmaker=FooterCanvas)
    expected_pdf = LivePdf(expected_path)

    actual_path = tmp_path / "actual.pdf"
    write_blocks(blocks, actual_path)
    actual_pdf = LivePdf(actual_path)

    image_differ.assert_equal(actual_pdf, expected_pdf)
