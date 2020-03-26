import logging
from argparse import Namespace
from cifsdk.utils import setup_logging
import arrow
from cifsdk.zmq.msg import Msg

from test.store.test_basics import store, indicator


args = Namespace(debug=True, verbose=None)
setup_logging(args)

logger = logging.getLogger(__name__)


def test_indicators_create(store, indicator):

    m = Msg()
    m.data = indicator

    x = store.indicators.indicators_create(m)

    # TODO- fix this based on store handle
    assert x == 1

    indicator['last_at'] = arrow.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    indicator['tags'] = ['malware']
    m.data = indicator
    x = store.indicators.indicators_create(m)

    assert x == 1


def test_indicators_search_fqdn(store, indicator):
    m = Msg()
    m.data = [{
        'indicator': 'example.com',
    }]
    x = store.indicators.indicators_search(m)

    assert len(list(x)) == 0

    x = store.indicators.indicators_search(m)

    assert len(list(x)) == 1

    indicator['tags'] = 'botnet'
    indicator['indicator'] = 'example2.com'

    m.data = indicator

    x = store.indicators.indicators_create(m)

    assert x == 1

    m.data = [{
        'indicator': 'example2.com',
    }]
    x = store.indicators.indicators_search(m)

    assert len(list(x)) == 1

    x = store.indicators.indicators_search(m)

    assert len(list(x)) > 0

    m.data = [{
        'indicator': 'example2.com',
        'tags': 'malware'
    }]
    x = store.indicators.indicators_search(m)

    assert len(list(x)) == 0


def test_indicators_search_ipv4(store, indicator):
    indicator['indicator'] = '192.168.1.1'
    indicator['itype'] = 'ipv4'
    indicator['tags'] = 'botnet'

    m = Msg()
    m.data = indicator

    x = store.indicators.indicators_create(m)

    assert x == 1

    for i in ['192.168.1.1', '192.168.1.0/24']:
        m.data = [{
            'indicator': i,
        }]
        x = store.indicators.indicators_search(m)

        assert len(list(x)) > 0


def test_indicators_search_ipv6(store, indicator):
    indicator['indicator'] = '2001:4860:4860::8888'
    indicator['itype'] = 'ipv6'
    indicator['tags'] = 'botnet'

    m = Msg(data=indicator)
    x = store.indicators.indicators_create(m)

    assert x == 1

    m.data = [{
        'indicator': '2001:4860:4860::8888',
    }]
    x = store.indicators.indicators_search(m)

    assert len(list(x)) > 0

    m.data = [{
        'indicator': '2001:4860::/32',
    }]
    x = store.indicators.indicators_search(m)

    assert len(list(x)) > 0


def test_indicators_search_bulk(store, indicator):
    m = Msg(data=indicator)

    x = store.indicators.indicators_create(m)

    assert x == 1

    m.data = [
        {
            'indicator': 'example.com',
            'tags': 'botnet',
            'confidence': 1
        },
        {
            'indicator': 'example2.com',
        }
    ]

    x = list(store.indicators.indicators_search(m))
    assert len(x) == 1

    assert x[0]['indicator'] == 'example.com'


# def test_indicators_delete(store, indicator):
#     m = Msg()
#     m.data = [indicator]
#
#     x = store.indicators.indicators_create(m)
#
#     m.data = {
#         'indicator': 'example.com',
#     }
#     r = store.indicators.indicators_delete(m)
#     assert r == 1
#
#     m.data = [{
#         'indicator': 'example.com',
#         'nolog': 1
#     }]
#     x = store.indicators.indicators_search(m)
#     assert len(x) == 0
#
#     m.data = [{
#         'indicator': 'example2.com',
#         'nolog': 1
#     }]
#     x = store.indicators.indicators_search(m)
#
#     for xx in x:
#         m.data = [{
#             'id': xx['id']
#         }]
#         r = store.indicators.indicators_delete(m)
#         assert r == 1


def test_indicators_create_sha1(store, indicator):
    indicator['indicator'] = 'd52380918a07322c50f1bfa2b43af3bb54cb33db'
    indicator['group'] = 'everyone'
    indicator['itype'] = 'sha1'

    m = Msg(data=[indicator])
    x = store.indicators.indicators_create(m)
    # TODO indicators_hash table isn't showing up..

    # assert x == -1
    #
    # x = store.indicators_search(t, {
    #     'indicator': indicator['indicator'],
    #     'nolog': 1
    # })
    # assert len(x) == 1
