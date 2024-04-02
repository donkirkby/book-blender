from svgwrite import Drawing
from svgwrite.path import Path
from svgwrite.shapes import Rect

from blender_block import BlenderBlock, LETTER_WIDTH


class BlockPair:
    def __init__(self,
                 left: BlenderBlock,
                 right: BlenderBlock | None = None) -> None:
        self.left = left
        self.right = right

    def as_svg(self) -> str:
        scale = self.left.scale
        trim = round(LETTER_WIDTH * scale * 0.2)  # tiny outer edge
        margin = round(LETTER_WIDTH * scale * 0.9)  # gap for cover and shadow
        gutter = round(LETTER_WIDTH * scale * 1.3)  # along book spine
        cover_gray = 'rgb(100, 100, 100)'
        shadow_gray = 'rgb(220, 220, 220)'

        left_width = self.left.width * scale
        left_height = self.left.height * scale
        drawing = Drawing(size=(round(2 * (gutter + left_width) + 3.2 * margin),
                                round(left_height + 6.3 * margin)))

        drawing.add(Rect((trim, trim+margin),
                         size=(round(2*(left_width+gutter) + 2.7 * margin),
                               round(left_height + 2.5 * margin)),
                         fill=cover_gray,
                         stroke='black',
                         stroke_width=trim/2))
        drawing.add(Rect((trim+margin, trim+margin),
                         size=(round(2*(left_width+gutter) + 0.8 * margin),
                               round(left_height + 1.3 * margin)),
                         fill=shadow_gray,
                         stroke='black',
                         stroke_width=trim/2))
        h_span = round(left_width - 2.9 * gutter)
        drawing.add(Path(d=('M', trim + margin, trim,
                            'h', h_span,
                            'c', round(3.3 * gutter), 0,
                            round(4.2*gutter), margin,
                            round(4.2*gutter), margin,
                            'v', round(left_height + margin * 1.2),
                            'v', -round(left_height + margin * 1.2),
                            'c', 0, 0,
                            round(0.8 * gutter), -margin,
                            round(4.2 * gutter), -margin,
                            'h', h_span,
                            'v', round(left_height + margin * 1.2),
                            'h', -h_span,
                            'c', -round(3.3 * gutter), 0,
                            -round(4.2*gutter), margin,
                            -round(4.2*gutter), margin,
                            'c', 0, 0,
                            -round(0.8 * gutter), -margin,
                            -round(4.2 * gutter), -margin,
                            'h', -h_span,
                            'z'),
                         fill='white',
                         stroke='black',
                         stroke_width=trim/2))

        left_group = self.left.draw(drawing)
        left_offset = (2 * trim + margin) / scale
        left_group.translate(round(left_offset), round(margin / scale))

        if self.right is not None:
            right_group = self.right.draw(drawing)
            right_group.translate(round(left_offset + self.left.width +
                                        2.05 * gutter / scale),
                                  round(margin / scale))

        return drawing.tostring()
