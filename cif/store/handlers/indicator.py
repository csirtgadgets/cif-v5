from base64 import b64decode
from arrow import utcnow
import logging
from csirtg_indicator.utils import resolve_itype
from time import time
from ..constants import REQUIRED_ATTRIBUTES, LIMIT

logger = logging.getLogger(__name__)


def _check_indicator(i):
    if not i.get('tags'):
        i['tags'] = 'suspicious'

    if not i.get('reported_at'):
        i['reported_at'] = utcnow().datetime

    for e in REQUIRED_ATTRIBUTES:
        if not i.get(e):
            raise ValueError('missing %s' % e)

    return True


def _cleanup_indicator(i):
    if not i.get('message'):
        return

    try:
        i['message'] = b64decode(i['message'])

    except Exception as e:
        pass


class IndicatorHandler(object):

    def __init__(self, store):
        self.store = store

    def _log_search(self, i):
        if i.get('nolog', '0') == '1':
            return

        if i.get('indicator', '') == '':
            return

        for e in ['limit', 'nofeed', 'nolog']:
            if i.get(e):
                del i[e]

        for e in ['first_at', 'last_at', 'reported_at']:
            if not i.get(e):
                i[e] = str(utcnow())

        i['provider'] = 'local'
        i['itype'] = resolve_itype(i['indicator'])
        i['tags'] = 'search'
        i['confidence'] = 4
        i['tlp'] = 'amber'
        i['group'] = 'everyone'
        i['count'] = 1
        i['description'] = 'search'

        self.store.indicators.create(i)

    def indicators_create(self, m):
        data = m.data

        if isinstance(data, dict):
            data = [data]

        for i in data:
            _check_indicator(i)
            _cleanup_indicator(i)

        return self.store.indicators.create(data)

    def indicators_search(self, m):
        s1 = time()
        to_log = []

        try:
            for e in m.data:
                if e.get('limit') is None:
                    e['limit'] = LIMIT

                if e.get('indicator') and not e.get('itype'):
                    e['itype'] = resolve_itype(e['indicator'])

                if e.get('nolog', 0) == 1:
                    continue

                if e.get('indicator'):
                    to_log.append(e)

            yield from self.store.indicators.search(m.data)

            for ee in to_log:
                self._log_search(ee)

        except StopIteration as e:
            yield

        except Exception as e:
            logger.error(e)

            if logger.getEffectiveLevel() == logging.DEBUG:
                import traceback
                traceback.print_exc()

            raise TypeError('invalid search')

        s2 = time()
        logger.debug(f"took: {round(s2 - s1, 2)}s")
