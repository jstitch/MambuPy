"""Schema tables for Mambu Custom fields.
"""

from mambupy import schema_orm as orm

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

dbname = orm.dbname
session = orm.session
Base = orm.Base

class CustomField(Base):
    """CustomField table.
    Related with CustomFieldValue
    """
    __tablename__  = "customfield"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedkey       = Column(String, primary_key=True)
    name             = Column(String)
    description      = Column(String)
    id               = Column(String)
    type             = Column(String)
    valuelength      = Column(String)
    datatype         = Column(String)
    state            = Column(String)
    creationdate     = Column(DateTime)
    lastmodifieddate = Column(DateTime)

    def __repr__(self):
        return "<CustomField(name={})>".format(self.name)


class CustomFieldValue(Base):
    """CustomFieldValue table.
    """
    __tablename__  = "customfieldvalue"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedkey               = Column(String, primary_key=True)
    parentkey                = Column(String)
    indexinlist              = Column(Integer)
    value                    = Column(String)
    linkedentitykeyvalue     = Column(String)
    amount                   = Column(Numeric(50,10))
    customfieldsetgroupindex = Column(Integer)

    # Relationships
    customfieldkey           = Column(String, ForeignKey(CustomField.encodedkey))
    customfield              = relationship(CustomField, backref=backref('customfieldvalues'))

    def __repr__(self):
        return "<CustomFieldValue(customfield={},value={})>".format(self.customfield, self.value)
