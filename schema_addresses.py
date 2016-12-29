"""Schema tables for Mambu Addresses.
"""

from mambupy import schema_orm as orm

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, ForeignKey
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
    encodedkey    = Column(String, primary_key=True)
    parentkey     = Column(String)
    city          = Column(String)
    country       = Column(String)
    line1         = Column(String)
    line2         = Column(String)
    postcode      = Column(String)
    region        = Column(String)

    def address(self):
        return "{}, {}, {}, {}, {}, {}".format(self.line1, self.line2, self.region, self.city, self.country, self.postcode)

    def __repr__(self):
        return "<Address(address={})>".format(self.address())
