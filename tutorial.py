""" Write the starting SVG file for the Fox and Grapes tutorial.

Use Inkscape to add the handwriting for each step. Download Gochi Hand from
fonts.google.com. Convert the handwriting text to paths, so the browser doesn't
need the font installed.
"""

from pathlib import Path

from blender_block import BlenderBlock


def main():
    project_path = Path(__file__).parent
    docs_path = project_path / 'docs'
    in_path = docs_path / 'solutions' / 'fox-and-grapes.md'
    out_path = docs_path / 'images' / 'fox.svg'

    with in_path.open('r') as f:
        blocks = BlenderBlock.read(f, width=30, height=6, scale=0.58*2)

    out_path.write_text(blocks[0].as_svg())
    print(f'Wrote {out_path.relative_to(project_path)}')


main()
