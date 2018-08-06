"""Schema table for Mambu Branches.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   Branch

.. todo:: this is just a basic schema for branches. Some fields
          are missing.
"""

import schema_orm as orm

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

dbname = orm.dbname
session = orm.session
Base = orm.Base

class Branch(Base):
    """Branch table.
    Related with client
    """
    __tablename__  = "branch"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedKey   = Column(String, primary_key=True)
    id           = Column(String, index=True, unique=True)
    name         = Column(String)
    notes        = Column(String)
    phoneNumber  = Column(String)
    emailAddress = Column(String)
    state        = Column(String)

    # Relationships
    addresses         = relationship('Address',
                                     back_populates = 'branch',
                                     foreign_keys   = 'Address.parentKey',
                                     primaryjoin    = 'Address.parentKey == Branch.encodedKey')
    customInformation = relationship('CustomFieldValue',
                                     back_populates = 'branch',
                                     foreign_keys   = 'CustomFieldValue.parentKey',
                                     primaryjoin    = 'CustomFieldValue.parentKey == Branch.encodedKey')
    loans             = relationship('LoanAccount', back_populates='branch')
    activities        = relationship('Activity', back_populates='branch')
    clients           = relationship('Client', back_populates='branch')
    groups            = relationship('Group', back_populates='branch')
    users             = relationship('User', back_populates='branch')

    def __repr__(self):
        return "<Branch(id={}, name={})>".format(self.id, self.name)
