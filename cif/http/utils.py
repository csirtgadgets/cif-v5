import logging
import re

from cifsdk.constants import VALID_FILTERS

logger = logging.getLogger(__name__)

CONFIDENCE_DEFAULT = 3


def filters_cleanup(request):
    filters = {}
    for f in VALID_FILTERS:
        if request.args.get(f):
            filters[f] = request.args.get(f)

    if request.args.get('q'):
        filters['indicator'] = request.args.get('q')

    if not filters.get('confidence') \
            and not filters.get('no_feed', '0') == '1' \
            and not filters.get('indicator'):
        filters['confidence'] = CONFIDENCE_DEFAULT

    return filters


def is_human(headers):
    if re.search(r'json$', headers.get('Accept', '')):
        return False

    if headers.get('Accept') in ['*/*', 'text/plain', 'text/csv']:
        return True

    if re.match(r'(curl|wget|mozilla|edge|chrome|webkit)',
                headers.get('User-Agent').lower()):
        return True
