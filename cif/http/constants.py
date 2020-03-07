import os.path

RUNTIME_PATH = os.getcwd()
ROUTER_ADDR = 'ipc:///var/folders/dw/3q1bw3dj3ss45f3myjw28c200000gn/T/router.ipc'

HTTP_LISTEN = os.getenv('CIF_HTTPD_LISTEN', '127.0.0.1')

TRACE = os.getenv('CIF_HTTPD_TRACE', 0)
HTTP_LISTEN_PORT = os.getenv('CIF_HTTPD_LISTEN_PORT', 5000)

# NEEDS TO BE STATIC TO WORK WITH SESSIONS
SECRET_KEY = os.getenv('CIF_HTTPD_SECRET_KEY', os.urandom(24))

HTTPD_PROXY = os.getenv('CIF_HTTPD_PROXY')

LOGLEVEL = 'ERROR'
LOGLEVEL = os.getenv('CIF_HTTPD_LOGLEVEL', LOGLEVEL).upper()

ITYPES = ['ipv4', 'ipv6', 'url', 'fqdn', 'sha1', 'sha256', 'sha512', 'email',
          'asn']
