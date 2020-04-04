import os
from csirtg_indicator.feed import process as feed
from csirtg_indicator.feed.fqdn import process as feed_fqdn
from csirtg_indicator.feed.ipv4 import process as feed_ipv4
from csirtg_indicator.feed.ipv6 import process as feed_ipv6

FEEDS_DAYS = 60
FEEDS_LIMIT = os.getenv("CIF_HTTPD_FEED_LIMIT", 500)
FEEDS_WHITELIST_LIMIT = os.getenv("CIF_HTTPD_FEED_WHITELIST_LIMIT", 1000)
FEEDS_WHITELIST_DAYS = 14

HTTPD_FEED_WHITELIST_CONFIDENCE = \
    os.getenv('CIF_HTTPD_FEED_WHITELIST_CONFIDENCE', 3)

CONFIDENCE_DEFAULT = 3

FEED_PLUGINS = {
    'ipv4': feed_ipv4,
    'ipv6': feed_ipv6,
    'fqdn': feed_fqdn,
    'url': feed,
    'email': feed,
    'md5': feed,
    'sha1': feed,
    'sha256': feed,
    'sha512': feed,
    'asn': feed,
}

DAYS_SHORT = 21
DAYS_MEDIUM = 60
DAYS_LONG = 90
DAYS_REALLY_LONG = 180

FEED_DAYS = {
    'ipv4': DAYS_SHORT,
    'ipv6': DAYS_SHORT,
    'url': DAYS_MEDIUM,
    'email': DAYS_MEDIUM,
    'fqdn': DAYS_MEDIUM,
    'md5': DAYS_MEDIUM,
    'sha1': DAYS_MEDIUM,
    'sha256': DAYS_MEDIUM,
    'asn': DAYS_MEDIUM,
}
