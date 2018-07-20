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

from mambuutil import connectDb, dbname

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = connectDb()
"""Database engine, connecting with default parameters by default.
"""

Session = sessionmaker(bind=engine)
"""Sessionmaker object.
"""

session = Session()
"""Default session created here.
"""

Base = declarative_base()
"""Declarative base for models.
"""
