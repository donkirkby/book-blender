from reportlab.pdfgen import canvas


class FooterCanvas(canvas.Canvas):
    @classmethod
    def title_factory(cls, title: str):
        def factory(*args, **kwargs) -> FooterCanvas:
            return cls(title=title, *args, **kwargs)
        return factory

    def __init__(self,
                 *args,
                 is_booklet=False,
                 font_name='Helvetica',
                 title: str = '',
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.is_booklet = is_booklet
        self.font_name = font_name
        self.previous_bottom = 0
        self.title = title
        self._saved_page_states: list[dict] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        for state in self._saved_page_states:
            # annotation_count = getattr(self, '_annotationCount', 0)
            annotation_count = self._annotationCount
            self.__dict__.update(state)
            self._annotationCount = annotation_count
            self.draw_canvas()
            # self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 7)
        self.drawRightString(200*mm, 20*mm,
            "Page %d of %d" % (self._pageNumber, page_count))

    def draw_canvas(self):
        x = 30
        width, height = self._pagesize
        bottom = 70
        top = height - bottom
        num_pages = len(self._saved_page_states)

        self.saveState()
        self.setFont(self.font_name, 8 if self.is_booklet else 9)
        if self._pageNumber in (1, num_pages):
            message = ("Find the solution and more puzzling books at "
                       "https://donkirkby.github.io/book-blender")
            self.drawCentredString(width / 2,
                                   bottom,
                                   message)
            self.linkURL("https://donkirkby.github.io/book-blender",
                         (0, bottom - 2, width, bottom + 10))
        if self._pageNumber == 1:
            pass
        elif self._pageNumber % 2:
            self.drawRightString(width-x, bottom, str(self._pageNumber))
            if self.title:
                self.drawRightString(width-x, top, self.title)
        else:
            self.drawString(x, bottom, str(self._pageNumber))
            if self.title:
                self.drawString(x, top, self.title)
        self.restoreState()
