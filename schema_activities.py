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

    loan                        = relationship(LoanAccount, backref=backref('activities'))
    branch                      = relationship(Branch, backref=backref('activities'))
    client                      = relationship(Client, backref=backref('activities'))
    group                       = relationship(Group, backref=backref('activities'))
    user                        = relationship(User, primaryjoin="User.encodedkey==Activity.userkey", backref=backref('activities'))
    assigneduser                = relationship(User, primaryjoin="User.encodedkey==Activity.assigneduserkey", backref=backref('assignedactivities'))

    def __repr__(self):
        return "<Activity(type=%s, timestamp=%s)>" % (self.type, self.timestamp.strftime('%Y%m%d'))
