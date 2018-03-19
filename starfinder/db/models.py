import contextlib

import sqlalchemy as sa
from sqlalchemy import orm

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