"""Schema tables for Mambu Users.

TODO: this are just very basic schemas for users.
"""

import schema_orm as orm
from schema_branches import Branch
from schema_customfields import CustomFieldValue

from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

dbname = orm.dbname
session = orm.session
Base = orm.Base

class Role(Base):
    """Role table.
    Related with user
    """
    __tablename__  = "role"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedkey = Column(String, primary_key=True)
    name      = Column(String)

    def __repr__(self):
        return "<Role(name={})>".format(self.name)

class User(Base):
    """User table.
    """
    __tablename__  = "user"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedkey    = Column(String, primary_key=True)
    id            = Column(String, index=True, unique=True)
    firstname     = Column(String)
    lastname      = Column(String)
    username      = Column(String)
    creationdate  = Column(DateTime)
    homephone     = Column(String)
    mobilephone1  = Column(String)
    email         = Column(String)
    userstate     = Column(String)
    iscreditofficer = Column(Integer)

    # Relationships
    assignedbranchkey = Column(String, ForeignKey(Branch.encodedkey))
    branch            = relationship(Branch, backref=backref('users'))

    role_encodedkey_oid = Column(String, ForeignKey(Role.encodedkey))
    role                = relationship(Role, backref=backref('users'))

    custominformation   = relationship(CustomFieldValue,
                                       backref=backref('user'),
                                       foreign_keys=[CustomFieldValue.parentkey],
                                       primaryjoin='CustomFieldValue.parentkey == User.encodedkey')

    def name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def __repr__(self):
        return "<User(id={}, name={})>".format(self.id, self.name())
