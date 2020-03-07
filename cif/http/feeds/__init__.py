import arrow
import zmq
import logging
import copy

from cifsdk.client.zeromq import ZMQ as Client

from .constants import FEEDS_LIMIT, FEEDS_WHITELIST_LIMIT, \
    HTTPD_FEED_WHITELIST_CONFIDENCE, FEEDS_WHITELIST_DAYS, FEED_DAYS, \
    FEED_PLUGINS, FEEDS_DAYS, DAYS_SHORT

from csirtg_indicator.feed import aggregate
from .utils import calc_reported_at_window, feed_factory

from pprint import pprint
logger = logging.getLogger(__name__)


def _get(filters):
    try:
        with Client() as client:
            r = client.indicators_search(filters)

    except zmq.error.Again as e:
        raise ConnectionError

    return r


def get_feed(filters):
    # single search
    if filters.get('indicator') or filters.get('no_feed', '0') == '1':
        return _get(filters)

    # feed
    if not filters.get('reported_at') and not filters.get('days') \
            and not filters.get('hours'):
        if not filters.get('itype'):
            filters['days'] = str(DAYS_SHORT)
        else:
            filters['days'] = str(FEED_DAYS[filters['itype']])

    if not filters.get('reported_at'):
        calc_reported_at_window(filters)

    if not filters.get('limit'):
        filters['limit'] = FEEDS_LIMIT

    tags = set(filters.get('tags', []))
    if 'whitelist' in tags:
        return _get(filters)

    if not filters.get('itype'):
        raise SyntaxError('itype required')

    f = feed_factory(filters['itype'])

    myfeed = list(f(
        _get(filters),
        _get_whitelist(filters)
    ))

    return aggregate(myfeed)


def _get_whitelist(filters={}):
    wl_filters = copy.deepcopy(filters)

    # whitelists are typically updated 1/month so we should catch those
    # esp for IP addresses
    wl_filters['tags'] = 'whitelist'
    wl_filters['confidence'] = HTTPD_FEED_WHITELIST_CONFIDENCE

    wl_filters['nolog'] = '1'
    wl_filters['limit'] = FEEDS_WHITELIST_LIMIT

    now = arrow.utcnow().shift(days=-FEEDS_WHITELIST_DAYS)
    wl_filters['reported_at'] = '%s' % f"{now.format('YYYY-MM-DDTHH:mm:ss')}"

    return aggregate(_get(wl_filters))
