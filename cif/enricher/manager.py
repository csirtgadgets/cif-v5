import logging
import zmq

from cifsdk.actor.manager import Manager as _Manager
from cifsdk.actor import Actor as Enricher
from .constants import TRACE, ENRICHER_ADDR, ENRICHER_SINK_ADDR, \
    LOGLEVEL


logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

if TRACE:
    logger.setLevel(logging.DEBUG)


class Manager(_Manager):

    def __init__(self, context, threads=0):

        if threads > 0:
            _Manager.__init__(self, Enricher, threads)

        self.socket = context.socket(zmq.PUSH)
        self.socket.bind(ENRICHER_ADDR)
        self.socket.SNDTIMEO = 5000
        self.socket.RCVTIMEO = 5000
        self.socket.setsockopt(zmq.LINGER, 3)

        self.sink_s = context.socket(zmq.PULL)
        self.sink_s.bind(ENRICHER_SINK_ADDR)
