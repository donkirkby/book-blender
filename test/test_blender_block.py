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
        primis in faucibus orci luctus et ultrices posuere cubilia curae.
        
        Nunc ultrices enim velit, ac imperdiet neque eleifend a. Integer mollis
        eget nulla vel faucibus. Donec in volutpat odio. Donec hendrerit nisl
        leo, nec imperdiet orci sollicitudin sit amet. Nam ut nunc at arcu
        feugiat vestibulum. Ut luctus eu nisl ac venenatis. Integer porta varius
        eros sit amet elementum. Sed arcu sapien, porta ut nisl quis, convallis
        molestie metus.""")
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
                       'cubilia curae.                          ',
                       'Nunc ultrices enim velit, ac imperdiet  ',
                       'neque eleifend a. Integer mollis eget   ',
                       'nulla vel faucibus. Donec in volutpat   ')
    expected_lines3 = ('odio. Donec hendrerit nisl leo, nec     ',
                       'imperdiet orci sollicitudin sit amet.   ',
                       'Nam ut nunc at arcu feugiat vestibulum. ',
                       'Ut luctus eu nisl ac venenatis. Integer ',
                       'porta varius eros sit amet elementum.   ',
                       'Sed arcu sapien, porta ut nisl quis,    ',
                       'convallis molestie metus.               ')
    blocks = BlenderBlock.read(text)

    assert len(blocks) == 3
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2
    assert blocks[2].lines == expected_lines3


def test_text_dimensions():
    text = dedent("""\
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacus
        augue, sagittis at tortor id, condimentum mollis nibh. Sed lectus metus,
        bibendum sit amet finibus venenatis, vehicula vel ipsum.
        
        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.
        
        Nunc ultrices enim velit.""")
    expected_lines1 = ('Lorem ipsum dolor sit amet, consectetur adipiscing',
                       'elit. Mauris lacus augue, sagittis at tortor id,  ',
                       'condimentum mollis nibh. Sed lectus metus,        ',
                       'bibendum sit amet finibus venenatis, vehicula vel ',
                       'ipsum.                                            ',
                       'Donec ultricies magna vitae risus vestibulum      ')
    expected_lines2 = ('congue. Morbi sed metus nulla. Nullam ut felis non',
                       'quam auctor euismod. Vestibulum ante ipsum primis ',
                       'in faucibus orci luctus et ultrices posuere       ',
                       'cubilia curae.                                    ',
                       'Nunc ultrices enim velit.                         ')
    width = 50
    height = 6
    blocks = BlenderBlock.read(text, width, height)

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
                       'ipsum.                                  ')
    expected_lines2 = ('Donec ultricies magna vitae risus       ',
                       'vestibulum congue. Morbi sed metus      ',
                       'nulla. Nullam ut felis non quam auctor  ',
                       'euismod. Vestibulum ante ipsum primis in',
                       'faucibus orci luctus et ultrices posuere',
                       'cubilia curae.                          ')
    blocks = BlenderBlock.read(text)

    assert len(blocks) == 2
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2
    assert blocks[0].title == 'Blender Test'
    assert blocks[0].subtitle == 'by Mr. Blends'


def test_heading():
    text = dedent("""\
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacus
        augue, sagittis at tortor id, condimentum mollis nibh.

        # Chapter II
        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.""")
    expected_lines1 = ('Lorem ipsum dolor sit amet, consectetur ',
                       'adipiscing elit. Mauris lacus augue,    ',
                       'sagittis at tortor id, condimentum      ',
                       'mollis nibh.                            ',
                       '                                        ',
                       'Donec ultricies magna vitae risus       ')
    expected_lines2 = ('vestibulum congue. Morbi sed metus      ',
                       'nulla. Nullam ut felis non quam auctor  ',
                       'euismod. Vestibulum ante ipsum primis in',
                       'faucibus orci luctus et ultrices posuere',
                       'cubilia curae.                          ')
    blocks = BlenderBlock.read(text)

    assert len(blocks) == 2
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2
    assert blocks[0].headings == ['', '', '', '', 'Chapter II', '']


def test_heading_and_title():
    text = dedent("""\
        ---
        title: Lorem Ipsum
        ---
        # Chapter I
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.

        # Chapter II
        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.""")
    expected_lines1 = ('                                        ',
                       '                                        ',
                       'Lorem ipsum dolor sit amet, consectetur ',
                       'adipiscing elit.                        ',
                       '                                        ',
                       'Donec ultricies magna vitae risus       ')
    expected_lines2 = ('vestibulum congue. Morbi sed metus      ',
                       'nulla. Nullam ut felis non quam auctor  ',
                       'euismod. Vestibulum ante ipsum primis in',
                       'faucibus orci luctus et ultrices posuere',
                       'cubilia curae.                          ')
    blocks = BlenderBlock.read(text)

    assert len(blocks) == 2
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2
    assert blocks[0].headings == ['', 'Chapter I', '', '', 'Chapter II', '']


def test_heading_at_page_end_without_room():
    text = dedent("""\
        # Chapter I
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacus
        augue, sagittis at tortor id, condimentum mollis nibh.

        # Chapter II
        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.""")
    expected_lines1 = ('                                        ',
                       'Lorem ipsum dolor sit amet, consectetur ',
                       'adipiscing elit. Mauris lacus augue,    ',
                       'sagittis at tortor id, condimentum      ',
                       'mollis nibh.                            ')
    expected_lines2 = ('                                        ',
                       'Donec ultricies magna vitae risus       ',
                       'vestibulum congue. Morbi sed metus      ',
                       'nulla. Nullam ut felis non quam auctor  ')
    expected_lines3 = ('euismod. Vestibulum ante ipsum primis in',
                       'faucibus orci luctus et ultrices posuere',
                       'cubilia curae.                          ')
    blocks = BlenderBlock.read(text, height=6)

    assert len(blocks) == 3
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2
    assert blocks[2].lines == expected_lines3
    assert blocks[0].headings == ['Chapter I', '', '', '', '']
    assert blocks[1].headings == ['Chapter II', '', '', '']
    assert blocks[2].headings == ['', '', '']


def test_heading_at_page_end_with_room():
    text = dedent("""\
        # Chapter I
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacus
        augue, sagittis at tortor id, condimentum mollis nibh.

        # Chapter II
        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.""")
    expected_lines1 = ('                                        ',
                       'Lorem ipsum dolor sit amet, consectetur ',
                       'adipiscing elit. Mauris lacus augue,    ',
                       'sagittis at tortor id, condimentum      ',
                       'mollis nibh.                            ',
                       '                                        ',
                       'Donec ultricies magna vitae risus       ')
    expected_lines2 = ('vestibulum congue. Morbi sed metus      ',
                       'nulla. Nullam ut felis non quam auctor  ',
                       'euismod. Vestibulum ante ipsum primis in',
                       'faucibus orci luctus et ultrices posuere',
                       'cubilia curae.                          ')
    blocks = BlenderBlock.read(text, height=7)

    assert len(blocks) == 2
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2
    assert blocks[0].headings == ['Chapter I', '', '', '', '', 'Chapter II', '']
    assert blocks[1].headings == ['', '', '', '', '']


def test_text_style():
    text = dedent("""\
        Lorem *ipsum* dolor _sit_ amet, **consectetur** adipiscing __elit__.""")
    expected_lines = ('Lorem ipsum dolor sit amet, consectetur ',
                      'adipiscing elit.                        ')
    blocks = BlenderBlock.read(text)

    assert len(blocks) == 1
    assert blocks[0].lines == expected_lines


def test_draw(image_differ):
    sp = ' '
    nbsp = '\xa0'
    expected_drawing = Drawing(size=(380, 210))
    grey = 'rgb(240, 240, 240)'
    expected_drawing.add(Rect((70, 10),
                              (60, 180),
                              fill=grey))
    expected_drawing.add(Rect((190, 10),
                              (60, 180),
                              fill=grey))
    expected_drawing.add(Rect((310, 10),
                              (60, 180),
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
    expected_drawing.add(Text('                    -  -    .'.replace(sp, nbsp),
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
                                'Its fleece was white-as-snow. '),
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
                              (190, 45),
                              font_family='Helvetica',
                              text_anchor='middle',
                              font_size=27))
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
                              (190, 45),
                              font_family='Helvetica',
                              text_anchor='middle',
                              font_size=27))
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


# noinspection DuplicatedCode
def test_draw_heading(image_differ):
    expected_drawing = Drawing(size=(380, 290))
    expected_block = BlenderBlock(lines=('Mary had a "little" lamb.     ',
                                         '                              ',
                                         'Its fleece was white as snow. '),
                                  scale=1.0)
    expected_block.draw(expected_drawing)
    expected_drawing.add(Text('Chapter II',
                              (10, 107),
                              font_family='Helvetica',
                              text_anchor='start',
                              font_size=20))
    expected_svg = expected_drawing.tostring()

    block = BlenderBlock(lines=('Mary had a "little" lamb.     ',
                                '                              ',
                                'Its fleece was white as snow. '),
                         scale=1.0)
    block.headings[1] = 'Chapter II'
    actual_svg = block.as_svg()

    image_differ.assert_equal(LiveSvg(SvgDiagram(actual_svg)),
                              LiveSvg(SvgDiagram(expected_svg)))
