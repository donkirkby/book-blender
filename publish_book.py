from pathlib import Path

from reportlab.platypus import SimpleDocTemplate, Paragraph, Flowable


class Book:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.flowables: list[Flowable] = []

    def add_paragraph(self, text):
        self.flowables.append(Paragraph(text))

    def build(self):
        doc = SimpleDocTemplate(str(self.path))
        doc.build(self.flowables)


def main():
    filename = 'foo.pdf'
    doc = SimpleDocTemplate(filename)
    flowables = [Paragraph('Foo'), Paragraph('Bar')]
    doc.build(flowables)


if __name__ == '__main__':
    main()
