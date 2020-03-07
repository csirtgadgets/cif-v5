import os
import inspect

from cifsdk.constants import RUNTIME_PATH

MOD_PATH = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))

STORE_PATH = os.path.join(MOD_PATH, "store")

STORE_DEFAULT = os.environ.get('CIF_STORE_STORE', 'sqlite')
STORE_PLUGINS = ['cif.store.sqlite']

REQUIRED_ATTRIBUTES = ['group', 'provider', 'indicator', 'itype', 'tags']
TRACE = os.environ.get('CIF_STORE_TRACE')
GROUPS = ['everyone']

LOGLEVEL = os.getenv('CIF_STORE_LOGLEVEL', 'ERROR')

STORE_ADDR = os.path.join(RUNTIME_PATH, 'store.ipc')
STORE_ADDR = f"ipc://{STORE_ADDR}"
STORE_ADDR = os.getenv('CIF_STORE_ADDR', STORE_ADDR)

STORE_WRITE_ADDR = os.path.join(RUNTIME_PATH, 'store_write.ipc')
STORE_WRITE_ADDR = f"ipc://{STORE_WRITE_ADDR}"
STORE_WRITE_ADDR = os.getenv('CIF_STORE_WRITE_ADDR', STORE_WRITE_ADDR)

STORE_DEFAULT = os.getenv('CIF_STORE_STORE', STORE_DEFAULT)

LIMIT = os.getenv('CIF_STORE_RETURN_LIMIT', 250)
LIMIT = int(LIMIT)
