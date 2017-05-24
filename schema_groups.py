"""Schema tables for Mambu Groups.

TODO: this are just very basic schemas for groups. A some fields
are missing.
"""

import schema_orm as orm
from schema_branches import Branch
from schema_users import User
import schema_clients

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

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
    encodedKey = Column(String) # this MUST be declared before primary_key
    encodedkey = Column(String, primary_key=True)
    id         = Column(String, index=True, unique=True)
    groupname  = Column(String)
    loancycle  = Column(Integer)
    creationdate = Column(DateTime)

    # Relationships
    assignedcentrekey = Column(String)
    assignedbranchkey = Column(String, ForeignKey(Branch.encodedkey))
    branch            = relationship(Branch, back_populates='groups')
    assigneduserkey   = Column(String, ForeignKey(User.encodedkey))
    user              = relationship(User, back_populates='groups')
    addresses         = relationship('Address',
                                     back_populates = 'group',
                                     foreign_keys   = 'Address.parentkey',
                                     primaryjoin    = 'Address.parentkey == Group.encodedkey')
    custominformation = relationship('CustomFieldValue',
                                     back_populates = 'group',
                                     foreign_keys   = 'CustomFieldValue.parentkey',
                                     primaryjoin    = 'CustomFieldValue.parentkey == Group.encodedkey')
    loans             = relationship('LoanAccount',
                                     back_populates = 'holder_group',
                                     foreign_keys   = 'LoanAccount.accountholderkey',
                                     primaryjoin    = 'LoanAccount.accountholderkey == Group.encodedkey')
    activities        = relationship('Activity', back_populates='group')
    clients           = relationship('Client',
                                secondary=lambda: schema_clients.ClientsGroups,
                                back_populates='groups')

    # redundant with same-as-RESTAPI-case
    groupName    = Column(String)
    loanCycle    = Column(Integer)
    creationDate = Column(DateTime)
    # redundant relationships camelCase
    assignedCentreKey = Column(String)
    assignedBranchKey = Column(String)
    assignedUserKey   = Column(String)
    customInformation = relationship('CustomFieldValue',
                                     back_populates = 'group',
                                     foreign_keys   = 'CustomFieldValue.parentkey',
                                     primaryjoin    = 'CustomFieldValue.parentkey == Group.encodedkey')

    def __repr__(self):
        return "<Group(id={}, groupname={})>".format(self.id, self.groupname)
