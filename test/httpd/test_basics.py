import json
import os
import tempfile

import pytest
from cif.http.app import app
from cif.store import Store

ROUTER_ADDR = 'ipc://{}'.format(tempfile.NamedTemporaryFile().name)


@pytest.fixture
def client(request):
    app.config['TESTING'] = True
    app.config['CIF_ROUTER_ADDR'] = ROUTER_ADDR
    app.config['dummy'] = True
    return app.test_client()


@pytest.yield_fixture
def store():
    dbfile = tempfile.mktemp()
    with Store(store_type='sqlite', dbfile=dbfile) as s:
        yield s

    os.unlink(dbfile)


def test_httpd_search(client):
    rv = client.get('/indicators?q=example.com')
    assert rv.status_code == 200

    data = rv.data

    rv = json.loads(data.decode('utf-8'))
    assert rv[0]['indicator'] == 'example.com'
