
import os
from cifsdk.constants import RUNTIME_PATH

LOG_LEVEL = os.getenv('CIF_ROUTER_LOGLEVEL', 'ERROR')

ZMQ_HWM = os.getenv('ROUTER_ZMQ_HWM', '1000')
ZMQ_HWM = int(ZMQ_HWM)

TRACE = False
if os.getenv('CIF_ROUTER_TRACE', '0') == '1':
    TRACE = True

ZMQ_SNDTIMEO = os.getenv('CIF_ZMQ_SNDTIMEO', '5000')
ZMQ_SNDTIMEO = int(ZMQ_SNDTIMEO)

ZMQ_RCVTIMEO = os.getenv('CIF_ZMQ_RCVTIMEO', '5000')
ZMQ_RCVTIMEO = int(ZMQ_RCVTIMEO)

FRONTEND_TIMEOUT = os.getenv('CIF_FRONTEND_TIMEOUT', 1)
BACKEND_TIMEOUT = os.getenv('CIF_BACKEND_TIMEOUT', 1)

ROUTER_ADDR = os.path.join(RUNTIME_PATH, 'router.ipc')
ROUTER_ADDR = f"ipc://{ROUTER_ADDR}"
ROUTER_ADDR = os.getenv('CIF_ROUTER_ADDR', ROUTER_ADDR)

ENRICHMENT = False
if os.getenv('CIF_ENRICHMENT', '') == '1':
    ENRICHMENT = True

HUNT = False
if os.getenv('CIF_HUNT', '') == '1':
    HUNT = True
