"""Schema tables for Mambu Addresses.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   Address
"""

import schema_orm as orm

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

dbname = orm.dbname
session = orm.session
Base = orm.Base

class Address(Base):
    """Adress table.
    """
    __tablename__  = "address"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedKey    = Column(String, primary_key=True)
    parentKey     = Column(String) # redundant with same-as-RESTAPI-case
    city          = Column(String)
    country       = Column(String)
    line1         = Column(String)
    line2         = Column(String)
    postcode      = Column(String)
    region        = Column(String)

    client        = relationship('Client',
                                 back_populates = 'addresses',
                                 foreign_keys   = 'Address.parentKey',
                                 primaryjoin    = 'Address.parentKey == Client.encodedKey')
    branch        = relationship('Branch',
                                 back_populates = 'addresses',
                                 foreign_keys   = 'Address.parentKey',
                                 primaryjoin    = 'Address.parentKey == Branch.encodedKey')
    group         = relationship('Group',
                                 back_populates = 'addresses',
                                 foreign_keys   = 'Address.parentKey',
                                 primaryjoin    = 'Address.parentKey == Group.encodedKey')

    @property
    def address(self):
        return "{}, {}, {}, {}, {}, {}".format(self.line1, self.line2, self.region, self.city, self.country, self.postcode)

    def __repr__(self):
        return "<Address(address={})>".format(self.address)
