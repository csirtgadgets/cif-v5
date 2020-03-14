#!/usr/bin/env python3

import logging
import textwrap
import traceback
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from time import sleep
import zmq
from zmq import POLLIN as Z_POLLIN
import os
import time

from cifsdk.utils import setup_logging, setup_runtime_path
from cifsdk.constants import RUNTIME_PATH

from cifsdk.zmq.socket import Context as CTX
from cif.store.manager import Manager as StoreManager
from cif.router.message import Manager as MessageManager
from cif.enricher.manager import Manager as EnrichmentManager
from cif.hunter.manager import Manager as HuntManager

from cif.router.constants import ROUTER_ADDR, ZMQ_SNDTIMEO, ZMQ_RCVTIMEO, \
    FRONTEND_TIMEOUT, BACKEND_TIMEOUT, TRACE, ZMQ_HWM, LOG_LEVEL, ENRICHMENT, \
    HUNT

from cif.constants import VERSION

from cif.store.constants import STORE_DEFAULT, STORE_PLUGINS

logger = logging.getLogger(__name__)

logger.setLevel(LOG_LEVEL)
logging.getLogger('asyncio').setLevel(logging.ERROR)

if TRACE:
    logger.setLevel(logging.DEBUG)


class Router(object):

    def __init__(self, **kwargs):
        self.store = None
        self.message = None
        self.terminate = False

        self.context = CTX()
        self.frontend_s = self.context.socket(zmq.ROUTER)
        self.frontend_s.set_hwm(ZMQ_HWM)
        self.frontend_s.setsockopt(zmq.SNDTIMEO, ZMQ_SNDTIMEO)
        self.frontend_s.setsockopt(zmq.RCVTIMEO, ZMQ_RCVTIMEO)

        self.kwargs = kwargs

        self.enrichment = kwargs.get('enrichment', False)
        if self.enrichment:
            self.enrichment = EnrichmentManager(CTX())

        self.hunt = kwargs.get('hunt', False)
        if self.hunt:
            self.hunt = HuntManager(CTX())

        self.poller = zmq.Poller()
        self.poller_enrichers = zmq.Poller()
        self.poller_hunters = zmq.Poller()

    def _init_store(self, **kwargs):
        logger.info('launching store...')

        store_type = kwargs.get('store_type', STORE_DEFAULT)

        self.store = StoreManager(self.context)
        self.store.start(store_type=store_type)

        logger.info('Waiting for Store to initialize...')
        time.sleep(2)
        logger.info("Store Ready....")

    def _init_pollers(self):
        for s in [self.frontend_s, self.store.socket, self.store.s_write]:
            self.poller.register(s, Z_POLLIN)

        if self.enrichment:
            self.poller_enrichers.register(self.enrichment.sink_s, Z_POLLIN)

        if self.hunt:
            self.poller_hunters.register(self.hunt.sink, Z_POLLIN)

    def _poll_sockets(self):
        items = dict(self.poller.poll(FRONTEND_TIMEOUT))

        if items.get(self.frontend_s) == Z_POLLIN:
            self.message.handle(self.frontend_s)

        for s in [self.store.socket, self.store.s_write]:
            if items.get(s) == Z_POLLIN:
                m = s.recv_msg()
                self.frontend_s.send_msg(m)

        if self.enrichment:
            items = dict(self.poller_enrichers.poll(BACKEND_TIMEOUT))

            if items.get(self.enrichment.sink_s) == Z_POLLIN:
                self.message.handle_enricher(self.enrichment.sink_s)

        if self.hunt:
            items = dict(self.poller_hunters.poll(BACKEND_TIMEOUT))
            if items.get(self.hunt.sink) == Z_POLLIN:
                self.message.handle(self.hunt.sink)

    def start(self):
        logger.info('launching backend..')
        self._init_store(**self.kwargs)

        logger.info('launching frontend...')
        self.message = MessageManager(self)

        logger.info(f"listening on: {ROUTER_ADDR}")
        self.frontend_s.bind(ROUTER_ADDR)

        self._init_pollers()

        while not self.terminate:
            self._poll_sockets()

    def stop(self):
        self.terminate = True
        sleep(0.5)

        self.frontend_s.close()
        sleep(0.5)

        logger.info('shutting down store...')
        self.store.stop()
        sleep(0.5)


def main():
    p = ArgumentParser(
        description=textwrap.dedent('''\
        Env Variables:
            CIF_RUNTIME_PATH
            CIF_ROUTER_ADDR

        example usage:
            $ CIF_ROUTER_ADDR=0.0.0.0 cif-router -d
        '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='cif-router',
    )
    p.add_argument(
        "--runtime-path",
        help="specify the runtime path [default %(default)s]",
        default=RUNTIME_PATH
    )
    p.add_argument('-d', '--debug', dest='debug', action="store_true")
    p.add_argument('-v', '--verbose', action='store_true')

    p.add_argument('-V', '--version', action='version',
                   version=VERSION)

    p.add_argument('-E', '--enrichment', help='Enable Enrichment',
                   default=ENRICHMENT, action='store_true')

    p.add_argument('-H', '--hunt', help='Enable Hunting',
                   action='store_true', default=HUNT)

    p.add_argument("--store",
                   help=f"specify a store type {', '.join(STORE_PLUGINS)} "
                   f"[default: %(default)s]",
                   default=STORE_DEFAULT)

    p.add_argument('--logging-ignore',
                   help='set logging to WARNING for specific modules')

    args = p.parse_args()
    setup_logging(args)

    if args.verbose:
        logger.setLevel(logging.INFO)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info(f"loglevel: {logger.getEffectiveLevel()}")

    if args.logging_ignore:
        to_ignore = args.logging_ignore.split(',')

        for i in to_ignore:
            logging.getLogger(i).setLevel(logging.WARNING)

    setup_runtime_path(args.runtime_path)
    # setup_signals(__name__)

    # http://stackoverflow.com/a/789383/7205341
    pid = str(os.getpid())
    logger.debug("pid: %s" % pid)

    r = Router(store_type=args.store, enrichment=args.enrichment,
               hunt=args.hunt)

    try:
        logger.info('starting router..')
        r.start()

    except KeyboardInterrupt:
        # todo - signal to threads to shut down and wait for them to finish
        logger.info('shutting down via SIGINT...')

    except SystemExit:
        logger.info('shutting down via SystemExit...')

    except Exception as e:
        logger.critical(e)
        traceback.print_exc()

    logger.info('stopping..')
    r.stop()

    logger.info('Shutting down')


if __name__ == "__main__":
    main()
