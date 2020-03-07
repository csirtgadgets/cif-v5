

import zmq

from cifsdk.actor.manager import Manager as _Manager
from cif.hunter import Hunter

from cif.hunter.constants import HUNTER_SINK_ADDR, HUNTER_ADDR


class Manager(_Manager):

    def __init__(self, context, threads=2):
        _Manager.__init__(self, Hunter, threads)

        self.sink = context.socket(zmq.ROUTER)
        self.sink.bind(HUNTER_SINK_ADDR)

        self.socket = context.socket(zmq.PUSH)
        self.socket.bind(HUNTER_ADDR)
