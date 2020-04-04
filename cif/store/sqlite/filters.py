
import logging
from arrow import get as get_ts
from csirtg_indicator.utils import resolve_itype
from cifsdk.constants import VALID_FILTERS

import ipaddress
from sqlalchemy import or_, and_
from cif.store.sqlite.models.indicator import Indicator, Ipv4, Ipv6, Fqdn, \
    Url, Email, Tag, Hash

from .constants import HASH_TYPES
logger = logging.getLogger(__name__)


def filter_indicator(filters, s):

    for k, v in list(filters.items()):
        if k not in VALID_FILTERS:
            del filters[k]

    if not filters.get('indicator'):
        return s

    i = filters.pop('indicator')

    itype = resolve_itype(i)

    if itype == 'email':
        s = s.join(Email).filter(or_(
            Email.email.like('%.{}'.format(i)),
            Email.email == i)
        )
        return s

    if itype == 'ipv4':
        ip = ipaddress.IPv4Network(i)
        mask = ip.prefixlen

        if mask < 8:
            raise TypeError('prefix needs to be >= 8')

        start = str(ip.network_address)
        end = str(ip.broadcast_address)

        logger.debug('{} - {}'.format(start, end))

        s = s.join(Ipv4).filter(Ipv4.ip >= start)
        s = s.filter(Ipv4.ip <= end)

        return s

    if itype == 'ipv6':
        ip = ipaddress.IPv6Network(i)
        mask = ip.prefixlen

        if mask < 32:
            raise TypeError('prefix needs to be >= 32')

        start = str(ip.network_address)
        end = str(ip.broadcast_address)

        logger.debug('{} - {}'.format(start, end))

        s = s.join(Ipv6).filter(Ipv6.ip >= start)
        s = s.filter(Ipv6.ip <= end)
        return s

    if itype == 'fqdn':
        s = s.join(Fqdn).filter(or_(
            Fqdn.fqdn.like('%.{}'.format(i)),
            Fqdn.fqdn == i)
        )
        return s

    if itype == 'url':
        s = s.join(Url).filter(Url.url == i)
        return s

    if itype in HASH_TYPES:
        s = s.join(Hash).filter(Hash.hash == str(i))
        return s

    raise ValueError


def filter_terms(filters, s):  # NOSONAR

    idx = ['reported_at', 'itype', 'confidence', 'tags', 'provider', 'asn', 'cc',
           'asn_desc', 'rdata', 'region', 'uuid',  'drop_index']

    for k in idx:
        if not filters.get(k):
            continue

        v = filters[k]

        if k == 'reported_at':
            if ',' in v:
                start, end = v.split(',')
                s = s.filter(
                    and_(Indicator.reported_at >= get_ts(start).datetime,
                         Indicator.reported_at <= get_ts(end).datetime))
            else:
                s = s.filter(Indicator.reported_at >= get_ts(v).datetime)

        elif k == 'confidence':
            if ',' in str(v):
                start, end = str(v).split(',')
                s = s.filter(Indicator.confidence >= float(start))
                s = s.filter(Indicator.confidence <= float(end))
            else:
                s = s.filter(Indicator.confidence >= float(v))

        elif k == 'itype':
            s = s.filter(Indicator.itype == v)

        elif k == 'provider':
            s = s.filter(Indicator.provider == v)

        elif k == 'asn':
            s = s.filter(Indicator.asn == v)

        elif k == 'asn_desc':
            s = s.filter(Indicator.asn_desc.like('%{}%'.format(v)))

        elif k == 'cc':
            s = s.filter(Indicator.cc == v)

        elif k == 'rdata':
            s = s.filter(Indicator.rdata == v)

        elif k == 'region':
            s = s.filter(Indicator.region == v)

        elif k == 'related':
            s = s.filter(Indicator.related == v)

        elif k == 'uuid':
            s = s.filter(Indicator.uuid == v)

        elif k == 'oid':
            s = s.filter(Indicator.oid == v)

        elif k == 'iid':
            s = s.filter(Indicator.iid == v)

        elif k == 'tags':
            t = v
            if isinstance(v, str):
                t = v.split(',')
            s = s.join(Tag)
            s = s.filter(or_(Tag.tag == tt for tt in t))

        elif k == 'drop_index':
            if ',' in str(v):
                start, end = str(v).split(',')
                start, end = float(start), float(end)

                if end > 1.0:
                    start = start / 100.0
                    end = end / 100.0

                if start == 0.0:
                    s = s.filter(or_(Indicator.drop_index == None,
                                     Indicator.drop_index <= end))
                else:
                    s = s.filter(Indicator.drop_index >= start)
                    s = s.filter(Indicator.drop_index <= end)

            else:
                v = float(v)
                if v == 0:
                    continue

                if v > 1.0:
                    v = v / 100.0
                s = s.filter(Indicator.drop_index >= v)

        else:
            raise TypeError('invalid filter: %s' % k)

    return s


def filter_groups(filters, s):
    groups = filters.get('groups', ['everyone'])

    if isinstance(groups, str):
        groups = [groups]

    s = s.filter(or_(Indicator.group == g for g in groups))
    return s
