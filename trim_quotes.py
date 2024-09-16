import csv
import re
from argparse import ArgumentParser, FileType
from collections import Counter

""" Trim usable quotes from a large source file.

This expects a source of quotes like the one at
https://archive.org/details/quotes_20230625

It grabs the first 100 quotes at each letter count from 10 to 50.
"""


def parse_args():
    parser = ArgumentParser(description='Trim quotes from big CSV file.')
    parser.add_argument('csv_in',
                        type=FileType())
    parser.add_argument('csv_out',
                        type=FileType('w'))
    return parser.parse_args()


def main():
    args = parse_args()
    reader = csv.DictReader(args.csv_in)
    writer = csv.DictWriter(args.csv_out, fieldnames=reader.fieldnames)
    writer.writeheader()
    length_counts = Counter()
    category_counts = Counter()
    author_counts = Counter()
    for i, row in enumerate(reader):
        if __name__ == '__live_coding__' and i > 10:
            break
        quote = row['quote']
        letters = re.sub('[^A-Z]', '', quote.upper())
        letter_count = len(letters)
        if letter_count < 10 or 50 < letter_count:
            continue
        if length_counts[letter_count] >= 100:
            continue
        author = row['author']
        if 'Lailah Gifty Akita' in author:
            continue
        if 'Sunday Adelaja' in author:
            continue
        writer.writerow(row)
        length_counts[letter_count] += 1
        author_counts[author] += 1
        categories = re.split(r'\s*,\s*', row['category'])
        for category in categories:
            category_counts[category] += 1

    for length, count in sorted(length_counts.items()):
        print(f'{length}: {count}')
    for category, count in category_counts.most_common(100):
        print(f'{category}: {count}')
    for author, count in author_counts.most_common(100):
        print(f'{author}: {count}')


if __name__ in ('__main__', '__live_coding__'):
    main()
