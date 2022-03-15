"""Schema tables for Mambu Activities.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Numeric, String,
                        Table, Text)
from sqlalchemy.ext.hybrid import hybrid_property
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


class Task(Base):
    """Task table."""

    __tablename__ = "task"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    creationDate = Column(DateTime)
    completionDate = Column(DateTime)
    description = Column(Text)
    dueDate = Column(DateTime)
    id = Column(Integer)
    lastModifiedDate = Column(DateTime)
    status = Column(String)
    title = Column(String)
    taskLinkType = Column(String)

    # Relationships
    assignedUserKey = Column(String, ForeignKey(User.encodedKey))
    createdByUserKey = Column(String, ForeignKey(User.encodedKey))

    createdByUser = relationship(
        User,
        primaryjoin="User.encodedKey==Task.createdByUserKey",
        back_populates="createdTasks",
    )
    assignedUser = relationship(
        User,
        primaryjoin="User.encodedKey==Task.assignedUserKey",
        back_populates="assignedTasks",
    )

    taskLinkKey = Column(String)
    link_group = relationship(
        "Group",
        back_populates="tasks",
        foreign_keys="Task.taskLinkKey",
        primaryjoin="Task.taskLinkKey == Group.encodedKey",
    )
    link_loan = relationship(
        "LoanAccount",
        back_populates="tasks",
        foreign_keys="Task.taskLinkKey",
        primaryjoin="Task.taskLinkKey == LoanAccount.encodedKey",
    )

    @hybrid_property
    def daysUntilDue(self):
        """Days until due date"""
        diffDays = self.dueDate - datetime.now()
        return diffDays

    def __repr__(self):
        return "<Task(taskLinkType=%s, dueDate=%s)>" % (
            self.taskLinkType,
            self.dueDate.strftime("%Y%m%d"),
        )
