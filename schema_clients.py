"""Schema tables for Mambu Clients.

TODO: this are just very basic schemas for clients. A lot of fields
are missing.
"""

import schema_orm as orm
from schema_groups import Group
from schema_branches import Branch
from schema_addresses import Address

from sqlalchemy.orm import relationship
from sqlalchemy import Table, ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

dbname = orm.dbname
session = orm.session
Base = orm.Base

class Client(Base):
    """Client table.
    """
    __tablename__  = "client"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedKey             = Column(String) # this MUST be declared before primary_key
    encodedkey    = Column(String, primary_key=True)
    id            = Column(String, index=True, unique=True)
    firstname     = Column(String)
    middlename    = Column(String)
    lastname      = Column(String)
    gender        = Column(String)
    birthdate     = Column(DateTime)
    homephone     = Column(String)
    mobilephone1  = Column(String)
    emailaddress  = Column(String)
    state         = Column(String)
    loancycle     = Column(Integer)
    groups        = relationship(Group,
                                secondary=lambda: ClientsGroups,
                                back_populates='clients')

    # Relationships
    assignedbranchkey = Column(String, ForeignKey(Branch.encodedkey))
    branch            = relationship('Branch', back_populates='clients')
    addresses         = relationship('Address',
                                     back_populates = 'client',
                                     foreign_keys   = 'Address.parentkey',
                                     primaryjoin    = 'Address.parentkey == Client.encodedkey')
    custominformation = relationship('CustomFieldValue',
                                     back_populates = 'client',
                                     foreign_keys   = 'CustomFieldValue.parentkey',
                                     primaryjoin    = 'CustomFieldValue.parentkey == Client.encodedkey')
    loans             = relationship('LoanAccount',
                                     back_populates = 'holder_client',
                                     foreign_keys   = 'LoanAccount.accountholderkey',
                                     primaryjoin    = 'LoanAccount.accountholderkey == Client.encodedkey')
    activities        = relationship('Activity', back_populates='client')
    identificationdocuments = relationship('IdentificationDocument', back_populates='client')

    # redundant with same-as-RESTAPI-case
    firstName     = Column(String)
    middleName    = Column(String)
    lastName      = Column(String)
    birthDate     = Column(DateTime)
    homePhone     = Column(String)
    mobilePhone1  = Column(String)
    emailAddress  = Column(String)
    loanCycle     = Column(Integer)
    # redundant relationships camelCase
    assignedBranchKey = Column(String)
    customInformation = relationship('CustomFieldValue',
                                     back_populates = 'client',
                                     foreign_keys   = 'CustomFieldValue.parentkey',
                                     primaryjoin    = 'CustomFieldValue.parentkey == Client.encodedkey')
    identificationDocuments = relationship('IdentificationDocument', back_populates='client')

    @property
    def name(self):
        return "{}{} {}".format(self.firstname.strip(),(' '+self.middlename.strip()) if self.middlename else '',self.lastname.strip())

    def __repr__(self):
        return "<Client(id={}, name={})>".format(self.id, self.name)


ClientsGroups = Table('groupmember', Base.metadata,
    Column('clientkey', Integer, ForeignKey(Client.encodedkey), nullable=False, primary_key=True, doc='Reference to client'),
    Column('groupkey',  Integer, ForeignKey(Group.encodedkey),  nullable=False, primary_key=True, doc='Reference to group'),
    schema=dbname)


class IdentificationDocument(Base):
    """IdentificationDocument table.
    Related with client
    """
    __tablename__  = "identificationdocument"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    encodedKey          = Column(String) # this MUST be declared before primary_key
    encodedkey          = Column(String, primary_key=True)
    documentid          = Column(String)
    documenttype        = Column(String)
    indexinlist         = Column(Integer)
    issuingauthority    = Column(String)
    validuntil          = Column(DateTime)
    identificationdocumenttemplatekey   = Column(String)

    # Relationships
    clientkey = Column(String, ForeignKey(Client.encodedkey))
    client    = relationship(Client, back_populates='identificationdocuments')

    # redundant with same-as-RESTAPI-case
    documentId          = Column(String)
    documentType        = Column(String)
    indexInList         = Column(Integer)
    issuingAuthority    = Column(String)
    validUntil          = Column(DateTime)
    identificationDocumentTemplateKey   = Column(String)
    # redundant relationships camelCase
    clientKey = Column(String)

    def __repr__(self):
        return "<IdentificationDocument(documentid={})>".format(self.documentid)
