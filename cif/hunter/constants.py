import os
from cifsdk.constants import RUNTIME_PATH

HUNTER_ADDR = os.path.join(RUNTIME_PATH, 'hunter.ipc')
HUNTER_ADDR = f"ipc://{HUNTER_ADDR}"
HUNTER_ADDR = os.getenv('CIF_HUNTER_ADDR', HUNTER_ADDR)

HUNTER_SINK_ADDR = os.path.join(RUNTIME_PATH, 'hunter_sink.ipc')
HUNTER_SINK_ADDR = f"ipc://{HUNTER_SINK_ADDR}"
HUNTER_SINK_ADDR = os.getenv('CIF_HUNTER_SINK_ADDR', HUNTER_SINK_ADDR)

SNDTIMEO = os.getenv('CIF_HUNTER_ZMQ_SNDTIMEO', '5000')
SNDTIMEO = int(SNDTIMEO)

RCVTIMEO = os.getenv('CIF_HUNTER_ZMQ_RCVTIMEO', '5000')
RCVTIMEO = int(RCVTIMEO)

ZMQ_HWM = os.getenv('CIF_HUNTER_ZMQ_HWM', '10000')
ZMQ_HWM = int(ZMQ_HWM)

THREADS = os.getenv('CIF_HUNTER_THREADS', '0')
THREADS = int(THREADS)

EXCLUDE = os.environ.get('CIF_HUNTER_EXCLUDE', None)
HUNTER_ADVANCED = os.getenv('CIF_HUNTER_ADVANCED', 0)

CONFIG_PATH = os.environ.get('CIF_ROUTER_CONFIG_PATH', 'router.yml')
if not os.path.isfile(CONFIG_PATH):
    CONFIG_PATH = os.environ.get('CIF_ROUTER_CONFIG_PATH',
                                 os.path.join(os.path.expanduser('~'),
                                              'router.yml'))

TRACE = False
if os.environ.get('CIF_HUNTER_TRACE', '') == '1':
    TRACE = True

MIN_CONFIDENCE = os.getenv('CIF_HUNTER_MIN_CONFIDENCE', 1.0)

LOGLEVEL = os.getenv('CIF_HUNTER_LOGLEVEL', 'ERROR')
