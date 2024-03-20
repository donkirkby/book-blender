from io import StringIO
from textwrap import dedent

from svgwrite import Drawing
from svgwrite.shapes import Rect
from svgwrite.text import Text

from blender_block import BlenderBlock
from live_svg import LiveSvg
from svg_diagram import SvgDiagram


def test_text():
    text = dedent("""\
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacus
        augue, sagittis at tortor id, condimentum mollis nibh. Sed lectus metus,
        bibendum sit amet finibus venenatis, vehicula vel ipsum.
        
        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.""")
    expected_lines1 = ('Lorem ipsum dolor sit amet, consectetur ',
                       'adipiscing elit. Mauris lacus augue,    ',
                       'sagittis at tortor id, condimentum      ',
                       'mollis nibh. Sed lectus metus, bibendum ',
                       'sit amet finibus venenatis, vehicula vel',
                       'ipsum.                                  ',
                       'Donec ultricies magna vitae risus       ',
                       'vestibulum congue. Morbi sed metus      ')
    expected_lines2 = ('nulla. Nullam ut felis non quam auctor  ',
                       'euismod. Vestibulum ante ipsum primis in',
                       'faucibus orci luctus et ultrices posuere',
                       'cubilia curae.                          ')
    blocks = BlenderBlock.read(StringIO(text))

    assert len(blocks) == 2
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2


def test_text_dimensions():
    text = dedent("""\
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacus
        augue, sagittis at tortor id, condimentum mollis nibh. Sed lectus metus,
        bibendum sit amet finibus venenatis, vehicula vel ipsum.
        
        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.""")
    expected_lines1 = ('Lorem ipsum dolor sit amet, consectetur adipiscing',
                       'elit. Mauris lacus augue, sagittis at tortor id,  ',
                       'condimentum mollis nibh. Sed lectus metus,        ',
                       'bibendum sit amet finibus venenatis, vehicula vel ',
                       'ipsum.                                            ',
                       'Donec ultricies magna vitae risus vestibulum      ')
    expected_lines2 = ('congue. Morbi sed metus nulla. Nullam ut felis non',
                       'quam auctor euismod. Vestibulum ante ipsum primis ',
                       'in faucibus orci luctus et ultrices posuere       ',
                       'cubilia curae.                                    ')
    width = 50
    height = 6
    blocks = BlenderBlock.read(StringIO(text), width, height)

    assert len(blocks) == 2
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2


def test_draw(image_differ):
    expected_drawing = Drawing(size=(440, 200))
    grey = 'rgb(200, 200, 200)'
    expected_drawing.add(Rect((80, 0),
                              (70, 200),
                              fill=grey))
    expected_drawing.add(Rect((220, 0),
                              (70, 200),
                              fill=grey))
    expected_drawing.add(Rect((360, 0),
                              (70, 200),
                              fill=grey))
    expected_drawing.add(Rect((0, 0),
                              (440, 140),
                              fill_opacity=0,
                              stroke='black'))
    expected_drawing.add(Rect((0, 0),
                              (440, 200),
                              fill_opacity=0,
                              stroke='black'))
    expected_drawing.add(Text('____ ___ _ "______" ____.',
                              (10, 40),
                              font_family='Courier',
                              font_size=20,
                              letter_spacing=2))
    expected_drawing.add(Text('amry adh a\xa0 eilltt\xa0 ablm',
                              (10, 60),
                              font_family='Courier',
                              font_size=20,
                              letter_spacing=2))
    expected_drawing.add(Text('___ ______ ___ _____ __ ____.',
                              (10, 100),
                              font_family='Courier',
                              font_size=20,
                              letter_spacing=2))
    expected_drawing.add(Text('ist ceeefl asw ehitw as nosw',
                              (10, 120),
                              font_family='Courier',
                              font_size=20,
                              letter_spacing=2))
    expected_drawing.add(Text('iaryfhadca waitthetelambsnow',
                              (10, 160),
                              font_family='Courier',
                              font_size=20,
                              letter_spacing=2))
    expected_drawing.add(Text('mts\xa0 lee e\xa0 ls wli \xa0 as',
                              (10, 180),
                              font_family='Courier',
                              font_size=20,
                              letter_spacing=2))
    expected_svg = expected_drawing.tostring()

    block = BlenderBlock(('Mary had a "little" lamb.     ',
                          'Its fleece was white as snow. '))
    actual_svg = block.as_svg()

    image_differ.assert_equal(LiveSvg(SvgDiagram(actual_svg)),
                              LiveSvg(SvgDiagram(expected_svg)))
