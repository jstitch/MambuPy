"""Schema tables for Mambu Activities.
"""

import schema_orm as orm
from schema_branches import Branch
from schema_clients import Client
from schema_groups import Group
from schema_loans import LoanAccount
from schema_users import User

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

dbname = orm.dbname
session = orm.session
Base = orm.Base

class Activity(Base):
    """Activity table.
    """
    __tablename__  = "activity"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedKey                  = Column(String) # this MUST be declared before primary_key
    encodedkey                  = Column(String, primary_key=True)
    lineofcreditkey             = Column(String)
    centrekey                   = Column(String)
    loanproductkey              = Column(String)
    savingsaccountkey           = Column(String)
    savingsproductkey           = Column(String)
    assignedcentrekey           = Column(String)
    taskkey                     = Column(String)
    glaccountkey                = Column(String)
    glaccountsclosurekey        = Column(String)
    entitykey                   = Column(String)
    parent_key                  = Column(String)

    transactionid               = Column(Integer)
    timestamp                   = Column(DateTime)
    entitytype                  = Column(String)
    notes                       = Column(String)
    type                        = Column(String)
    fieldchangename             = Column(String)
    activitychanges_integer_idx = Column(Integer)

    # Relationships
    loanaccountkey              = Column(String, ForeignKey(LoanAccount.encodedkey))
    branchkey                   = Column(String, ForeignKey(Branch.encodedkey))
    clientkey                   = Column(String, ForeignKey(Client.encodedkey))
    groupkey                    = Column(String, ForeignKey(Group.encodedkey))
    userkey                     = Column(String, ForeignKey(User.encodedkey))
    assigneduserkey             = Column(String, ForeignKey(User.encodedkey))

    loan                        = relationship(LoanAccount, back_populates='activities')
    branch                      = relationship(Branch, back_populates='activities')
    client                      = relationship(Client, back_populates='activities')
    group                       = relationship(Group, back_populates='activities')
    user                        = relationship(User,
                                               primaryjoin    = 'User.encodedkey==Activity.userkey',
                                               back_populates = 'activities')
    assigneduser                = relationship(User,
                                               primaryjoin    = 'User.encodedkey==Activity.assigneduserkey',
                                               back_populates = 'assignedactivities')

    # redundant with same-as-RESTAPI-case
    lineOfCreditKey             = Column(String)
    centreKey                   = Column(String)
    loanProductKey              = Column(String)
    savingsAccountKey           = Column(String)
    savingsProductKey           = Column(String)
    assignedCentreKey           = Column(String)
    taskKey                     = Column(String)
    glAccountKey                = Column(String)
    glAccountsClosureKey        = Column(String)
    entityKey                   = Column(String)
    transactionId               = Column(Integer)
    entityType                  = Column(String)
    fieldChangeName             = Column(String)
    activityChanges_integer_idx = Column(Integer)
    # redundant relationships camelCase
    loanAccountKey              = Column(String)
    branchKey                   = Column(String)
    clientKey                   = Column(String)
    groupKey                    = Column(String)
    userKey                     = Column(String)
    assignedUserKey             = Column(String)
    assignedUser                = relationship(User,
                                               primaryjoin    = 'User.encodedkey==Activity.assigneduserkey',
                                               back_populates = 'assignedactivities')

    def __repr__(self):
        return "<Activity(type=%s, timestamp=%s)>" % (self.type, self.timestamp.strftime('%Y%m%d'))
