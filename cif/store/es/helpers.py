from csirtg_indicator.utils import resolve_itype
import re
import binascii
import socket


def expand_ip_idx(data):
    itype = resolve_itype(data['indicator'])
    if itype not in ['ipv4', 'ipv6']:
        return

    if itype is 'ipv4':
        match = re.search('^(\S+)\/(\d+)$', data['indicator'])
        if match:
            data['indicator_ipv4'] = match.group(1)
            data['indicator_ipv4_mask'] = match.group(2)
        else:
            data['indicator_ipv4'] = data['indicator']

        return

    # compile?
    match = re.search('^(\S+)\/(\d+)$', data['indicator'])
    if match:
        data['indicator_ipv6'] = match.group(1)
        data['indicator_ipv6_mask'] = match.group(2)

    else:
        data['indicator_ipv6'] = data['indicator']


def expand_location(indicator):
    if not indicator.get('latitude'):
        return
    
    indicator['location'] = {}
    indicator['location']['lat'] = indicator.get('latitude', 0)
    indicator['location']['lon'] = indicator.get('longitude', 0)
