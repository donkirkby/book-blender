from pathlib import Path

import pytest
from space_tracer import LiveImageDiffer


@pytest.fixture(scope='session')
def session_image_differ():
    """ Track all images compared in a session. """
    diffs_path = Path(__file__).parent / 'image_diffs'
    differ = LiveImageDiffer(diffs_path)
    yield differ
    differ.remove_common_prefix()


@pytest.fixture
def image_differ(request, session_image_differ):
    """ Pass the current request to the session image differ. """
    session_image_differ.request = request
    yield session_image_differ
