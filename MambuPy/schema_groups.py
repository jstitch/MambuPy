"""Schema tables for Mambu Groups.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   Group
   GroupRoleName

.. todo:: this are just very basic schemas for groups. A some fields
          are missing.
"""

import schema_orm as orm
from schema_branches import Branch
from schema_users import User
import schema_clients

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer, Text

dbname = orm.dbname
session = orm.session
Base = orm.Base

class Group(Base):
    """Group table.
    """
    __tablename__  = "group"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedKey   = Column(String, primary_key=True)
    id           = Column(String, index=True, unique=True)
    groupName    = Column(String)
    homePhone    = Column(String)
    mobilePhone1 = Column(String)
    loanCycle    = Column(Integer)
    creationDate = Column(DateTime)
    notes        = Column(Text)

    # Relationships
    assignedCentreKey = Column(String)
    assignedUserKey   = Column(String, ForeignKey(User.encodedKey))
    assignedBranchKey = Column(String, ForeignKey(Branch.encodedKey))
    user              = relationship(User, back_populates='groups')
    branch            = relationship(Branch, back_populates='groups')
    addresses         = relationship('Address',
                                     back_populates = 'group',
                                     foreign_keys   = 'Address.parentKey',
                                     primaryjoin    = 'Address.parentKey == Group.encodedKey')
    customInformation = relationship('CustomFieldValue',
                                     back_populates = 'group',
                                     foreign_keys   = 'CustomFieldValue.parentKey',
                                     primaryjoin    = 'CustomFieldValue.parentKey == Group.encodedKey')
    loans             = relationship('LoanAccount',
                                     back_populates = 'holder_group',
                                     foreign_keys   = 'LoanAccount.accountHolderKey',
                                     primaryjoin    = 'LoanAccount.accountHolderKey == Group.encodedKey')
    activities        = relationship('Activity', back_populates='group')
    clients           = relationship('Client',
                                secondary=lambda: schema_clients.ClientsGroups,
                                back_populates='groups')
    roles             = relationship('GroupRole', back_populates='group')


    def __repr__(self):
        return "<Group(id={}, groupName={})>".format(self.id, self.groupName)


class GroupRoleName(Base):
    """GroupRoleName table.
    """
    __tablename__  = "grouprolename"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedKey = Column(String, primary_key=True)
    name       = Column(String)

    roles = relationship('schema_clients.GroupRole', back_populates='roleName')

    def __repr__(self):
        return "<GroupRoleName(name={})>".format(self.name)
