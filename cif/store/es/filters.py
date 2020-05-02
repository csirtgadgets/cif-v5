from csirtg_indicator.utils import resolve_itype
import socket
import binascii
from elasticsearch_dsl import Q
import ipaddress
import arrow

from cifsdk.constants import VALID_FILTERS


def _filter_ipv4(s, i):
    ip = ipaddress.IPv4Network(i)
    mask = ip.prefixlen
    if mask < 8:
        raise ValueError('prefix needs to be greater than or equal to 8')

    start = str(ip.network_address)
    end = str(ip.broadcast_address)

    s = s.filter('range', indicator_ipv4={'gte': start, 'lte': end})
    return s


def _filter_ipv6(s, i):
    ip = ipaddress.IPv6Network(i)
    mask = ip.prefixlen
    if mask < 32:
        raise ValueError('prefix needs to be greater than or equal to 32')

    start = binascii.b2a_hex(socket.inet_pton(
        socket.AF_INET6, str(ip.network_address))).decode('utf-8')

    end = binascii.b2a_hex(socket.inet_pton(
        socket.AF_INET6, str(ip.broadcast_address))).decode('utf-8')

    s = s.filter('range', indicator_ipv6={'gte': start, 'lte': end})
    return s


def filter_confidence(s, filter):
    if not filter.get('confidence'):
        return s

    c = filter.pop('confidence')

    low, high = c, 4.0
    if isinstance(c, str) and ',' in c:
        low, high = c.split(',')

    return s.filter('range',
                    confidence={'gte': float(low), 'lte': float(high)})


def filter_reported_at(s, filter):
    if not filter.get('reported_at'):
        return s

    c = filter.pop('reported_at')

    low, high = c, arrow.utcnow()
    if ',' in c:
        low, high = c.split(',')

    low = arrow.get(low).datetime
    high = arrow.get(high).datetime

    s = s.filter('range', reported_at={'gte': low, 'lte': high})
    return s


def filter_indicator(s, q_filters):
    if not q_filters.get('indicator'):
        return s

    i = q_filters.pop('indicator')

    try:
        itype = resolve_itype(i)

    except TypeError:
        if '%' in i:
            i = i.replace('%', '*')

        if '*' in i:
            return s.query("wildcard", indicator=i)

        s = s.query("match", message=i)
        return s

    if itype in ('email', 'url', 'fqdn', 'md5', 'sha1', 'sha256', 'sha512'):
        return s.filter('term', indicator=i)

    if itype is 'ipv4':
        return _filter_ipv4(s, i)

    if itype is 'ipv6':
        return _filter_ipv6(s, i)

    return s


def filter_terms(s, q_filters):
    for f in q_filters:
        if f in ['nolog', 'days', 'hours', 'group', 'limit', 'tags']:
            continue

        kwargs = {f: q_filters[f]}
        if isinstance(q_filters[f], list):
            s = s.filter('terms', **kwargs)
        else:
            s = s.filter('term', **kwargs)

    return s


def filter_tags(s, q_filters):
    tags = q_filters['tags']

    if isinstance(tags, str):
        tags = tags.split(',')

    tt = [Q('term', tags=t) for t in tags]

    s.query = Q('bool', must=s.query, should=tt, minimum_should_match=1)

    return s


def filter_group(s, q_filters):
    group = q_filters['group']

    if isinstance(group, str):
        group = [group]

    gg = []
    for g in group:
        gg.append(Q('term', group=g))

    s.query = Q('bool', must=s.query, should=gg, minimum_should_match=1)

    return s


def filter_build_bulk(s, filters):
    queries = []
    for f in filters:
        queries.append(Q("term", indicator=f['indicator']))

    q = Q("bool", should=queries)
    return s.query(q)


def filter_build(s, filters):
    q_filters = {}
    for f in VALID_FILTERS:
        if filters.get(f):
            q_filters[f] = filters[f]

    # treat indicator as special, transform into Search
    s = filter_indicator(s, q_filters)

    s = filter_confidence(s, q_filters)

    s = filter_reported_at(s, q_filters)

    # transform all other filters into term=
    s = filter_terms(s, q_filters)

    if filters.get('tags'):
        s = filter_tags(s, filters)

    if filters.get('group'):
        s = filter_group(s, filters)

    return s
