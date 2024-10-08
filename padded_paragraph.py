import re

from reportlab.platypus import Paragraph, FragLine, ParaLines


class PaddedParagraph(Paragraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_padding = 0
        self.all_line_endings = []

    # noinspection PyPep8Naming
    def wrap(self, availWidth, availHeight):
        width, height = super().wrap(availWidth - self.extra_padding, availHeight)
        padded_lines = []
        for line in self.blPara.lines:
            if isinstance(line, FragLine) or isinstance(line, ParaLines):
                # noinspection PyUnresolvedReferences
                line.extraSpace += self.extra_padding
                padded_lines.append(line)
            else:
                unused_space, words = line
                padded_lines.append((unused_space+self.extra_padding*2, words))
        self.blPara.lines = padded_lines
        return width + self.extra_padding, height

    def breakLines(self, width):
        first_line_width, later_width = width
        return super().breakLines([first_line_width - self.extra_padding,
                                   later_width - self.extra_padding])

    # noinspection PyPep8Naming
    def split(self, availWidth, availHeight):
        pieces = super().split(availWidth - self.extra_padding, availHeight)
        for piece in pieces:
            piece.extra_padding = self.extra_padding
        return pieces

    def get_line_endings(self) -> str:
        lines = self.blPara.lines
        line_endings = []
        for line in lines:
            if isinstance(line, tuple):
                unused_space, words = line
                last_chunk = words[-1]
            else:
                assert isinstance(line, (ParaLines, FragLine))
                # noinspection PyUnresolvedReferences
                last_chunk = line.words[-1].text
            if re.match(r'.*\w[.?!]\W*$', last_chunk):
                line_ending = '.'
            else:
                line_ending = 'x'
            line_endings.append(line_ending)
        return ''.join(line_endings)

    def find_all_line_endings(self, avail_width) -> None:
        old_extra_padding = self.extra_padding
        seen_line_endings = set()
        for extra_padding in range(avail_width // 10):
            self.extra_padding = extra_padding
            self.wrap(avail_width, avail_width)
            line_endings = self.get_line_endings()
            if line_endings not in seen_line_endings:
                self.all_line_endings.append((self.extra_padding, line_endings))
                seen_line_endings.add(line_endings)
        self.extra_padding = old_extra_padding
