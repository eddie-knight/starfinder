import contextlib

import sqlalchemy as sa
from sqlalchemy import orm

from starfinder import config, logging

CONF = config.CONF
LOG = logging.get_logger(__name__)
DB_NAME = "starfinder_{}".format(CONF.get("ENVIRONMENT"))
ENGINE_URL = CONF.get("DB_ENGINE_URL")

connection_debug = CONF.get("database.connection.debug")
connection_debug = connection_debug.lower() == "true"
connection_pool_size = int(CONF.get("database.connection.poolsize"))
connection_overflow_pool = int(CONF.get("database.connection.overflowpool"))
# NOTE: MySQL defaults to 8 hour connection timeouts. It's possible that
#      docker-compose or our hosting provider will sever connections sooner.
#      if we see "MySQL has gone away" tweaking this variable is the thing
#      to revisit
connection_pool_recycle = int(CONF.get("database.connection.poolrecycle"))

engine_kwargs = {}
if "sqlite" not in ENGINE_URL:
    engine_kwargs = {
        "pool_size": connection_pool_size,
        "max_overflow": connection_overflow_pool,
        "pool_recycle": connection_pool_recycle}

engine = sa.create_engine(ENGINE_URL, echo=connection_debug,
                          **engine_kwargs)

SessionFactory = orm.sessionmaker(bind=engine, expire_on_commit=False,
                                  autocommit=False, autoflush=True)

ScopedSession = orm.scoped_session(SessionFactory)
Session = ScopedSession


def can_connect():
    try:
        engine.connect()
        return True
    except Exception:
        return False


def teardown():
    ScopedSession.remove()


@contextlib.contextmanager
def transaction():
    try:
        session = ScopedSession()
        yield session
        session.commit()
    except:
        LOG.exception("Transaction failed! Rolling back...")
        session.rollback()
        raise
