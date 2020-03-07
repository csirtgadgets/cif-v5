
from zmq import DEALER
from cif.store.constants import STORE_ADDR, STORE_WRITE_ADDR
from cifsdk.actor.manager import Manager as _Manager
from cif.store import Store


class Manager(_Manager):

    def __init__(self, context):
        _Manager.__init__(self, Store, 1)

        self.socket = context.socket(DEALER)
        self.socket.bind(STORE_ADDR)

        self.s_write = context.socket(DEALER)
        self.s_write.bind(STORE_WRITE_ADDR)
