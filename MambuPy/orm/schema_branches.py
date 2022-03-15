"""Schema table for Mambu Branches.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

.. todo:: this is just a basic schema for branches. Some fields
          are missing.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from . import schema_orm as orm

dbname = orm.dbname
session = orm.session
Base = orm.Base


class Branch(Base):
    """Branch table.
    Related with client
    """

    __tablename__ = "branch"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    id = Column(String, index=True, unique=True)
    name = Column(String)
    notes = Column(String)
    phoneNumber = Column(String)
    emailAddress = Column(String)
    state = Column(String)
    creationDate = Column(DateTime)
    lastModifiedDate = Column(DateTime)

    # Relationships
    addresses = relationship(
        "Address",
        back_populates="branch",
        foreign_keys="Address.parentKey",
        primaryjoin="Address.parentKey == Branch.encodedKey",
    )
    customInformation = relationship(
        "CustomFieldValue",
        back_populates="branch",
        foreign_keys="CustomFieldValue.parentKey",
        primaryjoin="CustomFieldValue.parentKey == Branch.encodedKey",
    )
    loans = relationship("LoanAccount", back_populates="branch")
    activities = relationship("Activity", back_populates="branch")
    clients = relationship("Client", back_populates="branch")
    groups = relationship("Group", back_populates="branch")
    users = relationship("User", back_populates="branch")
    centres = relationship("Centre", back_populates="branch")

    def __repr__(self):
        return "<Branch(id={}, name={})>".format(self.id, self.name)
