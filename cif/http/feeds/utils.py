import arrow
import re
from .constants import FEED_PLUGINS


def feed_factory(name):
    return FEED_PLUGINS.get(name, None)


def calc_reported_at_window(filters):
    now = arrow.utcnow()
    end = f"{now.format('YYYY-MM-DDTHH:mm:ss')}"
    start = f"{now.format('YYYY-MM-DDTHH:mm:ss')}"

    if filters.get('days'):
        if re.match(r'^\d+$', filters['days']):
            now = now.shift(days=-int(filters['days']))
            start = f"{now.format('YYYY-MM-DDTHH:mm:ss')}"
        del filters['days']

    if filters.get('hours'):
        if re.match(r'^\d+$', filters['hours']):
            now = now.shift(hours=-int(filters['hours']))
            start = f"{now.format('YYYY-MM-DDTHH:mm:ss')}"
        del filters['hours']

    if filters.get('today'):
        if filters['today'] == '1':
            start = f"{now.format('YYYY-MM-DDTHH:mm:ss')}"
            end = f"{now.format('YYYY-MM-DDT23:59:59')}"
        del filters['today']

    filters['reported_at'] = '%s,%s' % (start, end)
