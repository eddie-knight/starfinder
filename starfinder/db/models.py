import contextlib

import sqlalchemy as sa
from sqlalchemy import orm, func
from sqlalchemy.ext import declarative

from starfinder import config, logging

CONF = config.CONF
LOG = logging.get_logger(__name__)
DB_NAME = "starfinder_{}".format(CONF.get("ENVIRONMENT"))
ENGINE_URL = CONF.get("DB_ENGINE_URL")
TABLE_KWARGS = {"mysql_engine": "InnoDB",
                "mysql_charset": "utf8",
                "mysql_collate": "utf8_general_ci"}

connection_debug = CONF.get("database.connection.debug")
connection_debug = connection_debug.lower() == "true"
connection_pool_size = int(CONF.get("database.connection.poolsize"))
connection_overflow_pool = int(CONF.get("database.connection.overflowpool"))
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

class MetaBase(declarative.DeclarativeMeta):
    def __init__(cls, klsname, bases, attrs):
        if klsname != "Base":
            super().__init__(klsname, bases, attrs)
            for attr_name, attr in attrs.items():
                if isinstance(attr, sa.Column):
                    query_single_getter_name = "get_by_{}".format(attr_name)
                    query_all_getter_name = "get_all_by_{}".format(attr_name)
                    if not hasattr(cls, query_single_getter_name):
                        setattr(cls, query_single_getter_name,
                                functools.partial(cls._get_by, attr))

                    if not hasattr(cls, query_all_getter_name):
                        setattr(cls, query_all_getter_name,
                                functools.partial(cls._get_all_by, attr))


class ModelBase(object):
    created_at = sa.Column(sa.DateTime(), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(), onupdate=func.now())
    __table_args__ = TABLE_KWARGS

    @declarative.declared_attr
    def __tablename__(cls):
        """ Returns a snake_case form of the table name. """
        return db_utils.pluralize(db_utils.to_snake_case(cls.__name__))

    def __eq__(self, other):
        if not other:
            return False
        return self.id == other.id

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if hasattr(self, key):
            return setattr(self, key, value)
        raise AttributeError(key)

    def __contains__(self, key):
        return hasattr(self, key)

    def update(self, **fields):
        for attr, value in fields.items():
            if attr not in self:
                raise exception.ModelUnknownAttrbute(model=self, attr=attr)
            self[attr] = value
        return self

    @classmethod
    def get(cls, pk):
        return Session.query(cls).filter(cls.id == pk).first()

    @classmethod
    def _get_by_property(cls, prop):
        LOG.debug("Fetching '%s' by property '%s'", cls, prop)
        return Session.query(cls).filter(prop).first()

    @classmethod
    def _get_by(cls, field, value):
        LOG.debug("Fetching one '%s.%s' by value '%s'", cls, field, value)
        return Session.query(cls).filter(field == value).first()

    @classmethod
    def _get_all_by(cls, field, value):
        LOG.debug("Fetching all '%s.%s' with value '%s'", cls, field, value)
        return Session.query(cls).filter(field == value).all()

    def save(self):
        LOG.debug("Attempting to save '%s'", self)
        with transaction() as session:
            session.add(self)

    def delete(self):
        LOG.debug("Attempting to delete '%s'", self)
        with transaction() as session:
            session.delete(self)

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()
                if not callable(value) and not key.startswith('_')}


Base = declarative.declarative_base(cls=ModelBase, bind=engine,
                                    metaclass=MetaBase)
