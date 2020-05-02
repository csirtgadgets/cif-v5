import os


VALID_FILTERS = ['indicator', 'confidence', 'provider', 'itype', 'group',
                 'tags', 'rdata']

LIMIT = 2500
LIMIT = os.getenv('CIF_ES_LIMIT', LIMIT)

LIMIT_HARD = 500000
LIMIT_HARD = os.getenv('CIF_ES_LIMIT_HARD', LIMIT_HARD)

WINDOW_LIMIT = 250000
WINDOW_LIMIT = os.getenv('CIF_ES_WINDOW_LIMIT', WINDOW_LIMIT)

TIMEOUT = '120'
TIMEOUT = os.getenv('CIF_ES_TIMEOUT', TIMEOUT)
TIMEOUT = '{}s'.format(TIMEOUT)

PARTITION = os.getenv('CIF_STORE_ES_PARTITION', 'month')

SHARDS = os.getenv('CIF_ES_SHARDS', 1)
REPLICAS = os.getenv('CIF_ES_REPLICAS', 0)
