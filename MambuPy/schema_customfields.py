"""Schema tables for Mambu Custom fields.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   CustomField
   CustomFieldValue
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
    encodedKey       = Column(String, primary_key=True)
    name             = Column(String)
    description      = Column(String)
    id               = Column(String)
    type             = Column(String)
    state            = Column(String)
    valueLength      = Column(String)
    dataType         = Column(String)
    creationDate     = Column(DateTime)
    lastModifiedDate = Column(DateTime)
    customFieldValues= relationship('CustomFieldValue', back_populates='customField')

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
    encodedKey               = Column(String, primary_key=True)
    parentKey                = Column(String)
    indexInList              = Column(Integer)
    value                    = Column(String)
    linkedEntityKeyValue     = Column(String)
    amount                   = Column(Numeric(50,10))
    customFieldSetGroupIndex = Column(Integer)

    # Relationships
    customFieldKey = Column(String, ForeignKey(CustomField.encodedKey))
    customField    = relationship(CustomField, back_populates='customFieldValues')
    loan           = relationship('LoanAccount',
                                  back_populates = 'customInformation',
                                  foreign_keys   = 'CustomFieldValue.parentKey',
                                  primaryjoin    = 'CustomFieldValue.parentKey == LoanAccount.encodedKey')
    client         = relationship('Client',
                                  back_populates = 'customInformation',
                                  foreign_keys   = 'CustomFieldValue.parentKey',
                                  primaryjoin    = 'CustomFieldValue.parentKey == Client.encodedKey')
    group          = relationship('Group',
                                  back_populates = 'customInformation',
                                  foreign_keys   = 'CustomFieldValue.parentKey',
                                  primaryjoin    = 'CustomFieldValue.parentKey == Group.encodedKey')
    user           = relationship('User',
                                  back_populates = 'customInformation',
                                  foreign_keys   = 'CustomFieldValue.parentKey',
                                  primaryjoin    = 'CustomFieldValue.parentKey == User.encodedKey')
    branch         = relationship('Branch',
                                  back_populates = 'customInformation',
                                  foreign_keys   = 'CustomFieldValue.parentKey',
                                  primaryjoin    = 'CustomFieldValue.parentKey == Branch.encodedKey')

    @property
    def linkedclient(self):
        from schema_clients import Client
        try:
            if self.customField.dataType == 'CLIENT_LINK':
                return session.query(Client).filter(Client.encodedKey==self.linkedEntityKeyValue).one()
            else:
                return None
        except NoResultFound:
            return None

    @property
    def linkedgroup(self):
        from schema_groups import Group
        try:
            if self.customField.dataType == 'GROUP_LINK':
                return session.query(Group).filter(Group.encodedKey==self.linkedEntityKeyValue).one()
            else:
                return None
        except NoResultFound:
            return None

    @property
    def linkeduser(self):
        from schema_users import User
        try:
            if self.customField.dataType == 'USER_LINK':
                return session.query(User).filter(User.encodedKey==self.linkedEntityKeyValue).one()
            else:
                return None
        except NoResultFound:
            return None

    def __repr__(self):
        return "<CustomFieldValue(customField={},value={})>".format(self.customField, self.value if self.value else self.linkedclient if self.linkedclient else self.linkedgroup if self.linkedgroup else self.linkeduser if self.linkeduser else 'None')
