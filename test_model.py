import os
import tempfile

import pytest

from short_link import short_link


@pytest.fixture
def client():
    db_fd, short_link.app.config['DATABASE'] = tempfile.mkstemp()
    short_link.app.config['TESTING'] = True

    with short_link.app.test_client() as client:
        with short_link.app.app_context():
            short_link.init_db()
        yield client

    os.close(db_fd)
    os.unlink(short_link.app.config['DATABASE'])


def test_new_link(client):
    
    link = Link(long_url='http://ya.ru')
    assert link.long_url == 'http://ya.ru'