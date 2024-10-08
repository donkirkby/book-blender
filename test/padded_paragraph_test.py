from padded_paragraph import PaddedParagraph

TEST_TEXT = """\
    When he heard a voice thus calling to him, he was standing at the
    door of his box, with a flag in his hand, furled round its short
    pole. One would have thought, considering the nature of the ground,
    that he could not have doubted from what quarter the voice came;
    but, instead of looking up to where I stood on the top of the steep
    cutting nearly over his head, he turned himself about and looked
    down the Line. There was something remarkable in his manner of
    doing so, though I could not have said, for my life, what. But I
    know it was remarkable enough to attract my notice, even though
    his figure was foreshortened and shadowed, down in the deep trench,
    and mine was high above him, and so steeped in the glow of an angry
    sunset that I had shaded my eyes with my hand before I saw him at
    all."""


def test_find_line_endings():
    paragraph = PaddedParagraph(TEST_TEXT)
    paragraph.wrap(234, 500)
    expected_line_endings = 'xxxxxxxxxxxxxxxx.'

    line_endings = paragraph.get_line_endings()

    assert line_endings == expected_line_endings


def test_find_all_line_endings():
    paragraph = PaddedParagraph(TEST_TEXT)
    expected_all_line_endings = [(0, 'xxxxxxxxxxxxxxxx.'),
                                 (8, 'xxxxxxxxxxxxxxxxx.'),
                                 (14, 'xxxxxxxx.xxxxxxxx.'),
                                 (16, 'xx.xxxxxxxxxxxxxxx.'),
                                 (20, 'xxxxxxxxxxxxxxxxxxx.')]

    paragraph.find_all_line_endings(234)

    assert paragraph.all_line_endings == expected_all_line_endings


def test_find_line_endings_with_fragments():
    paragraph = PaddedParagraph(
        "The <em>quick</em> brown fox jumps over the lazy dog.")
    paragraph.wrap(234, 500)
    expected_line_endings = '.'

    line_endings = paragraph.get_line_endings()

    assert line_endings == expected_line_endings


def test_find_line_endings_with_final_fragment():
    paragraph = PaddedParagraph(
        "The quick brown fox jumps over the lazy <em>dog.</em>")
    paragraph.wrap(234, 500)
    expected_line_endings = '.'

    line_endings = paragraph.get_line_endings()

    assert line_endings == expected_line_endings


def test_find_line_endings_with_multiline_fragments():
    paragraph = PaddedParagraph(
        "The quick brown fox jumps over the lazy <em>dog.</em>")
    paragraph.wrap(80, 500)
    expected_line_endings = 'xx.'

    line_endings = paragraph.get_line_endings()

    assert line_endings == expected_line_endings
