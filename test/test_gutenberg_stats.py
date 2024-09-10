from textwrap import dedent

from gutenberg_stats import find_stats, find_links


def test_h1():
    html = """\
        <h1>Foo</h1>
        <p>Lorem ipsum dolores sit amet.</p>
        <p>Lazy dogs and quick foxes.</p>
        <h1>Bar</h1>
        <p>It was a dark and stormy night.</p>
    """

    expected_report = dedent("""\
        Total - 19 words
        # Foo - 11 words
        # Bar - 8 words
    """)

    report = find_stats(html)

    assert report == expected_report


def test_h1_h2():
    html = """\
        <h1>Foo</h1>
        <p>Lorem ipsum dolores sit amet.</p>
        <p>Lazy dogs and quick foxes.</p>
        <h2>Bar</h2>
        <p>It was a dark and stormy night.</p>
    """

    expected_report = dedent("""\
        Total - 19 words
        # Foo - 19 words
        ## Bar - 8 words
    """)

    report = find_stats(html)

    assert report == expected_report


def test_h1_h2_h1():
    html = """\
        <h1>Foo</h1>
        <p>Lorem ipsum dolores sit amet.</p>
        <p>Lazy dogs and quick foxes.</p>
        <h2>Bar</h2>
        <p>It was a dark and stormy night.</p>
        <h1>Moby Dick</h1>
        <p>Call me Ishmael.</p>
    """

    expected_report = dedent("""\
        Total - 24 words
        # Foo - 19 words
        ## Bar - 8 words
        # Moby Dick - 5 words
    """)

    report = find_stats(html)

    assert report == expected_report


def test_html():
    html = """\
        <html>
        <body>
        <h1>Foo</h1>
        <p>Lorem ipsum dolores sit amet.</p>
        <p>Lazy dogs and quick foxes.</p>
        <h2>Bar</h2>
        <p>It was a dark and stormy night.</p>
        <h1>Moby Dick</h1>
        <p>Call me Ishmael.</p>
        </body>
        </html>
    """

    expected_report = dedent("""\
        Total - 24 words
        # Foo - 19 words
        ## Bar - 8 words
        # Moby Dick - 5 words
    """)

    report = find_stats(html)

    assert report == expected_report


def test_line_breaks():
    html = """\
        <h1>Foo
        and
        Friends</h1>
        <p>Lorem ipsum dolores sit amet.</p>
        <p>Lazy dogs and quick foxes.</p>
        <h1>Bar</h1>
        <p>It was a dark and stormy night.</p>
    """

    expected_report = dedent("""\
        Total - 21 words
        # Foo and Friends - 13 words
        # Bar - 8 words
    """)

    report = find_stats(html)

    assert report == expected_report


def test_find_links():
    html = """\
        <p>Lorem ipsum dolores sit <a href="/ebooks/1234">amet</a>.
        Lazy dogs often <a href="/ebooks/999">chase</a> rabbits.</p>
    """
    expected_links = ["/ebooks/1234", "/ebooks/999"]

    urls = find_links(html)

    assert urls == expected_links


def test_find_links_skip_non_books():
    html = """\
        <p>Lorem ipsum dolores sit <a href="/ebooks/1234">amet</a>.
        Lazy dogs often <a href="/other_stuff/999">chase</a> rabbits.</p>
    """
    expected_links = ["/ebooks/1234"]

    urls = find_links(html)

    assert urls == expected_links


def test_find_links_skip_audio_books():
    html = """\
        <p>Lorem ipsum dolores sit <a href="/ebooks/1234">amet
        <span class="icon foo"></span></a>.
        Lazy dogs often <a href="/ebooks/999">chase
        <span class="icon icon_audiobook"></span></a> rabbits.</p>
    """
    expected_links = ["/ebooks/1234"]

    urls = find_links(html)

    assert urls == expected_links
