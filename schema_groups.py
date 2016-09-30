"""Schema tables for Mambu Groups.

TODO: this are just very basic schemas for groups. A some fields
are missing.
"""

from mambuutil import connectDb, dbname

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

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


class GroupBranch(Base):
    """Branch table.
    Related with group
    """
    __tablename__  = "branch"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedkey   = Column(String, primary_key=True)
    id           = Column(String, index=True, unique=True)
    name         = Column(String)
    notes        = Column(String)
    phonenumber  = Column(String)
    emailaddress = Column(String)

    def __repr__(self):
        return "<Branch(id={}, name={})>".format(self.id, self.name)


class Group(Base):
    """Group table.
    """
    __tablename__  = "group"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedkey = Column(String, primary_key=True)
    id         = Column(String, index=True, unique=True)
    groupname  = Column(String)
    loancycle  = Column(Integer)

    # Relationships
    assignedbranchkey = Column(String, ForeignKey(GroupBranch.encodedkey))
    branch            = relationship('GroupBranch', backref=backref('groups'))

    def __repr__(self):
        return "<Group(id={}, groupname={})>".format(self.id, self.groupname)
