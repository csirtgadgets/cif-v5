#!/usr/bin/env python3

import logging
import os
import traceback
import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from flask import Flask, make_response
from flask_cors import CORS
from flask_compress import Compress
from flask_restplus import Api
from werkzeug.middleware.proxy_fix import ProxyFix


from cifsdk.utils import setup_logging, setup_runtime_path, get_argument_parser
from .constants import HTTP_LISTEN, HTTP_LISTEN_PORT, TRACE, SECRET_KEY
from cif.constants import VERSION

from .indicators import api as indicators_api

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

CORS(app, resources={r"/*": {"origins": "*"}})
Compress(app)

api = Api(app, version=VERSION, title='CIFv5 API', description='The CIFv5 API')


def output_csv(data, code, headers=None):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


api.representations['text/plain'] = output_csv
api.add_namespace(indicators_api)

app.secret_key = SECRET_KEY

log_level = logging.WARN
if TRACE == '1':
    log_level = logging.DEBUG
    logging.getLogger('flask_cors').level = logging.INFO

console = logging.StreamHandler()
logging.getLogger('gunicorn.error').setLevel(log_level)
logging.getLogger('gunicorn.error').addHandler(console)
logger = logging.getLogger('gunicorn.error')


def main():

    p = get_argument_parser()
    p = ArgumentParser(
        description=textwrap.dedent('''\
        example usage:
            $ cif-httpd -d
        '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='cif-httpd',
        parents=[p]
    )

    p.add_argument('--fdebug', action='store_true')

    args = p.parse_args()
    setup_logging(args)

    logger.info('loglevel is: {}'.
                format(logging.getLevelName(logger.getEffectiveLevel())))

    setup_runtime_path(args.runtime_path)

    if not args.fdebug:
        # http://stackoverflow.com/a/789383/7205341
        pid = str(os.getpid())
        logger.debug("pid: %s" % pid)

    try:
        logger.info('pinging router...')
        logger.info('starting up...')

        app.run(host=HTTP_LISTEN, port=HTTP_LISTEN_PORT, debug=args.fdebug)

    except KeyboardInterrupt:
        logger.info('shutting down...')

    except Exception as e:
        logger.critical(e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
