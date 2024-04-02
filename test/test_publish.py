from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate

from blender_block import BlenderBlock
from block_pair import BlockPair
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
                           scale=0.58),
              BlenderBlock(lines=('venenatis, vehicula vel ipsum.',
                                  'Donec ultricies magna vitae   ',
                                  'risus vestibulum congue. Morbi',
                                  'sed metus nulla. Nullam ut    ',
                                  'felis non quam auctor euismod.',
                                  'Vestibulum ante ipsum primis  '),
                           scale=0.58),
              BlenderBlock(lines=('in faucibus orci luctus et    ',
                                  'ultrices posuere cubilia      ',
                                  'curae.                        ',
                                  'Ut vestibulum lectus et       ',
                                  'aliquam sollicitudin.Integer  ',
                                  'egestas neque sed lacus cursus'),
                           scale=0.58),
              BlenderBlock(lines=('porttitor.Ut quis blandit     ',
                                  'justo. Nulla vel hendrerit    ',
                                  'leo, vitae vehicula est.      '),
                           scale=0.58)]
    pairs = [BlockPair(blocks[0], blocks[1]),
             BlockPair(blocks[2], blocks[3])]
    expected_path = tmp_path / "expected.pdf"
    expected_doc = SimpleDocTemplate(str(expected_path),
                                     leftMargin=inch*0.75,
                                     rightMargin=inch*0.75,
                                     showBoundary=False)

    expected_doc.build([SvgDiagram(pair.as_svg()).to_reportlab()
                        for pair in pairs])
    expected_pdf = LivePdf(expected_path)

    actual_path = tmp_path / "actual.pdf"
    write_blocks(blocks, actual_path)
    actual_pdf = LivePdf(actual_path)

    image_differ.assert_equal(actual_pdf, expected_pdf)
