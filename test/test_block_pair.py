from svgwrite import Drawing
from svgwrite.path import Path
from svgwrite.shapes import Rect

from blender_block import BlenderBlock
from block_pair import BlockPair
from test.live_svg import LiveSvg

from svg_diagram import SvgDiagram


# noinspection DuplicatedCode
def test_draw(image_differ):
    left_block = BlenderBlock(lines=('Mary had a "little" lamb.     ',
                                     'Its fleece was white as snow. '),
                              scale=0.75)
    right_block = BlenderBlock(lines=('+ everywhere that Mary went,  ',
                                      'The lamb was sure to go.      '),
                               scale=0.75)

    expected_drawing = Drawing(size=(620, 200))
    cover_gray = 'rgb(100, 100, 100)'
    shadow_gray = 'rgb(220, 220, 220)'
    expected_drawing.add(Rect((2, 10),
                              (616, 170),
                              fill=cover_gray,
                              stroke='black'))
    expected_drawing.add(Rect((10, 10),
                              (600, 160),
                              fill=shadow_gray,
                              stroke='black'))
    path = Path(d=('M', 10, 2,
                   'h', 250,
                   'c', 40, 0, 50, 8, 50, 8,
                   'v', 160,
                   'v', -160,
                   'c', 0, 0, 10, -8, 50, -8,
                   'h', 250,
                   'v', 160,
                   'h', -250,
                   'c', -40, 0, -50, 8, -50, 8,
                   'c', 0, 0, -10, -8, -50, -8,
                   'h', -250,
                   'z'),
                stroke='black',
                fill='white')
    expected_drawing.add(path)
    left_group = left_block.draw(expected_drawing)
    left_group.translate(16, 11)
    right_group = right_block.draw(expected_drawing)
    right_group.translate(429, 11)
    # expected_drawing.add(Rect((0, 0), (10, 20)))
    expected_svg = expected_drawing.tostring()

    block_pair = BlockPair(left_block, right_block)
    actual_svg = block_pair.as_svg()

    image_differ.assert_equal(LiveSvg(SvgDiagram(actual_svg)),
                              LiveSvg(SvgDiagram(expected_svg)))


# noinspection DuplicatedCode
def test_draw_single(image_differ):
    left_block = BlenderBlock(lines=('Mary had a "little" lamb.     ',
                                     'Its fleece was white as snow. '),
                              scale=0.75)

    expected_drawing = Drawing(size=(620, 200))
    cover_gray = 'rgb(100, 100, 100)'
    shadow_gray = 'rgb(220, 220, 220)'
    expected_drawing.add(Rect((2, 10),
                              (616, 170),
                              fill=cover_gray,
                              stroke='black'))
    expected_drawing.add(Rect((10, 10),
                              (600, 160),
                              fill=shadow_gray,
                              stroke='black'))
    path = Path(d=('M', 10, 2,
                   'h', 250,
                   'c', 40, 0, 50, 8, 50, 8,
                   'v', 160,
                   'v', -160,
                   'c', 0, 0, 10, -8, 50, -8,
                   'h', 250,
                   'v', 160,
                   'h', -250,
                   'c', -40, 0, -50, 8, -50, 8,
                   'c', 0, 0, -10, -8, -50, -8,
                   'h', -250,
                   'z'),
                stroke='black',
                fill='white')
    expected_drawing.add(path)
    left_group = left_block.draw(expected_drawing)
    left_group.translate(16, 11)
    expected_svg = expected_drawing.tostring()

    block_pair = BlockPair(left_block)
    actual_svg = block_pair.as_svg()

    image_differ.assert_equal(LiveSvg(SvgDiagram(actual_svg)),
                              LiveSvg(SvgDiagram(expected_svg)))


# noinspection DuplicatedCode
def test_draw_longer_page(image_differ):
    left_block = BlenderBlock(lines=('Mary had a "little" lamb.     ',),
                              scale=0.75)
    right_block = BlenderBlock(lines=('+ everywhere that Mary went,  ',
                                      'The lamb was sure to go.      '),
                               scale=0.75)

    expected_drawing = Drawing(size=(620, 200))
    cover_gray = 'rgb(100, 100, 100)'
    shadow_gray = 'rgb(220, 220, 220)'
    expected_drawing.add(Rect((2, 10),
                              (616, 170),
                              fill=cover_gray,
                              stroke='black'))
    expected_drawing.add(Rect((10, 10),
                              (600, 160),
                              fill=shadow_gray,
                              stroke='black'))
    path = Path(d=('M', 10, 2,
                   'h', 250,
                   'c', 40, 0, 50, 8, 50, 8,
                   'v', 160,
                   'v', -160,
                   'c', 0, 0, 10, -8, 50, -8,
                   'h', 250,
                   'v', 160,
                   'h', -250,
                   'c', -40, 0, -50, 8, -50, 8,
                   'c', 0, 0, -10, -8, -50, -8,
                   'h', -250,
                   'z'),
                stroke='black',
                fill='white')
    expected_drawing.add(path)
    left_group = left_block.draw(expected_drawing)
    left_group.translate(16, 11)
    right_group = right_block.draw(expected_drawing)
    right_group.translate(429, 11)
    # expected_drawing.add(Rect((0, 0), (10, 20)))
    expected_svg = expected_drawing.tostring()

    block_pair = BlockPair(left_block, right_block)
    actual_svg = block_pair.as_svg()

    image_differ.assert_equal(LiveSvg(SvgDiagram(actual_svg)),
                              LiveSvg(SvgDiagram(expected_svg)))
