"""Schema tables for Mambu Clients.

TODO: this are just very basic schemas for clients. A lot of fields
are missing.
"""

from mambuutil import connectDb, dbname
from mambupy.schema_groups import Group

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import Table, ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

engine = connectDb()
"""Database engine, connecting with default parameters by default.
"""

Session = sessionmaker(bind=engine)
"""Sessionmaker object.
"""

session = Session()
"""Default session created here.
"""

Base = declarative_base()
"""Declarative base for models.
"""


class ClientBranch(Base):
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

    def __repr__(self):
        return "<Branch(id={}, name={})>".format(self.id, self.name)


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
    groups        = relationship(Group,
                                secondary=lambda: ClientsGroups)


    # Relationships
    assignedbranchkey = Column(String, ForeignKey(ClientBranch.encodedkey))
    branch            = relationship('ClientBranch', backref=backref('clients'))

    def name(self):
        return "{}{} {}".format(self.firstname,(' '+self.middlename) if self.middlename else '',self.lastname)

    def __repr__(self):
        return "<Client(id={}, name={})>".format(self.id, self.name())


ClientsGroups = Table('groupmember', Base.metadata,
    Column('clientkey', Integer, ForeignKey(Client.encodedkey), nullable=False, primary_key=True, doc='Reference to client'),
    Column('groupkey',  Integer, ForeignKey(Group.encodedkey),  nullable=False, primary_key=True, doc='Reference to group'),
    schema=dbname)


class ClientAddress(Base):
    """Adress table.
    Related with client
    """
    __tablename__  = "address"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedkey = Column(String, primary_key=True)
    line1      = Column(String)
    line2      = Column(String)
    region     = Column(String)
    city       = Column(String)
    country    = Column(String)
    postcode   = Column(String)

    # Relationships
    parentkey = Column(String, ForeignKey(Client.encodedkey))
    client    = relationship('Client', backref=backref('addresses'))

    def address(self):
        return "{}, {}, {}, {}, {}, {}".format(self.line1, self.line2, self.region, self.city, self.country, self.postcode)

    def __repr__(self):
        return "<Address(address={})>".format(self.address())
