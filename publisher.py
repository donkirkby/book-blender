from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile

from pymupdf import pymupdf
from textstat import textstat


def find_mod_time(project_path: Path) -> float:
    return max(file_path.stat().st_mtime
               for file_path in project_path.rglob('*.py'))


class Publisher:
    def __init__(self):
        self.project_path = Path(__file__).parent
        self.books_path = self.project_path / 'docs' / 'solutions'
        self.is_optimized = True
        self.old_size_text = ''
        self.new_size_text = ''
        self.content_summary = ''

    def publish(self) -> None:
        code_mod_time = find_mod_time(self.project_path)
        for in_path in sorted(self.books_path.glob('*.md')):
            name_base = in_path.with_suffix('.pdf').name
            if name_base == 'index.pdf':
                continue
            in_mod_time = in_path.stat().st_mtime
            out_path = self.project_path / 'docs' / name_base
            if not out_path.exists():
                is_changed = True
            else:
                out_mod_time = out_path.stat().st_mtime
                is_changed = (out_mod_time < in_mod_time or
                              out_mod_time < code_mod_time)
            source = in_path.read_text()
            level = textstat.text_standard(source)
            word_count = textstat.lexicon_count(source)
            self.content_summary = f'{word_count} words'

            if is_changed:
                is_changed = self.generate(source, out_path)
            if not is_changed:
                action = 'skipped'
            else:
                action = f'generated {self.old_size_text} -> {self.new_size_text}'
            print(f'{self.content_summary}, {level} in {name_base}, {action}.')

    def generate(self, source: str, out_path: Path) -> bool:
        """ Generate one PDF from its input markdown, if needed.

        :return bool: True if a new file was generated. Either out_path didn't
         exist, or had different contents from the newly generated file.
        """
        with NamedTemporaryFile(prefix='book-blender',
                                suffix='.pdf',
                                delete_on_close=False) as tmp_ctx:
            tmp_ctx.file.close()
            tmp_path = Path(tmp_ctx.name)
            self.write(source, tmp_path)
            is_changed = False
            if not out_path.exists():
                is_changed = True
            else:
                new_doc = pymupdf.open(tmp_ctx.name)
                old_doc = pymupdf.open(out_path)
                if new_doc.page_count != old_doc.page_count:
                    is_changed = True
                else:
                    dpi = 72
                    for i in range(new_doc.page_count):
                        new_page = new_doc.load_page(i).get_pixmap(dpi=dpi)
                        old_page = old_doc.load_page(i).get_pixmap(dpi=dpi)
                        if new_page.tobytes() != old_page.tobytes():
                            is_changed = True
                            break
            if is_changed:
                tmp_path.rename(out_path)

        if is_changed and self.is_optimized:
            old_size = out_path.lstat().st_size
            try:
                run(['pdfsizeopt', '--v=30', out_path, out_path], check=True)
            except FileNotFoundError:
                self.is_optimized = False
            new_size = out_path.lstat().st_size
            if new_size != old_size:
                self.old_size_text = human_format_size(old_size)
                self.new_size_text = human_format_size(new_size)
        return is_changed

    def write(self, source: str, out_path: Path) -> None:
        """ Write one PDF from its input markdown. """
        raise NotImplementedError()


def human_format_size(num: float) -> str:
    """
    Human-readable formatting of bytes, using binary (powers of 1024)
    """

    assert isinstance(num, int), "num must be an int"
    assert num > 0, "num must be positive"

    unit_labels: list[str] = ["B", "kB", "MB", "GB"]
    last_label = unit_labels[-1]
    unit_step = 1024
    unit_step_thresh = unit_step - 0.5

    for unit in unit_labels:
        if num < unit_step_thresh:
            # VERY IMPORTANT:
            # Only accepts the CURRENT unit if we're BELOW the threshold where
            # float rounding behavior would place us into the NEXT unit: F.ex.
            # when rounding a float to 1 decimal, any number ">= 1023.95" will
            # be rounded to "1024.0". Obviously we don't want ugly output such
            # as "1024.0 KiB", since the proper term for that is "1.0 MiB".
            break
        if unit != last_label:
            # We only shrink the number if we HAVEN'T reached the last unit.
            # NOTE: These looped divisions accumulate floating point rounding
            # errors, but each new division pushes the rounding errors further
            # and further down in the decimals, so it doesn't matter at all.
            num /= unit_step

    # noinspection PyUnboundLocalVariable
    return f"{num:.0f}{unit}"
