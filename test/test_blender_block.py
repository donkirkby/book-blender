from io import StringIO
from textwrap import dedent

from blender_block import BlenderBlock


def test_text():
    text = dedent("""\
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacus
        augue, sagittis at tortor id, condimentum mollis nibh. Sed lectus metus,
        bibendum sit amet finibus venenatis, vehicula vel ipsum.
        
        Donec ultricies magna vitae risus vestibulum congue. Morbi sed metus
        nulla. Nullam ut felis non quam auctor euismod. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae.""")
    expected_lines1 = ('Lorem ipsum dolor sit amet, consectetur',
                       'adipiscing elit. Mauris lacus augue,',
                       'sagittis at tortor id, condimentum',
                       'mollis nibh. Sed lectus metus, bibendum',
                       'sit amet finibus venenatis, vehicula vel',
                       'ipsum.',
                       'Donec ultricies magna vitae risus',
                       'vestibulum congue. Morbi sed metus')
    expected_lines2 = ('nulla. Nullam ut felis non quam auctor',
                       'euismod. Vestibulum ante ipsum primis in',
                       'faucibus orci luctus et ultrices posuere',
                       'cubilia curae.')
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
                       'elit. Mauris lacus augue, sagittis at tortor id,',
                       'condimentum mollis nibh. Sed lectus metus,',
                       'bibendum sit amet finibus venenatis, vehicula vel',
                       'ipsum.',
                       'Donec ultricies magna vitae risus vestibulum')
    expected_lines2 = ('congue. Morbi sed metus nulla. Nullam ut felis non',
                       'quam auctor euismod. Vestibulum ante ipsum primis',
                       'in faucibus orci luctus et ultrices posuere',
                       'cubilia curae.')
    width = 50
    height = 6
    blocks = BlenderBlock.read(StringIO(text), width, height)

    assert len(blocks) == 2
    assert blocks[0].lines == expected_lines1
    assert blocks[1].lines == expected_lines2
