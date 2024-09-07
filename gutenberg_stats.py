import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup, Tag, PageElement
from textstat import textstat


@dataclass
class HtmlSection:
    header: str
    level: int
    word_count: int = 0

    @classmethod
    def from_tag(cls, tag: Tag) -> 'HtmlSection':
        if not tag.name.startswith('h'):
            raise ValueError(f'Tag {tag.name} does not start with "h".')
        level = int(tag.name[1:])
        content = ' '.join(tag.text.split())
        header_text = '#' * level + ' ' + content
        return HtmlSection(header_text, level)

    def display(self) -> str:
        label = 'WORDS' if 500 <= self.word_count <= 1500 else 'words'
        return f'{self.header} - {self.word_count} {label}'


def find_stats(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    level = 0

    sections: list[HtmlSection] = [HtmlSection('Total', 0)]
    section_stack: list[HtmlSection] = sections[:]
    for child in soup.descendants:
        if isinstance(child, Tag):
            if re.match(r'^h\d+$', child.name):
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
    with urlopen(url) as response:
        html = response.read().decode('utf-8')
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
        link_urls.append(href)
    return link_urls


def main():
    author_url = 'https://www.gutenberg.org/ebooks/author/37'
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
