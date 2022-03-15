"""Schema tables for Mambu Users.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

.. todo:: this are just very basic schemas for users.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from . import schema_orm as orm
from .schema_branches import Branch

dbname = orm.dbname
session = orm.session
Base = orm.Base


class Role(Base):
    """Role table.
    Related with user
    """

    __tablename__ = "role"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    name = Column(String)
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return "<Role(name={})>".format(self.name)


class User(Base):
    """User table."""

    __tablename__ = "user"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    id = Column(String, index=True, unique=True)
    firstName = Column(String)
    lastName = Column(String)
    userName = Column(String)
    homePhone = Column(String)
    mobilePhone1 = Column(String)
    userState = Column(String)
    email = Column(String)
    creationDate = Column(DateTime)
    isCreditOfficer = Column(Integer)

    # Relationships
    assignedBranchKey = Column(String, ForeignKey(Branch.encodedKey))
    branch = relationship(Branch, back_populates="users")

    role_encodedKey_oid = Column(String, ForeignKey(Role.encodedKey))
    role = relationship(Role, back_populates="users")

    customInformation = relationship(
        "CustomFieldValue",
        back_populates="user",
        foreign_keys="CustomFieldValue.parentKey",
        primaryjoin="CustomFieldValue.parentKey == User.encodedKey",
    )
    activities = relationship(
        "Activity",
        primaryjoin="User.encodedKey==Activity.userKey",
        back_populates="user",
    )
    assignedActivities = relationship(
        "Activity",
        primaryjoin="User.encodedKey==Activity.assignedUserKey",
        back_populates="assignedUser",
    )
    createdTasks = relationship(
        "Task",
        primaryjoin="User.encodedKey==Task.createdByUserKey",
        back_populates="createdByUser",
    )
    assignedTasks = relationship(
        "Task",
        primaryjoin="User.encodedKey==Task.assignedUserKey",
        back_populates="assignedUser",
    )
    groups = relationship("Group", back_populates="user")
    loans = relationship("LoanAccount", back_populates="user")

    @property
    def name(self):
        return "{} {}".format(self.firstName, self.lastName)

    def __repr__(self):
        return "<User(id={}, name={})>".format(self.id, self.name)
