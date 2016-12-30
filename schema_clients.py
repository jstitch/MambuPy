"""Schema tables for Mambu Clients.

TODO: this are just very basic schemas for clients. A lot of fields
are missing.
"""

from mambupy import schema_orm as orm
from mambupy.schema_groups import Group
from mambupy.schema_branches import Branch
from mambupy.schema_addresses import Address
from mambupy.schema_customfields import CustomFieldValue

from sqlalchemy.orm import relationship, backref
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
                                backref=backref('clients'))


    # Relationships
    assignedbranchkey = Column(String, ForeignKey(Branch.encodedkey))
    branch            = relationship(Branch, backref=backref('clients'))
    addresses         = relationship(Address,
                                     backref=backref('client'),
                                     foreign_keys=[Address.parentkey],
                                     primaryjoin='Address.parentkey == Client.encodedkey')
    custominformation = relationship(CustomFieldValue,
                                     backref=backref('client'),
                                     foreign_keys=[CustomFieldValue.parentkey],
                                     primaryjoin='CustomFieldValue.parentkey == Client.encodedkey')

    def name(self):
        return "{}{} {}".format(self.firstname,(' '+self.middlename) if self.middlename else '',self.lastname)

    def __repr__(self):
        return "<Client(id={}, name={})>".format(self.id, self.name())


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

    encodedkey          = Column(String, primary_key=True)
    documentid          = Column(String)
    documenttype        = Column(String)
    indexinlist         = Column(Integer)
    issuingauthority    = Column(String)
    validuntil          = Column(DateTime)
    identificationdocumenttemplatekey   = Column(String)

    # Relationships
    clientkey = Column(String, ForeignKey(Client.encodedkey))
    client    = relationship(Client, backref=backref('identificationdocuments'))

    def __repr__(self):
        return "<IdentificationDocument(documentid={})>".format(self.documentid)
