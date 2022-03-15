"""Schema table for Mambu Branches.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

.. todo:: this is just a basic schema for centres. Some fields
          are missing.
"""

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from . import schema_orm as orm
from .schema_branches import Branch

dbname = orm.dbname
session = orm.session
Base = orm.Base


class Centre(Base):
    """Centre table.
    Related with client
    """

    __tablename__ = "centre"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    id = Column(String, index=True, unique=True)
    name = Column(String)
    notes = Column(String)
    state = Column(String)
    creationDate = Column(DateTime)
    lastModifiedDate = Column(DateTime)

    # Relationships
    assignedBranchKey = Column(String, ForeignKey(Branch.encodedKey))
    branch = relationship(Branch, back_populates="centres")
    groups = relationship("Group", back_populates="centre")

    def __repr__(self):
        return "<Centre(id={}, name={})>".format(self.id, self.name)
