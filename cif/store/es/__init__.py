import logging
import os
import traceback
from time import sleep

from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import ConnectionError

from .indicator import IndicatorManager

ES_NODES = os.getenv('CIF_ES_NODES', '127.0.0.1:9200')
TRACE = os.environ.get('CIF_ES_TRACE')
TRACE_HTTP = os.getenv('CIF_ES_HTTP_TRACE')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('elasticsearch').setLevel(logging.ERROR)

if TRACE:
    logger.setLevel(logging.DEBUG)

if TRACE_HTTP:
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('elasticsearch').setLevel(logging.DEBUG)


class ES(object):
    name = 'es'

    def __init__(self, **kwargs):
        self.indicators_prefix = kwargs.get('indicators_prefix', 'indicators')

        connections.create_connection(hosts=kwargs.get('nodes', ES_NODES))

        self._alive = False

        while not self._alive:
            if not self._health_check():
                logger.warn('ES cluster not accessible')
                logger.info('retrying connection in 30s')
                sleep(30)

            self._alive = True

        logger.info('ES connection successful')
        self.indicators = IndicatorManager()

    @staticmethod
    def _health_check():
        try:
            x = connections.get_connection().cluster.health()

        except ConnectionError as e:
            logger.warn('elasticsearch connection error')
            logger.error(e)
            return

        except Exception as e:
            logger.error(traceback.print_exc())
            return

        logger.info('ES cluster is: %s' % x['status'])
        return x

    def ping(self, token):
        s = self._health_check()

        if s is None or s['status'] == 'red':
            raise ConnectionError('ES Cluster Issue')


Plugin = ES
