import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from random import sample


@dataclass
class Quote:
    quote: str
    author: str
    letters: str


def load_quotes_by_length() -> dict[int, list[Quote]]:
    source_path = Path(__file__).with_name('trimmed_quotes.csv')
    with source_path.open() as f:
        quotes_by_length: dict[int, list[Quote]] = defaultdict(list)
        reader = csv.DictReader(f)
        for row in reader:
            # noinspection PyTypeChecker
            quote = row['quote']
            letters = re.sub('[^A-Z]', '', quote.upper())
            solutions = quotes_by_length[len(letters)]
            author_text = row['author']
            author, *_ = author_text.split(',')
            solutions.append(Quote(quote, author, letters))
    return quotes_by_length


def find_quote_by_length(length: int) -> Quote:
    quotes_by_length = load_quotes_by_length()

    valid_quotes = quotes_by_length[length]
    if not valid_quotes:
        raise ValueError(f'No quotes found for length {length}.')
    solution = sample(valid_quotes, 1)[0]
    return solution


def main():
    solutions_by_length = load_quotes_by_length()
    for length, solutions in sorted(solutions_by_length.items()):
        print(f'{length}: {len(solutions)}')


if __name__ in ('__main__', '__live_coding__'):
    main()
