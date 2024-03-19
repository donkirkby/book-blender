import typing
from io import BytesIO
from pathlib import Path

from space_tracer import LiveImage

from svg_diagram import SvgDiagram


class LiveSvg(LiveImage):
    def __init__(self, diagram: SvgDiagram):
        super().__init__()
        self.diagram = diagram

    def convert_to_png(self) -> bytes:
        png_alpha_bytes = BytesIO()
        self.write_png(png_alpha_bytes)
        return png_alpha_bytes.getvalue()

    def write_png(self, file: typing.BinaryIO | Path | str):
        self.diagram.to_cairo(file)

    def save(self, file_path: Path) -> Path:
        """ Save the image to a file.

        :param file_path: The path to save the file to, without an extension.
        :return: The path of the saved file, with an extension.
        """
        extended_path = file_path.with_suffix('.svg')
        extended_path.write_text(self.diagram.svg_text)
        return extended_path
