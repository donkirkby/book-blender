from reportlab.pdfgen import canvas


class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, is_booklet=False, font_name='Times-Roman', **kwargs):
        super().__init__(*args, **kwargs)
        self.is_booklet = is_booklet
        self.font_name = font_name
        self.previous_bottom = 0

    def showPage(self):
        self.draw_canvas()
        super().showPage()

    def draw_canvas(self):
        x = 30
        width, height = self._pagesize
        bottom = 70

        self.saveState()
        self.setFont(self.font_name, 8 if self.is_booklet else 9)
        if self._pageNumber == 1:
            message = ("Find the solution and more blended books at "
                       "https://donkirkby.github.io/book-blender")
            self.drawCentredString(width / 2,
                                   bottom,
                                   message)
            self.linkURL("https://donkirkby.github.io/book-blender",
                         (0, bottom - 2, width, bottom + 10))
        elif self._pageNumber % 2:
            self.drawRightString(width-x, bottom, str(self._pageNumber))
        else:
            self.drawString(x, bottom, str(self._pageNumber))
        self.restoreState()
