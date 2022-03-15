"""Schema tables for Mambu Activities.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Numeric, String,
                        Table)
from sqlalchemy.orm import backref, relationship

from . import schema_orm as orm
from .schema_branches import Branch
from .schema_clients import Client
from .schema_groups import Group
from .schema_loans import LoanAccount
from .schema_users import User

dbname = orm.dbname
session = orm.session
Base = orm.Base


class Activity(Base):
    """Activity table."""

    __tablename__ = "activity"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    lineOfCreditKey = Column(String)
    centreKey = Column(String)
    loanProductKey = Column(String)
    savingsAccountKey = Column(String)
    savingsProductKey = Column(String)
    assignedCentreKey = Column(String)
    taskKey = Column(String)
    glAccountKey = Column(String)
    glAccountsClosureKey = Column(String)
    entityKey = Column(String)
    transactionId = Column(Integer)
    entityType = Column(String)
    parent_key = Column(String)
    fieldChangeName = Column(String)
    activityChanges_integer_idx = Column(Integer)

    timestamp = Column(DateTime)
    notes = Column(String)
    type = Column(String)

    # Relationships
    loanAccountKey = Column(String, ForeignKey(LoanAccount.encodedKey))
    branchKey = Column(String, ForeignKey(Branch.encodedKey))
    clientKey = Column(String, ForeignKey(Client.encodedKey))
    groupKey = Column(String, ForeignKey(Group.encodedKey))
    userKey = Column(String, ForeignKey(User.encodedKey))
    assignedUserKey = Column(String, ForeignKey(User.encodedKey))

    loan = relationship(LoanAccount, back_populates="activities")
    branch = relationship(Branch, back_populates="activities")
    client = relationship(Client, back_populates="activities")
    group = relationship(Group, back_populates="activities")
    user = relationship(
        User,
        primaryjoin="User.encodedKey==Activity.userKey",
        back_populates="activities",
    )
    assignedUser = relationship(
        User,
        primaryjoin="User.encodedKey==Activity.assignedUserKey",
        back_populates="assignedActivities",
    )
    fieldChanges = relationship("FieldChangeItem", back_populates="activity")

    def __repr__(self):
        return "<Activity(type=%s, timestamp=%s)>" % (
            self.type,
            self.timestamp.strftime("%Y%m%d"),
        )


class FieldChangeItem(Base):
    """Fieldchangeitem table."""

    __tablename__ = "fieldchangeitem"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    id = Column(String, primary_key=True)
    fieldChangeName = Column(String)
    fieldDetailName = Column(String)
    fieldDetailKey = Column(String)
    newValue = Column(String)
    originalValue = Column(String)
    fieldchanges_integer_idx = Column(Integer)

    # Relationships
    fieldchanges_encodedkey_own = Column(String, ForeignKey(Activity.encodedKey))
    activity = relationship(Activity, back_populates="fieldChanges")

    def __repr__(self):
        return (
            "<FieldChangeItem(newValue=%s, originalValue=%s, fieldChangeName=%s)>"
            % (self.originalValue, self.newValue, self.fieldChangeName)
        )
