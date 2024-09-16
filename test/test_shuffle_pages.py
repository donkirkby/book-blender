import pytest
from reportlab.platypus import Paragraph

from shuffle_pages import split_panels


@pytest.mark.parametrize('paragraph_heights,expected_splits',
                         [[[30, 30, 30, 30, 30],
                           [[30, 30, 30], [30, 30]]],
                          [[30, 30, 30, 30],
                           [[30, 30], [30, 30]]],
                          [[10] * 11,
                           [[10] * 6, [10] * 5]]
                          ])
def test(paragraph_heights: list[int], expected_splits: list[list[int]]):
    page_height = 100

    paragraphs: list[Paragraph] = []
    for height in paragraph_heights:
        paragraph = Paragraph('Example text.')
        paragraph.height = height
        paragraphs.append(paragraph)

    panels = split_panels(paragraphs, page_height)

    splits = [[paragraph.height for paragraph in panel.paragraphs]
              for panel in panels]
    assert splits == expected_splits
