
from arrow import utcnow, get as get_ts
import logging
import time
from ipaddress import ip_network

from sqlalchemy import desc, or_
from sqlalchemy.orm import lazyload

from cif.store.sqlite.constants import BASE
from cif.store.sqlite.models.indicator import Indicator, Ipv4, Ipv6, Fqdn, \
    Url, Tag, Hash
from cif.store.sqlite.utils import to_dict, normalize_data
from .filters import filter_indicator, filter_terms

from .constants import HASH_TYPES


logger = logging.getLogger(__name__)


class IndicatorManager(object):

    def __init__(self, handle, engine, **kwargs):
        super(IndicatorManager, self).__init__(**kwargs)

        self.handle = handle
        BASE.metadata.create_all(engine)

    def create(self, data, s=None, **kwargs):
        if isinstance(data, dict):
            data = [data]

        if not s:
            s = self.handle()

        # clean up the data
        normalize_data(data)

        # keep track of what's been inserted
        # keep track of what we've inserted
        created = {}

        # try batch mode
        s1 = time.time()
        try:
            [self._create(s, d, created) for d in data]
            s.commit()

            if logger.getEffectiveLevel() == logging.DEBUG:
                s2 = time.time()
                m = round(len(data) / (s2 - s1), 2)
                logger.debug(f"took: {round(s2 - s1, 2)}s ({m}/s)")

            return len(data)

        except Exception as e:
            logger.error(e, exc_info=True)

            logger.debug('rolling back transaction..')
            logger.debug('Trying batch again in non-batch mode')
            s.rollback()

        # something went wrong, try single mode. get *most* of the data
        # let the app figure out what didn't insert properly
        n = 0

        for i in data:
            try:
                self._create(s, i, created)
                s.commit()
                n += 1

            except Exception as e:
                logger.error(e, exc_info=True)
                logger.debug(i)

        logger.debug(f"took: {time.time() - s1}s")
        return n

    def search(self, filters, limit=500, s=None):
        if isinstance(filters, list) and len(filters) > 1:
            yield from self._search_bulk(filters, limit)

        else:
            # enrichment causes this to happen...
            if isinstance(filters, list):
                filters = filters[0]

            s = self._search(filters)

            limit = filters.pop('limit', limit)
            rv = s.order_by(desc(Indicator.reported_at)).limit(limit).all()
            for i in rv:
                yield to_dict(i)

    def delete(self, data=None):
        if not isinstance(data, list):
            data = [data]

        ids = []
        for d in data:
            if d.get('id'):
                ids.append(Indicator.id == d['id'])
            else:
                ids.append(Indicator.id == i.id
                           for i in self._search(d))

        if len(ids) == 0:
            return 0

        s = self.handle().query(Indicator).filter(or_(*ids))
        rv = s.delete()
        self.handle().commit()

        return rv

    def _upsert(self, i, d):
        # if not newer
        if not get_ts(d.get('last_at')).datetime > get_ts(i.last_at).datetime:
            return

        if not i.count:
            i.count = 1

        else:
            i.count += 1

        i.last_at = get_ts(d['last_at']).datetime.replace(tzinfo=None)
        i.reported_at = d.get('reported_at', utcnow().datetime)
        i.reported_at = get_ts(i.reported_at).datetime.replace(tzinfo=None)

        if d.get('drop_index') and i.drop_index != d['drop_index']:
            i.drop_index = d['drop_index']

    def _search_bulk(self, filters, limit, s=None):
        s = self.handle().query(Indicator)

        s = s.filter(or_(Indicator.indicator == i['indicator']
                         for i in filters))

        groups = ['everyone']

        s = s.filter(or_(Indicator.group == g for g in groups))
        for i in s.limit(limit):
            yield to_dict(i)

    def _search(self, filters, s=None):
        myfilters = dict(filters.items())

        s = self.handle().query(Indicator)

        # if no tags are presented, users probably expect non special data
        # in their results
        if not myfilters.get('tags') and not myfilters.get('indicator'):
            s = s.join(Tag)
            s = s.filter(Tag.tag != 'pdns')
            s = s.filter(Tag.tag != 'search')

        # these functions taint myfilters...
        s = filter_indicator(myfilters, s)
        s = filter_terms(myfilters, s)

        return s

    @staticmethod
    def _create_by_itype(s, i):
        if i.is_ip:
            addr = ip_network(i.indicator, False)
            if addr.version == 4:
                s.add(Ipv4(ip=str(addr.network_address), mask=addr.prefixlen,
                           indicator=i))
            else:
                s.add(Ipv6(ip=str(addr.network_address), mask=addr.prefixlen,
                           indicator=i))

        elif i.is_fqdn:
            s.add(Fqdn(fqdn=i.indicator, indicator=i))

        elif i.is_url:
            s.add(Url(url=i.indicator, indicator=i))

        elif i.is_hash:
            s.add(Hash(hash=i.indicator, indicator=i))

        return s

    @staticmethod
    def _create_build_filter(s, i):  # NOSONAR
        # setup query
        s = s.query(Indicator).options(lazyload('*')).filter_by(
            provider=i['provider'],
            itype=i['itype'],
            indicator=i['indicator'],
        ).order_by(Indicator.last_at.desc())

        if i.get('rdata', '') != '':
            s = s.filter_by(rdata=i['rdata'])

        if i['itype'] in ['ipv4', 'ipv6']:
            addr = ip_network(i['indicator'], False)
            if i['itype'] == 'ipv4':
                if addr.prefixlen == 32:
                    if i['indicator'].endswith('/32'):
                        i['indicator'], _ = i['indicator'].split('/')

                    s = s.join(Ipv4).filter(Ipv4.ip == i['indicator'])

                else:
                    s = s.join(Ipv4).filter(
                        Ipv4.ip == str(addr.network_address),
                        Ipv4.mask == addr.prefixlen)

            else:
                if addr.prefixlen == 128:
                    s = s.join(Ipv6).filter(Ipv6.ip == i['indicator'])

                else:
                    s = s.join(Ipv6).filter(
                        Ipv6.ip == str(addr.network_address),
                        Ipv6.mask == addr.prefixlen)
        elif i['itype'] == 'fqdn':
            s = s.join(Fqdn).filter(Fqdn.fqdn == i['indicator'])

        elif i['itype'] == 'url':
            s = s.join(Url).filter(Url.url == i['indicator'])

        elif i['itype'] in HASH_TYPES:
            s = s.join(Hash).filter(Hash.hash == i['indicator'])

        if len(i['tags']):
            s = s.join(Tag).filter(Tag.tag == i['tags'][0])

        return s

    def _create(self, s, d, created):
        # check duplicate
        if created.get(d['indicator']) and \
                d.get('last_at') in created[d['indicator']]:
            return

        rv = self._create_build_filter(s, d)

        # get first indicator
        if rv.first():
            return self._upsert(rv.first(), d)

        i = Indicator(**d)
        s.add(i)

        # create tags
        [s.add(Tag(tag=t, indicator=i)) for t in d.pop('tags', [])]

        self._create_by_itype(s, i)

        created[d['indicator']] = set()
        created[d['indicator']].add(d['last_at'])


