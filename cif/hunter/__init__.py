#!/usr/bin/env python3

import logging
import traceback
import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import zmq
from zmq.eventloop import zmqstream
from tornado.ioloop import IOLoop

from cifsdk.utils import setup_logging, get_argument_parser
from cifsdk.client.zeromq import ZMQ as Client
from csirtg_indicator import Indicator
from cifsdk.utils import load_plugins, init_plugins
from cifsdk.zmq.msg import Msg
from cifsdk.zmq.socket import Context
from cifsdk.actor import Actor
from cifsdk.actor.manager import Manager

import csirtg_hunter.plugins as hunters

from cif.hunter.constants import HUNTER_ADDR, HUNTER_SINK_ADDR, TRACE, \
    ZMQ_HWM, EXCLUDE, CONFIG_PATH, MIN_CONFIDENCE, \
    LOGLEVEL

EXCLUSIONS = ["", 'localhost', 'example.com']

logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

if TRACE:
    logger.setLevel(logging.DEBUG)


class Hunter(Actor):
    plugins = load_plugins(hunters.__path__)

    def __init__(self):
        Actor.__init__(self)

        self.exclude = {}
        self.router = None

        self._init_exclude()
        self.plugins_ext = init_plugins('csirtg_hunters_')

        for p in self.plugins_ext:
            self.plugins.append(self.plugins_ext[p])

    def _init_exclude(self):
        if not EXCLUDE:
            return

        for e in EXCLUDE.split(','):
            provider, tag = e.split(':')

            if not self.exclude.get(provider):
                self.exclude[provider] = set()

            logger.debug('setting hunter to skip: {}/{}'.format(provider, tag))
            self.exclude[provider].add(tag)

    def _exclude(self, d):
        if d.indicator in EXCLUSIONS:
            return True

        if not self.exclude.get(d.provider):
            return

        for t in d.tags:
            if t in self.exclude[d.provider]:
                logger.debug('skipping: {}'.format(d.indicator))
                return True

    @staticmethod
    def _process_plugin(p, i):
        try:
            indicators = p.process(i)
            if not indicators:
                return

            return [ii.__dict__() for ii in indicators if ii]

        except (KeyboardInterrupt, SystemExit):
            return

        except Exception as e:
            if 'SERVFAIL' not in str(e):
                logger.error(e, exc_info=True)
                logger.error(f"[{p}] giving up on {i}")

    def _process_plugins(self, i):
        for p in self.plugins:
            try:
                indicators = self._process_plugin(p, i)

            except Exception as e:
                logger.error(e, exc_info=True)
                continue

            if not indicators or len(indicators) == 0:
                continue

            for ii in indicators:
                ii['iid'] = i.uuid

            try:
                self.router.indicators_create(indicators, fireball=False)

            except zmq.error.Again:
                logger.error('EAGAIN: unable to create indicators.')
                logger.debug(len(indicators))
                logger.debug(indicators)

            except Exception as e:
                # TODO- catch low HWM (EAGAIN) and backoff...
                logger.error(e, exc_info=True)

    def _process_indicator(self, i):
        # searches
        if i.get('nolog', '0') in ['1', 1, True]:
            return

        if not i.get('itype'):
            i = Indicator(
                indicator=i['indicator'],
                tags='search',
                confidence=4,
                group='everyone',
                tlp='amber',
            ).__dict__()

        if not i.get('tags'):
            i['tags'] = []

        if not i.get('confidence', 0):
            return

        if isinstance(i['confidence'], str):
            i['confidence'] = float(i['confidence'])

        if i['confidence'] < MIN_CONFIDENCE:
            return

        if 'predict' in i['tags']:
            return

        ii = Indicator(**i)

        if self._exclude(ii):
            return

        self._process_plugins(ii)

    def _process_message(self, message):
        try:
            [self._process_indicator(i)
             for i in Msg().from_frame(message).data]

        except (KeyboardInterrupt, SystemExit):
            return

        except Exception as e:
            logger.error(e)
            if logger.getEffectiveLevel() == logging.DEBUG:
                traceback.print_exc()

    def start(self):
        loop = IOLoop()
        s = Context().socket(zmq.PULL)
        s.set_hwm(ZMQ_HWM)

        socket = zmqstream.ZMQStream(s, loop)

        socket.on_recv(self._process_message)
        logger.debug(f"connecting to: {HUNTER_ADDR}")
        socket.connect(HUNTER_ADDR)

        # this needs to be done here
        self.router = Client(remote=HUNTER_SINK_ADDR, nowait=True,
                             autoclose=False)

        try:
            loop.start()

        except KeyboardInterrupt as e:
            loop.stop()

        for ss in [s, self.router.socket]:
            ss.close()

        self.stop()


def main():
    p = get_argument_parser()
    p = ArgumentParser(
        description=textwrap.dedent('''\
            Env Variables:

            example usage:
                $ cif-hunter -d
            '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='cif-hunter',
        parents=[p]
    )

    p.add_argument('-w', '--workers', help='Number of workers', default=1)

    args = p.parse_args()
    setup_logging(args)

    if args.verbose:
        logger.setLevel(logging.INFO)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info(f"loglevel: {logger.getEffectiveLevel()}")

    m = Manager(target=Hunter, threads=args.workers)

    m.start()


if __name__ == '__main__':
    main()
