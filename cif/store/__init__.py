#!/usr/bin/env python3

import logging
import textwrap
import ujson as json
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import zmq
import traceback

from cifsdk.zmq.socket import Context

from cifsdk.utils import setup_logging, setup_signals, get_argument_parser, \
    init_plugins

from cifsdk.actor import MyProcess
from .handlers.indicator import IndicatorHandler

from .constants import STORE_DEFAULT, TRACE, STORE_PLUGINS, LOGLEVEL

from cif.store.constants import STORE_ADDR, STORE_WRITE_ADDR

logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

if TRACE == '1':
    logger.setLevel(logging.DEBUG)

for m in ['boto', 'boto3', 'urllib3', 'botocore']:
    logging.getLogger(m).setLevel(logging.ERROR)


class Store(MyProcess):

    def __init__(self, store_address=STORE_ADDR, **kwargs):
        MyProcess.__init__(self)

        self.context = Context()
        self.store_addr = store_address
        self.router = None
        self.router_write = None

        self.store = self._init_plugin(**kwargs)
        self.indicators = IndicatorHandler(self.store)

        self.handlers = {
            'indicators': self.indicators
        }

    @staticmethod
    def _init_plugin(**kwargs):
        if kwargs.get('store_type') == 'sqlite':
            from .sqlite import SQLite
            return SQLite(**kwargs)

        elif kwargs.get('store_type') == 'es':
            from .es import ES
            return ES(**kwargs)

        try:
            p = init_plugins(kwargs.get('store_type'))
            p = p[kwargs['store_type']].Plugin

        except ImportError as e:
            logger.error(e, exc_info=True)
            logger.fatal(f"{kwargs.get('store_type')} store plugin Not Found")
            raise SystemExit

        return p(**kwargs)

    def _get_handler(self, m):
        for h in self.handlers:
            if m.mtype.startswith(h):
                return getattr(self.handlers[h], m.mtype)

    @staticmethod
    def _trigger_handler(handler, m):
        rv, err = False, False

        try:
            rv = handler(m)
            rv = {"status": "success", "data": rv}
        except PermissionError as e:
            logger.error(e)
            err = 'unauthorized'

        except TypeError as e:
            logger.error(e, exc_info=True)
            err = 'invalid search'

        except ValueError as e:
            logger.error(e, exc_info=True)
            logger.debug(m.data)
            err = f"invalid indicator: {e}"

        except Exception as e:
            if logger.getEffectiveLevel() == logging.DEBUG:
                logger.debug(traceback.print_exc())
            else:
                logger.error(e)
            err = 'unknown failure'

        if err:
            rv = {'status': 'failed', 'message': err}

        try:
            m.data = json.dumps(rv)

        except Exception as e:
            if logger.getEffectiveLevel() == logging.DEBUG:
                logger.debug(traceback.print_exc())
            else:
                logger.error(e, exc_info=True)

            m.data = json.dumps({'status': 'failed', 'message':
                                 'feed too large, retry the query'})

        return m

    def handle_message(self, m):
        handler = self._get_handler(m)

        if not handler:
            logger.error('message type {0} unknown'.format(m.mtype))
            m.data = '0'
            return self.router.send_msg(m)

        m = self._trigger_handler(handler, m)

        if m.mtype == 'indicators_create':
            self.router_write.send_msg(m)

        else:
            self.router.reply(m)

    def _check_s(self, p, sock):
        s = dict(p.poll(5))
        if sock in s:
            return self.handle_message(sock.recv_msg())

    def _loop(self):
        poller = zmq.Poller()
        poller.register(self.router, zmq.POLLIN)

        poller_write = zmq.Poller()
        poller_write.register(self.router_write, zmq.POLLIN)

        pollers = {
            poller: self.router,
            poller_write: self.router_write,
        }

        while not self.exit.is_set():

            try:
                for p in pollers:
                    self._check_s(p, pollers[p])

            except KeyboardInterrupt:
                break

            except Exception as e:
                if logger.getEffectiveLevel() == logging.DEBUG:
                    logger.debug(traceback.print_exc())
                logger.error(e, exc_info=True)

    def _pipeline_start(self):
        for s in ['router', 'router_write']:
            setattr(self, s, self.context.socket(zmq.ROUTER))

        self.router.connect(self.store_addr)
        self.router_write.connect(STORE_WRITE_ADDR)

    def _pipeline_stop(self):
        for s in ['router', 'router_write']:
            getattr(self, s).close()

    def start(self):
        self._pipeline_start()
        self._loop()
        self._pipeline_stop()


def main():
    p = get_argument_parser()
    p = ArgumentParser(
        description=textwrap.dedent('''\
         Env Variables:
            CIF_RUNTIME_PATH

        example usage:
            $ cif-store -d
        '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='cif-store',
        parents=[p]
    )

    p.add_argument("--store", help="store type {} [default: %(default)s]".
                   format(', '.join(STORE_PLUGINS)),
                   default=STORE_DEFAULT)

    p.add_argument('--remote', help='specify remote')

    args = p.parse_args()

    setup_logging(args)

    setup_signals(__name__)


if __name__ == "__main__":
    main()
