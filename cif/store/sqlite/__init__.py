import logging
import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine

from cifsdk.constants import DATA_PATH

from .constants import BASE
from .indicator import Indicator, IndicatorManager

DB_PATH = os.path.join(DATA_PATH, 'cifv5.db')
DB_PATH = f"sqlite:///{DB_PATH}"

logger = logging.getLogger(__name__)
TRACE = os.environ.get('CIF_STORE_SQLITE_TRACE', '0')

# http://stackoverflow.com/q/9671490/7205341
SYNC = os.environ.get('CIF_STORE_SQLITE_SYNC', 'NORMAL')

# https://www.sqlite.org/pragma.html#pragma_cache_size
CACHE_SIZE = os.environ.get('CIF_STORE_SQLITE_CACHE_SIZE', 512000000)  # 512MB

AUTOFLUSH = os.getenv('CIF_STORE_SQLITE_AUTOFLUSH', '1')
if AUTOFLUSH == '0':
    AUTOFLUSH = False
else:
    AUTOFLUSH = True


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

TRACE = False
if os.getenv('CIF_STORE_SQLITE_TRACE', '0') == '1':
    TRACE = True

else:
    logger.setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA synchronous = {}".format(SYNC))
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.execute("PRAGMA cache_size = {}".format(CACHE_SIZE))
    cursor.close()


class SQLite(object):
    # http://www.pythoncentral.io/sqlalchemy-orm-examples/
    name = 'sqlite'

    def __init__(self, autocommit=False, autoflush=AUTOFLUSH, dictrows=True,
                 s=None, **kwargs):
        self.autocommit = autocommit
        self.autoflush = autoflush
        self.dictrows = dictrows

        self.path = kwargs.get('db_path', DB_PATH)

        logger.debug(self.path)

        # http://docs.sqlalchemy.org/en/latest/orm/contextual.html
        self.engine = create_engine(self.path, echo=TRACE)

        if s:
            self.handle = s

        else:
            self.handle = sessionmaker(bind=self.engine,
                                       autocommit=self.autocommit,
                                       autoflush=self.autoflush)
            self.handle = scoped_session(self.handle)

        BASE.metadata.create_all(self.engine)

        logger.debug('database path: {}'.format(self.path))

        self.indicators = IndicatorManager(self.handle, self.engine)


Plugin = SQLite
