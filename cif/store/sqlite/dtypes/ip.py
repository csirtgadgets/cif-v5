from sqlalchemy.ext.declarative import declarative_base
from . import IOCType
import socket
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class Ip(IOCType):
    # http://docs.sqlalchemy.org/en/latest/_modules/examples/postgis/postgis.html
    # http://docs.sqlalchemy.org/en/latest/core/custom_types.html#creating-new-types
    # http://sqlalchemy-utils.readthedocs.io/en/latest/_modules/sqlalchemy_utils/types/uuid.html
    # https://github.com/zzzeek/sqlalchemy/blob/master/lib/sqlalchemy/sql/sqltypes.py#L852

    def __init__(self, version=4):
        self.version = version

    def get_col_spec(self, **kw):
        return 'IP'

    def bind_processor(self, dialect):

        DBAPIBinary = dialect.dbapi.Binary

        def process(value):
            if self.version == 6:
                value = socket.inet_pton(socket.AF_INET6, value)
            else:
                value = socket.inet_pton(socket.AF_INET, value)

            return DBAPIBinary(value)

        try:
            return process

        except Exception as e:
            logger.error(e)
            raise

    def result_processor(self, dialect, coltype):
        def process(value):
            return socket.inet_ntop(value)

        return process
