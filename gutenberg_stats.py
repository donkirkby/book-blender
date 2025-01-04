import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup, Tag
from textstat import textstat


def is_chapter(tag):
    tag_classes = tag.get('class', [])
    assert isinstance(tag_classes, list)
    return 'chapter' in tag_classes


@dataclass
class HtmlSection:
    header: str
    level: int
    word_count: int = 0

    @classmethod
    def from_tag(cls, tag: Tag) -> 'HtmlSection':
        content = ' '.join(tag.text.split())
        if is_chapter(tag):
            level = 1
            content = content[:60]
        else:
            if not tag.name.startswith('h'):
                raise ValueError(f'Tag {tag.name} does not start with "h".')
            level = int(tag.name[1:])
        header_text = '#' * level + ' ' + content
        return HtmlSection(header_text, level)

    def display(self) -> str:
        if 1000 <= self.word_count < 3000:
            label = 'WORDS^'
        elif 3000 <= self.word_count < 6000:
            label = 'WORDS!'
        else:
            label = 'words'
        return f'{self.header} - {self.word_count} {label}'


def find_stats(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    level = 0

    sections: list[HtmlSection] = [HtmlSection('Total', 0)]
    section_stack: list[HtmlSection] = sections[:]
    for child in soup.descendants:
        if isinstance(child, Tag):
            if re.match(r'^h\d+$', child.name) or is_chapter(child):
                new_section = HtmlSection.from_tag(child)
                level = new_section.level
                sections.append(new_section)
                while len(section_stack) <= level:
                    section_stack.append(HtmlSection('Dummy', -1))
                section_stack[level] = new_section
        else:
            word_count = textstat.lexicon_count(child.text)
            for ancestor_level in range(level + 1):
                section_stack[ancestor_level].word_count += word_count

    stats = [section.display() for section in sections]
    return '\n'.join(stats) + '\n'


def fetch_page(url: str) -> str:
    cache_dir = Path(__file__).parent / 'dump'
    cache_dir.mkdir(exist_ok=True)
    cache_stem = re.sub(r'\W+', '-', url)
    hasher = hashlib.md5()
    hasher.update(url.encode('utf-8'))
    md5 = hasher.hexdigest()
    cache_path = cache_dir / f'{cache_stem}-{md5}.html'
    try:
        return cache_path.read_text()
    except FileNotFoundError:
        pass
    try:
        with urlopen(url) as response:
            html = response.read().decode('utf-8')
    except HTTPError as e:
        raise ValueError(f"Failed to fetch page {url}.") from e
    cache_path.write_text(html)
    return html


def find_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')

    link_urls = []
    link: Tag
    for link in soup.find_all('a'):
        href = link.get('href')
        if not isinstance(href, str):
            continue
        if not re.match(r'^/ebooks/\d+$', href):
            continue
        if link.find_all('span', 'icon_audiobook'):
            continue
        link_urls.append(href)
    return link_urls


def main():
    """ URLs that have been tried:
    https://www.gutenberg.org/ebooks/subject/1123?start_index=26
    detective and mystery stories, world's best, Owl's Ear and others
    https://www.gutenberg.org/ebooks/author/50039
    Thomas Furlong, police blotter style
    https://www.gutenberg.org/ebooks/author/183
    Mary Roberts Rinehart
    https://www.gutenberg.org/ebooks/author/5882
    W. F. Harvey (Modern Ghost Stories anthology)
    https://www.gutenberg.org/ebooks/author/2685
    Lord Dunsany
    """
    author_url = 'https://www.gutenberg.org/ebooks/author/5882'
    author_html = fetch_page(author_url)
    book_urls = find_links(author_html)
    for book_url in book_urls:
        images_url = book_url + '.html.images'
        book_html = fetch_page(urljoin(author_url, images_url))
        stats = find_stats(book_html)
        print(stats)
        print()


if __name__ in ('__main__', '__live_coding__'):
    main()
