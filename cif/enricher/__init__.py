#!/usr/bin/env python3

import logging
import traceback
import zmq
import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from zmq.eventloop import ioloop, zmqstream

from cifsdk.utils import setup_logging, get_argument_parser
from cifsdk.zmq.msg import Msg
from cifsdk.zmq.socket import Context
from csirtg_indicator import Indicator
from cifsdk.utils import load_plugins, init_plugins
from cifsdk.actor import Actor
from cifsdk.actor.manager import Manager as EnrichmentManager

import csirtg_enrichment.plugins as enrichers
from cif.enricher.constants import ENRICHER_ADDR, ENRICHER_SINK_ADDR, TRACE, \
    SNDTIMEO, ZMQ_HWM, RCVTIMEO, PLUGINS_NAMESPACE, LOGLEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

if TRACE:
    logger.setLevel(logging.DEBUG)


class Enricher(Actor):
    def __init__(self, **kwargs):
        Actor.__init__(self, **kwargs)

        self.plugins_ext = init_plugins(PLUGINS_NAMESPACE)

        self.plugins = load_plugins(enrichers.__path__) + \
            [self.plugins_ext[p] for p in self.plugins_ext]

        self.push_s = None

    def _process_message(self, message):
        m = Msg().from_frame(message)

        logger.debug(f"handling: {len(m.data)}")

        try:
            m.data = [Indicator(**i) for i in m.data]

        except Exception as e:
            logger.error(e)
            logger.debug(traceback.print_exc())

        try:
            [p.process(m.data) for p in self.plugins]

        except (KeyboardInterrupt, SystemExit):
            return

        except Exception as e:
            logger.error(e)
            logger.debug(traceback.print_exc())

        try:
            m.data = [i.__dict__() for i in m.data]

        except Exception as e:
            logger.error(e)
            m.data = []

        self.push_s.send_msg(m)

        logger.debug('done...')

    def start(self):
        pull_s = Context().socket(zmq.PULL)
        pull_s.setsockopt(zmq.LINGER, 3)
        pull_s.SNDTIMEO = SNDTIMEO
        pull_s.RCVTIMEO = RCVTIMEO

        self.push_s = Context().socket(zmq.PUSH)
        self.push_s.setsockopt(zmq.LINGER, 3)
        self.push_s.SNDTIMEO = SNDTIMEO
        self.push_s.RCVTIMEO = RCVTIMEO

        logger.info('connecting...')
        pull_s.connect(ENRICHER_ADDR)
        self.push_s.connect(ENRICHER_SINK_ADDR)

        logger.info('connected')

        loop = ioloop.IOLoop()

        s = zmqstream.ZMQStream(pull_s, loop)

        s.on_recv(self._process_message)
        s.connect(ENRICHER_ADDR)

        try:
            loop.start()

        except KeyboardInterrupt:
            loop.stop()

        for ss in [s, pull_s, self.push_s]:
            ss.close()


def main():
    p = get_argument_parser()
    p = ArgumentParser(
        description=textwrap.dedent('''\
            Env Variables:

            example usage:
                $ cif-enricher -d
            '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='cif-enricher',
        parents=[p]
    )

    p.add_argument('-E', '--threads', help='Number of workers', default=1)

    args = p.parse_args()
    setup_logging(args)

    if args.verbose:
        logger.setLevel(logging.INFO)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info(f"loglevel: {logger.getEffectiveLevel()}")

    m = EnrichmentManager(threads=args.threads, target=Enricher)

    try:
        m.start()

    except KeyboardInterrupt:
        m.stop()


if __name__ == '__main__':
    main()
