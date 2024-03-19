from reportlab.platypus import SimpleDocTemplate, Paragraph

from publish_book import Book
from live_pdf import LivePdf


def test(tmp_path, image_differ):
    expected_path = tmp_path / "expected.pdf"
    expected_doc = SimpleDocTemplate(str(expected_path))
    expected_doc.build([Paragraph("Foo."), Paragraph("Bar.")])
    expected_pdf = LivePdf(expected_path)

    actual_path = tmp_path / "actual.pdf"
    book = Book(actual_path)
    book.add_paragraph('Foo.')
    book.add_paragraph('Bar.')
    book.build()
    actual_pdf = LivePdf(actual_path)

    image_differ.assert_equal(actual_pdf, expected_pdf)
