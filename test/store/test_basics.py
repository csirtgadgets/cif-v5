
import logging
import os
import tempfile
from argparse import Namespace
import pytest
from cif.store import Store
from cifsdk.utils import setup_logging
from arrow import utcnow

args = Namespace(debug=True, verbose=None)
setup_logging(args)

logger = logging.getLogger(__name__)


@pytest.yield_fixture
def store():
    dbfile = tempfile.mktemp()
    with Store(store_type='sqlite', db_path='sqlite:///' + dbfile) as s:
        yield s

    if os.path.isfile(dbfile):
        os.unlink(dbfile)


@pytest.fixture
def indicator():
    return {
        'indicator': 'example.com',
        'tags': ['botnet'],
        'provider': 'csirtgadgets.com',
        'group': 'everyone',
        'last_at': utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'reported_at': utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'itype': 'fqdn',
        'count': 1,
        'confidence': 1
    }


def test_store(store):
    assert store is not None
