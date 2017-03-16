"""Schema tables for Mambu Custom fields.
"""

import schema_orm as orm

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer
from sqlalchemy.orm.exc import NoResultFound

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
    customfieldvalues= relationship('CustomFieldValue', back_populates='customfield')

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
    customfieldkey = Column(String, ForeignKey(CustomField.encodedkey))
    customfield    = relationship(CustomField, back_populates='customfieldvalues')
    loan           = relationship('LoanAccount',
                                  back_populates = 'custominformation',
                                  foreign_keys   = 'CustomFieldValue.parentkey',
                                  primaryjoin    = 'CustomFieldValue.parentkey == LoanAccount.encodedkey')
    client         = relationship('Client',
                                  back_populates = 'custominformation',
                                  foreign_keys   = 'CustomFieldValue.parentkey',
                                  primaryjoin    = 'CustomFieldValue.parentkey == Client.encodedkey')
    group          = relationship('Group',
                                  back_populates = 'custominformation',
                                  foreign_keys   = 'CustomFieldValue.parentkey',
                                  primaryjoin    = 'CustomFieldValue.parentkey == Group.encodedkey')
    user           = relationship('User',
                                  back_populates = 'custominformation',
                                  foreign_keys   = 'CustomFieldValue.parentkey',
                                  primaryjoin    = 'CustomFieldValue.parentkey == User.encodedkey')
    branch         = relationship('Branch',
                                  back_populates = 'custominformation',
                                  foreign_keys   = 'CustomFieldValue.parentkey',
                                  primaryjoin    = 'CustomFieldValue.parentkey == Branch.encodedkey')

    @property
    def linkedclient(self):
        from schema_clients import Client
        try:
            if self.customfield.datatype == 'CLIENT_LINK':
                return session.query(Client).filter(Client.encodedkey==self.linkedentitykeyvalue).one()
            else:
                return None
        except NoResultFound:
            return None

    @property
    def linkedgroup(self):
        from schema_groups import Group
        try:
            if self.customfield.datatype == 'GROUP_LINK':
                return session.query(Group).filter(Group.encodedkey==self.linkedentitykeyvalue).one()
            else:
                return None
        except NoResultFound:
            return None

    @property
    def linkeduser(self):
        from schema_users import User
        try:
            if self.customfield.datatype == 'USER_LINK':
                return session.query(User).filter(User.encodedkey==self.linkedentitykeyvalue).one()
            else:
                return None
        except NoResultFound:
            return None

    def __repr__(self):
        return "<CustomFieldValue(customfield={},value={})>".format(self.customfield, self.value if self.value else self.linkedclient if self.linkedclient else self.linkedgroup if self.linkedgroup else self.linkeduser if self.linkeduser else 'None')
