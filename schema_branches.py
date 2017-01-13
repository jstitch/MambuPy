"""Schema table for Mambu Branches.

TODO: this is just a basic schema for branches. Some fields
are missing.
"""

import schema_orm as orm
from schema_addresses import Address
from schema_customfields import CustomFieldValue

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, ForeignKey
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
    encodedkey   = Column(String, primary_key=True)
    id           = Column(String, index=True, unique=True)
    name         = Column(String)
    notes        = Column(String)
    phonenumber  = Column(String)
    emailaddress = Column(String)

    # Relationships
    addresses         = relationship(Address,
                                     backref=backref('branch'),
                                     foreign_keys=[Address.parentkey],
                                     primaryjoin='Address.parentkey == Branch.encodedkey')
    custominformation = relationship(CustomFieldValue,
                                     backref=backref('branch'),
                                     foreign_keys=[CustomFieldValue.parentkey],
                                     primaryjoin='CustomFieldValue.parentkey == Branch.encodedkey')

    def __repr__(self):
        return "<Branch(id={}, name={})>".format(self.id, self.name)
