"""`SQLAlchemy <http://www.sqlalchemy.org/>`_ ORM for a Mambu Database backup.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

This is the basic module that holds a default session (and a default
Session maker and a connected engine) which is used on every ORM
module on MambuPy.

The default engine is connected to a database according to what you
configured on mambuconfig module.

This module also holds the Base declarative_base used for every ORM on
MambuPy.

Every ORM module on MambuPy (named schema_*.py) should ideally get the
default session, Base and etc. from here, allowing the user to use the
same session and etc. for the day-to-day work. If you chose to use
another session, please mind that you should replace the session on
every schema_*.py you need.

This last requirement also applies for the Base, or for the engine and
the sessionmaker for that matter.
"""
from __future__ import absolute_import

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from ..mambuconfig import dbeng, dbhost, dbname, dbport, dbpwd, dbuser


# Connects to DB
def connect_db(
    engine=dbeng,
    user=dbuser,
    password=dbpwd,
    host=dbhost,
    port=dbport,
    database=dbname,
    params="?charset=utf8&use_unicode=1",
    echoopt=False,
):
    """Connect to database utility function.

    Uses SQLAlchemy ORM library.

    Useful when using schema modules in MambuPy
    """
    return create_engine(
        "%s://%s:%s@%s:%s/%s%s" % (engine, user, password, host, port, database, params),
        poolclass=NullPool,
        isolation_level="READ UNCOMMITTED",
        echo=echoopt,
    )


engine = connect_db()
"""Database engine, connecting with default parameters by default.
"""

session_factory = sessionmaker(bind=engine)
"""Sessionmaker object, create factory sessions.
"""

Session = scoped_session(session_factory)
"""Scoped session object.
"""

session = Session()
"""Default session created here.
"""

Base = declarative_base()
"""Declarative base for models.
"""
