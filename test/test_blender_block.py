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


def test_title():
    text = dedent("""\
        ---
        title: Blender Test
        subtitle: by Mr. Blends
        ---
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacus
        augue, sagittis at tortor id, condimentum mollis nibh. Sed lectus metus,
        bibendum sit amet finibus venenatis, vehicula vel ipsum.

        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.""")
    expected_lines1 = ('                                        ',
                       'Lorem ipsum dolor sit amet, consectetur ',
                       'adipiscing elit. Mauris lacus augue,    ',
                       'sagittis at tortor id, condimentum      ',
                       'mollis nibh. Sed lectus metus, bibendum ',
                       'sit amet finibus venenatis, vehicula vel',
                       'ipsum.                                  ',
                       'Donec ultricies magna vitae risus       ')
    expected_lines2 = ('vestibulum congue. Morbi sed metus      ',
                       'nulla. Nullam ut felis non quam auctor  ',
                       'euismod. Vestibulum ante ipsum primis in',
                       'faucibus orci luctus et ultrices posuere',
                       'cubilia curae.                          ')
    blocks = BlenderBlock.read(StringIO(text))

    assert len(blocks) == 2
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2
    assert blocks[0].title == 'Blender Test'
    assert blocks[0].subtitle == 'by Mr. Blends'


def test_draw(image_differ):
    sp = ' '
    nbsp = '\xa0'
    expected_drawing = Drawing(size=(380, 210))
    grey = 'rgb(240, 240, 240)'
    expected_drawing.add(Rect((70, 20),
                              (60, 170),
                              fill=grey))
    expected_drawing.add(Rect((190, 20),
                              (60, 170),
                              fill=grey))
    expected_drawing.add(Rect((310, 20),
                              (60, 170),
                              fill=grey))
    expected_drawing.add(Text('           "      "     .'.replace(sp, nbsp),
                              (10, 40),
                              font_family='Courier',
                              font_size=20))
    expected_drawing.add(Text('---- --- -  ------  ---- '.replace(sp, nbsp),
                              (10, 47),
                              font_family='Courier',
                              font_size=20))
    expected_drawing.add(Text('amry adh a  eilltt  ablm'.replace(sp, nbsp),
                              (10, 60),
                              font_family='Courier',
                              font_size=20))
    expected_drawing.add(Text('                            .'.replace(sp, nbsp),
                              (10, 100),
                              font_family='Courier',
                              font_size=20))
    expected_drawing.add(Text('--- ------ --- ----- -- ----',
                              (10, 107),
                              font_family='Courier',
                              font_size=20))
    expected_drawing.add(Text('ist ceeefl asw ehitw as nosw',
                              (10, 120),
                              font_family='Courier',
                              font_size=20))
    expected_drawing.add(Text('iaryfhadca waitthetelambsnow',
                              (10, 160),
                              font_family='Courier',
                              font_size=20))
    expected_drawing.add(Text('mts\xa0 lee e\xa0 ls wli \xa0 as',
                              (10, 180),
                              font_family='Courier',
                              font_size=20))
    expected_drawing.add(Text('* * *',
                              (190, 140),
                              font_family='Courier',
                              text_anchor='middle',
                              font_size=20))
    expected_svg = expected_drawing.tostring()

    block = BlenderBlock(lines=('Mary had a "little" lamb.     ',
                                'Its fleece was white as snow. '),
                         page=13,
                         scale=1.0)
    actual_svg = block.as_svg()

    image_differ.assert_equal(LiveSvg(SvgDiagram(actual_svg)),
                              LiveSvg(SvgDiagram(expected_svg)))


# noinspection DuplicatedCode
def test_draw_title(image_differ):
    expected_drawing = Drawing(size=(380, 290))
    expected_block = BlenderBlock(lines=('                              ',
                                         'Mary had a "little" lamb.     ',
                                         'Its fleece was white as snow. '),
                                  scale=1.0)
    expected_block.draw(expected_drawing)
    expected_drawing.add(Text('Jaws',
                              (190, 50),
                              font_family='Helvetica',
                              text_anchor='middle',
                              font_size=30))
    expected_svg = expected_drawing.tostring()

    block = BlenderBlock(lines=('                              ',
                                'Mary had a "little" lamb.     ',
                                'Its fleece was white as snow. '),
                         scale=1.0)
    block.title = 'Jaws'
    actual_svg = block.as_svg()

    image_differ.assert_equal(LiveSvg(SvgDiagram(actual_svg)),
                              LiveSvg(SvgDiagram(expected_svg)))


# noinspection DuplicatedCode
def test_draw_subtitle(image_differ):
    expected_drawing = Drawing(size=(380, 290))
    expected_block = BlenderBlock(lines=('                              ',
                                         'Mary had a "little" lamb.     ',
                                         'Its fleece was white as snow. '),
                                  scale=1.0)
    expected_block.draw(expected_drawing)
    expected_drawing.add(Text('Jaws',
                              (190, 50),
                              font_family='Helvetica',
                              text_anchor='middle',
                              font_size=30))
    expected_drawing.add(Text('by Mr. Blender',
                              (190, 70),
                              font_family='Helvetica',
                              text_anchor='middle',
                              font_size=20))
    expected_svg = expected_drawing.tostring()

    block = BlenderBlock(lines=('                              ',
                                'Mary had a "little" lamb.     ',
                                'Its fleece was white as snow. '),
                         scale=1.0)
    block.title = 'Jaws'
    block.subtitle = 'by Mr. Blender'
    actual_svg = block.as_svg()

    image_differ.assert_equal(LiveSvg(SvgDiagram(actual_svg)),
                              LiveSvg(SvgDiagram(expected_svg)))
