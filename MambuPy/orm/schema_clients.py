"""Schema tables for Mambu Clients.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

.. todo:: this are just very basic schemas for clients. A lot of fields
          are missing.
"""

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Numeric, String,
                        Table)
from sqlalchemy.orm import relationship

from . import schema_orm as orm
from .schema_addresses import Address
from .schema_branches import Branch
from .schema_groups import Group, GroupRoleName

dbname = orm.dbname
session = orm.session
Base = orm.Base


class Client(Base):
    """Client table."""

    __tablename__ = "client"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    id = Column(String, index=True, unique=True)
    firstName = Column(String)
    middleName = Column(String)
    lastName = Column(String)
    homePhone = Column(String)
    mobilePhone1 = Column(String)
    mobilePhone2 = Column(String)
    emailAddress = Column(String)
    gender = Column(String)
    state = Column(String)
    loanCycle = Column(Integer)
    birthDate = Column(DateTime)
    creationDate = Column(DateTime)
    activationDate = Column(DateTime)
    approvedDate = Column(DateTime)
    groups = relationship(
        Group, secondary=lambda: ClientsGroups, back_populates="clients"
    )

    # Relationships
    assignedBranchKey = Column(String, ForeignKey(Branch.encodedKey))
    branch = relationship("Branch", back_populates="clients")
    addresses = relationship(
        "Address",
        back_populates="client",
        foreign_keys="Address.parentKey",
        primaryjoin="Address.parentKey == Client.encodedKey",
    )
    customInformation = relationship(
        "CustomFieldValue",
        back_populates="client",
        foreign_keys="CustomFieldValue.parentKey",
        primaryjoin="CustomFieldValue.parentKey == Client.encodedKey",
    )
    loans = relationship(
        "LoanAccount",
        back_populates="holder_client",
        foreign_keys="LoanAccount.accountHolderKey",
        primaryjoin="LoanAccount.accountHolderKey == Client.encodedKey",
    )
    activities = relationship("Activity", back_populates="client")
    identificationDocuments = relationship(
        "IdentificationDocument", back_populates="client"
    )
    roles = relationship("GroupRole", back_populates="client")

    @property
    def name(self):
        return "{}{} {}".format(
            self.firstName.strip(),
            (" " + self.middleName.strip()) if self.middleName else "",
            self.lastName.strip(),
        )

    def __repr__(self):
        return "<Client(id={}, name={})>".format(self.id, self.name)


ClientsGroups = Table(
    "groupmember",
    Base.metadata,
    Column(
        "clientkey",
        Integer,
        ForeignKey(Client.encodedKey),
        nullable=False,
        primary_key=True,
        doc="Reference to client",
    ),
    Column(
        "groupkey",
        Integer,
        ForeignKey(Group.encodedKey),
        nullable=False,
        primary_key=True,
        doc="Reference to group",
    ),
    schema=dbname,
)


class GroupRole(Base):
    """GroupRole table.

    Association object for many-to-many relationship
    """

    __tablename__ = "grouprole"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    encodedKey = Column(String, primary_key=True)

    clientKey = Column(
        String, ForeignKey(Client.encodedKey), nullable=False, doc="Reference to client"
    )
    groupKey = Column(
        String, ForeignKey(Group.encodedKey), nullable=False, doc="Reference to group"
    )
    groupRoleNameKey = Column(
        String,
        ForeignKey(GroupRoleName.encodedKey),
        nullable=False,
        doc="Reference to role name",
    )

    client = relationship(Client, back_populates="roles")
    group = relationship(Group, back_populates="roles")
    roleName = relationship(GroupRoleName, back_populates="roles")

    @property
    def rolename(self):
        return self.roleName.name

    def __repr__(self):
        return "<GroupRole(name={}, client={}, group={})>".format(
            self.roleName, self.client, self.group
        )


class IdentificationDocument(Base):
    """IdentificationDocument table.
    Related with client
    """

    __tablename__ = "identificationdocument"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    encodedKey = Column(String, primary_key=True)
    documentId = Column(String)
    documentType = Column(String)
    indexInList = Column(Integer)
    issuingAuthority = Column(String)
    validUntil = Column(DateTime)
    identificationDocumentTemplateKey = Column(String)

    # Relationships
    clientKey = Column(String, ForeignKey(Client.encodedKey))
    client = relationship(Client, back_populates="identificationDocuments")

    def __repr__(self):
        return "<IdentificationDocument(documentId={})>".format(self.documentId)
