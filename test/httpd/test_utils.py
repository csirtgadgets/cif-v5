
from cif.http.feeds.utils import calc_reported_at_window, feed_factory


def test_http_feed_utils():
    for e in ['days', 'hours', 'today']:
        f = {e: '1'}
        calc_reported_at_window(f)
        assert f.get('reported_at')


def test_http_feed_factory():
    for i in ['ipv4', 'url', 'ipv6', 'sha1', 'fqdn', 'email']:
        r = feed_factory(i)
        assert r
