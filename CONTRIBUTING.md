To add a story, find a good, short story that's public domain.
[Project Gutenberg] is a good place to look, and you can count words in an
author's books and chapters with the `gutenberg_stats.py` script. When you find
a story, add a link definition to
`docs/sources.md`, but don't actually add the link anywhere in the page. Once
you've playtested the puzzle, you'll come back and add the link.

Now copy the text of the story, but try not to read much of it. Create a new
markdown file in `docs/solutions` named after the story. Paste the text in, and
clean up the title and any headings. The title and author can be put in the
front matter, see other files for examples.

Run `publish.py`, and print out the PDF version of the new story. Try to solve
it.

Once you've finished solving it, decide if it's fun enough to publish. If not,
delete the solution, the PDF, and the source.

If it's enough fun to publish, clean up any errors by editing the solution and
regenerating the PDF. Then add the story in these places:
1. `README.md`
2. `docs/index.md` - Compare it to `README.md`.
3. `_posts/YYYY-MM-DD-title.md` - Copy description from `README.md`.
4. `docs/solutions/index.md`
5. `docs/sources.md`
6. `docs/_data/navigation.yml`
7. Mastodon - use the #WordGame and #puzzle hashtags, as well as an author
   hashtag, plus the description from `README.md`.

[Project Gutenberg]: https://gutenberg.org
