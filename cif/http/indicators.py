import logging
import traceback
from json import loads
from flask_restplus import Namespace, Resource, fields
from flask import request, current_app
import zmq
from pprint import pprint

from cifsdk.client.zeromq import ZMQ as Client
from csirtg_indicator.format.csv import get_lines
from csirtg_indicator.constants import FIELDS

from .utils import filters_cleanup, is_human
from .feeds import get_feed
from .constants import ITYPES

logger = logging.getLogger('cif-httpd')

api = Namespace('indicators', description='Indicator related operations')


F = {}
for ff in FIELDS:
    if ff.endswith('_at'):
        F[ff] = fields.DateTime
    else:
        F[ff] = fields.String

F['confidence'] = fields.Integer(min=0, max=4)
F['asn'] = fields.Integer
F['tlp'] = fields.String(enum=['white', 'green', 'amber', 'red'])

for ee in ['peers', 'upstream', 'downstream', 'tags']:
    F[ee] = fields.List(fields.String)

F['itype'] = fields.String(enum=ITYPES)

indicator = api.model('Indicator', F)

filters = api.model('Filters', {
    'indicator': fields.String(),
    'itype': fields.String(enum=ITYPES),
    'confidence': fields.Integer(min=0, max=4),
    'provider': fields.String,
    'group': fields.String,
    'tlp': fields.String(enum=['white', 'green', 'amber', 'red']),
    'tags': fields.List(fields.String)
})

Data = api.model('Data', {'data': fields.Integer})
indicators = fields.List


def _search_bulk(f):
    try:
        with Client() as client:
            r = client.indicators_search(f)

    except zmq.error.Again as e:
        return api.abort(503)

    except Exception as e:
        logger.error(e)
        if logger.getEffectiveLevel() == logging.DEBUG:
            traceback.print_exc()

        if 'invalid search' in str(e):
            logger.error(e)
            return api.abort(400, str(e))

        return api.abort(500)

    return r


def _indicators_create(data):
    n = 0
    try:
        with Client() as cli:
            r = cli.indicators_create(data)
            if isinstance(r, int):
                n += r

            # return from fireball
            else:
                for i in r:
                    if i['status'] != 'success':
                        logger.error('batch failed..')
                        continue

                    n += i['data']

    except zmq.error.Again as e:
        return api.abort(503)

    except Exception as e:
        logger.error(e)
        if logger.getEffectiveLevel() == logging.DEBUG:
            traceback.print_exc()

        return api.abort(500)

    return n


@api.route('')
class IndicatorList(Resource):
    @api.param('q', 'The indicator to search for (eg: 1.1.1.1)')
    @api.param('indicator', 'The Indicator to search for (eg: 1.1.1.1')
    @api.param('itype', 'by itype (eg: url, ipv4, ipv6, fqdn, sha1, sha256..')
    @api.param('tags', 'by tags (eg: botnet, phishing, proxy, malware')
    @api.param('confidence', 'by confidence (0-4)')
    @api.param('reported_at', 'by reported_at >= (eg: 2020-01-01T00:00:00')
    @api.param('hours', 'by last N hours (eg: 1)')
    @api.param('days', 'by last N days (eg: 7)')
    @api.param('provider', 'by provider (eg: csirtg.io)')
    # @api.marshal_list_with(indicator)
    def get(self):
        """Search Indicators by Parameters"""

        f = filters_cleanup(request)

        if not f.get('indicator') and not f.get('tags') and \
                not f.get('itype'):
            return 'q OR tags|itype params required', 400

        if current_app.config.get('dummy'):
            return [{'indicator': f['indicator']}], 200

        if f.get('indicator') and ',' in f['indicator']:
            return _search_bulk([{'indicator': i} for i in f['indicator']
                                .split(',')]), 200

        try:
            rv = get_feed(f)

        except SyntaxError as e:
            api.abort(400, str(e))

        except TypeError as e:
            logger.debug(e, exc_info=True)
            api.abort(400)

        except PermissionError as e:
            api.abort(401)

        except ConnectionError as e:
            api.abort(503)

        except Exception as e:
            logger.error(e)
            if logger.getEffectiveLevel() == logging.DEBUG:
                traceback.print_exc()

            api.abort(500)

        else:
            if is_human(request.headers):
                csv = ''
                for l in get_lines(rv):
                    # TODO- headers
                    csv += l

                return csv, 200

            return rv, 200

    @api.expect([filters])
    @api.marshal_list_with(indicator)
    def post(self):
        """Search Indicators in Bulk"""

        if request.data == b'':
            return 'invalid search', 400

        data = request.data.decode('utf-8')

        try:
            data = loads(data)

        except Exception as e:
            logger.error(e)
            return 'invalid search', 400

        results = _search_bulk(data)

        return results, 200

    @api.expect([indicator])
    @api.marshal_with(Data)
    def put(self):
        """Create Indicators from a List"""
        if request.data == b'':
            return 'invalid search', 400

        data = request.data.decode('utf-8')

        try:
            data = loads(data)

        except Exception as e:
            logger.error(e)
            return 'invalid search', 400

        rv = _indicators_create(data)
        return {'data': rv}, 200
