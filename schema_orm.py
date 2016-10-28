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
