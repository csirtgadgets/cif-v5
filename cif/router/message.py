import logging
import traceback
from zmq.error import Again

logger = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, router):
        self.router = router
        self.hunt = router.hunt
        self.store = router.store
        self.enrichment = router.enrichment

    def handle(self, s):

        try:
            m = s.recv_msg()

        except Exception as e:
            logger.error(e, exc_info=True)
            return

        handler = self.handle_default
        if m.mtype in ['indicators_create']:
            handler = getattr(self, "handle_" + m.mtype)

        logger.debug(f"handling message: {m.mtype}")

        try:
            handler(m)

        except Exception as e:
            logger.error(e, exc_info=True)
            logger.debug(traceback.print_exc())

    def handle_default(self, m):
        self.store.socket.send_msg(m)

    def _send_upstream(self, m):
        try:
            self.store.s_write.send_msg(m)

        except Again as e:
            logger.debug(e, exc_info=True)
            logger.error('timeout sending to store...')
            return

        if self.hunt:
            try:
                self.hunt.socket.send_msg(m)

            except Again:
                logger.error('timeout sending to hunters...')

    def handle_indicators_create(self, m):
        logger.debug(f"messages: {len(m.data)}")
        if not self.enrichment:
            return self._send_upstream(m)

        self.enrichment.socket.send_msg(m)

    def handle_enricher(self, s):
        return self._send_upstream(s.recv_msg())
