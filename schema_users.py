"""Schema tables for Mambu Users.

TODO: this are just very basic schemas for users.
"""

import schema_orm as orm
from schema_branches import Branch

from sqlalchemy.orm import relationship
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
    encodedKey = Column(String) # this MUST be declared before primary_key
    encodedkey = Column(String, primary_key=True)
    name       = Column(String)
    users      = relationship('User', back_populates='role')

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
    encodedKey          = Column(String) # this MUST be declared before primary_key
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
    branch            = relationship(Branch, back_populates='users')

    role_encodedkey_oid = Column(String, ForeignKey(Role.encodedkey))
    role                = relationship(Role, back_populates='users')

    custominformation   = relationship('CustomFieldValue',
                                       back_populates = 'user',
                                       foreign_keys   = 'CustomFieldValue.parentkey',
                                       primaryjoin    = 'CustomFieldValue.parentkey == User.encodedkey')
    activities          = relationship('Activity',
                                       primaryjoin    = 'User.encodedkey==Activity.userkey',
                                       back_populates = 'user')
    assignedactivities  = relationship('Activity',
                                       primaryjoin    = 'User.encodedkey==Activity.assigneduserkey',
                                       back_populates = 'assigneduser')
    groups              = relationship('Group', back_populates = 'user')
    loans               = relationship('LoanAccount', back_populates = 'user')

    # redundant with same-as-RESTAPI-case
    firstName     = Column(String)
    lastName      = Column(String)
    userName      = Column(String)
    creationDate  = Column(DateTime)
    homePhone     = Column(String)
    mobilePhone1  = Column(String)
    userState     = Column(String)
    isCreditOfficer = Column(Integer)
    # redundant relationships camelCase
    assignedBranchKey = Column(String)
    role_encodedKey_oid = Column(String)
    customInformation   = relationship('CustomFieldValue',
                                       back_populates = 'user',
                                       foreign_keys   = 'CustomFieldValue.parentkey',
                                       primaryjoin    = 'CustomFieldValue.parentkey == User.encodedkey')
    assignedActivities  = relationship('Activity',
                                       primaryjoin    = 'User.encodedkey==Activity.assigneduserkey',
                                       back_populates = 'assigneduser')

    @property
    def name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def __repr__(self):
        return "<User(id={}, name={})>".format(self.id, self.name)
