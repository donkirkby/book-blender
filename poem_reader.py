import re
from collections import defaultdict
from pathlib import Path
from random import sample


def load_solutions_by_length() -> dict[int, list[str]]:
    source_path = Path(__file__).with_name('poems.txt')
    source_text = source_path.read_text()
    sections = re.split(r'^\s*\d+\..*$', source_text, flags=re.MULTILINE)
    solutions_by_length: dict[int, list[str]] = defaultdict(list)
    sections.pop(0)
    for section in sections:
        section_lines = section.strip().splitlines()
        if not section_lines:
            continue
        first_line: str = section_lines[0]
        letters = re.sub('[^A-Z]', '', first_line.upper())
        solutions = solutions_by_length[len(letters)]
        solutions.append(letters)
    return solutions_by_length


def find_solution_by_length(length: int) -> str:
    solutions_by_length = load_solutions_by_length()

    valid_solutions = solutions_by_length[length]
    if not valid_solutions:
        raise ValueError(f'No solutions found for length {length}.')
    solution = sample(valid_solutions, 1)[0]
    return solution


def main():
    solutions_by_length = load_solutions_by_length()
    for length, solutions in sorted(solutions_by_length.items()):
        print(f'{length}: {len(solutions)}')


if __name__ in ('__main__', '__live_coding__'):
    main()
