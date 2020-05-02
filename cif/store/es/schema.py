from elasticsearch_dsl import Document, Text, Date, Integer, Float, Ip, \
    Keyword, GeoPoint


class Indicator(Document):

    class Index:
        name = 'indicators-*'

    indicator = Keyword()
    indicator_ipv4 = Ip()
    indicator_ipv4_mask = Integer()
    indicator_ipv6 = Ip()
    indicator_ipv6_mask = Integer()
    group = Keyword()
    itype = Keyword()
    tlp = Keyword()
    provider = Keyword()
    portlist = Text()
    asn = Float()
    asn_desc = Text()
    cc = Text(fields={'raw': Keyword()})
    protocol = Text(fields={'raw': Keyword()})
    confidence = Integer()
    timezone = Text()
    city = Text(fields={'raw': Keyword()})
    description = Keyword()
    tags = Keyword(multi=True, fields={'raw': Keyword()})
    rdata = Keyword()
    count = Integer()
    location = GeoPoint()
    region = Keyword()
    latitude = Float()
    longitude = Float()
    ns = Keyword()
    mx = Keyword()
    reported_at = Date()
    last_at = Date()
    first_at = Date()
    created_at = Date()
