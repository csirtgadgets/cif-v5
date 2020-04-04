import arrow
import ujson as json
import logging

from sqlalchemy import Column, Integer, String, Float, DateTime, UnicodeText, \
    ForeignKey, Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils.types.url import URLType
from sqlalchemy_utils.types.email import EmailType

from cif.store.sqlite.constants import BASE
from cif.store.sqlite.dtypes.ip import Ip
from cif.store.sqlite.dtypes.fqdn import FQDNType
from cif.store.sqlite.dtypes.hash import HASHType

from csirtg_indicator.wrappers.itypes import ItypesMixin

basestring = (str, bytes)

HASH_TYPES = ['sha1', 'sha256', 'sha512', 'md5']
REQUIRED_FIELDS = ['provider', 'indicator', 'tags', 'group', 'itype']

logger = logging.getLogger('cif.store.sqlite')


class Indicator(BASE, ItypesMixin):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, index=True)
    indicator = Column(UnicodeText, index=True)
    group = Column(String, index=True)
    itype = Column(String, index=True)
    tlp = Column(String)
    provider = Column(String, index=True)
    portlist = Column(String)
    asn_desc = Column(UnicodeText, index=True)
    asn = Column(Float, index=True)
    cc = Column(String, index=True)
    prefix = Column(UnicodeText, index=True)
    protocol = Column(Integer)
    reported_at = Column(DateTime, index=True)
    first_at = Column(DateTime)
    last_at = Column(DateTime, index=True)
    confidence = Column(Float, index=True)
    timezone = Column(String)
    city = Column(String)
    longitude = Column(String)
    latitude = Column(String)
    peers = Column(UnicodeText)
    description = Column(UnicodeText)
    additional_data = Column(UnicodeText)
    rdata = Column(UnicodeText, index=True)
    count = Column(Integer)
    region = Column(String, index=True)
    related = Column(String, index=True)
    reference = Column(UnicodeText)
    reference_tlp = Column(String)
    iid = Column(String, index=True)
    oid = Column(String, index=True)
    drop_index = Column(Float, index=True)

    tags = relationship(
        'Tag',
        primaryjoin='and_(Indicator.id==Tag.indicator_id)',
        backref=backref('tags', uselist=True),
        lazy='subquery',
        innerjoin=True,
        cascade="all,delete"
    )

    def __init__(self, **kwargs):

        for f in ['uuid', 'indicator', 'itype', 'tlp', 'provider',
                  'asn', 'asn_desc', 'cc', 'prefix', 'protocol',
                  'reported_at', 'first_at', 'confidence', 'reference',
                  'reference_tlp', 'timezone', 'city', 'longitude',
                  'latitude', 'peers', 'description', 'additional_data',
                  'rdata', 'rdata_type', 'count', 'region', 'related', 'oid',
                  'iid', 'drop_index', 'asn_type', 'portlist', 'last_at']:
            setattr(self, f, kwargs.get(f))

        self.group = kwargs.get('group', 'everyone')

        if self.reported_at and isinstance(self.reported_at, basestring):
            self.reported_at = arrow.get(self.reported_at).datetime

        if self.last_at and isinstance(self.last_at, basestring):
            self.last_at = arrow.get(self.last_at).datetime

        if self.first_at and isinstance(self.first_at, basestring):
            self.first_at = arrow.get(self.first_at).datetime

        if self.peers is not None:
            self.peers = json.dumps(self.peers)

        if self.additional_data is not None:
            self.additional_data = json.dumps(self.additional_data)

    def is_valid(self):
        for f in REQUIRED_FIELDS:
            if not self.get(f):
                raise ValueError(f"Missing required field: {f} for \n"
                                 f"{self.indicator}")


class Ipv4(BASE):
    __tablename__ = 'indicators_ipv4'

    id = Column(Integer, primary_key=True)
    ip = Column(Ip, index=True)
    mask = Column(Integer, default=32)

    indicator_id = Column(Integer, ForeignKey('indicators.id',
                                              ondelete='CASCADE'))
    indicator = relationship(
        Indicator,
    )


class Ipv6(BASE):
    __tablename__ = 'indicators_ipv6'

    id = Column(Integer, primary_key=True)
    ip = Column(Ip(version=6), index=True)
    mask = Column(Integer, default=128)

    indicator_id = Column(Integer, ForeignKey('indicators.id',
                                              ondelete='CASCADE'))
    indicator = relationship(
        Indicator,
    )


class Fqdn(BASE):
    __tablename__ = 'indicators_fqdn'

    id = Column(Integer, primary_key=True)
    fqdn = Column(FQDNType, index=True)

    indicator_id = Column(Integer, ForeignKey('indicators.id',
                                              ondelete='CASCADE'))
    indicator = relationship(
        Indicator,
    )


class Email(BASE):
    __tablename__ = 'indicators_email'

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, index=True)

    indicator_id = Column(Integer, ForeignKey('indicators.id',
                                              ondelete='CASCADE'))
    indicator = relationship(
        Indicator,
    )


class Url(BASE):
    __tablename__ = 'indicators_url'

    id = Column(Integer, primary_key=True)
    url = Column(URLType, index=True)

    indicator_id = Column(Integer, ForeignKey('indicators.id',
                                              ondelete='CASCADE'))
    indicator = relationship(
        Indicator,
    )


class Hash(BASE):
    __tablename__ = 'indicators_hash'

    id = Column(Integer, primary_key=True)
    hash = Column(HASHType, index=True)

    indicator_id = Column(Integer, ForeignKey('indicators.id',
                                              ondelete='CASCADE'))
    indicator = relationship(
        Indicator,
    )


class Tag(BASE):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    tag = Column(String, index=True)

    indicator_id = Column(Integer, ForeignKey('indicators.id',
                                              ondelete='CASCADE'))
    indicator = relationship(
        Indicator,
    )

    __table_args__ = (Index('ix_tags_indicator', "tag", "indicator_id"),)
