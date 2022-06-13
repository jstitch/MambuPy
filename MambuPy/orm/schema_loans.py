"""Schema tables for Mambu Loan Accounts.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

.. todo:: this are just very basic schemas for loan tables. A lot of fields
          are missing.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from . import schema_orm as orm
from .schema_branches import Branch
from .schema_users import User

dbname = orm.dbname
session = orm.session
Base = orm.Base


class LoanProduct(Base):
    """LoanProduct table."""

    __tablename__ = "loanproduct"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    id = Column(String, index=True, unique=True)
    productName = Column(String)  # redundant with same-as-RESTAPI-case
    activated = Column(Integer)
    loans = relationship("LoanAccount", back_populates="product")

    def __repr__(self):
        return "<LoanProduct(id=%s, name=%s)>" % (self.id, self.productName)


class DisbursementDetails(Base):
    """DisbursementDetails table."""

    __tablename__ = "disbursementdetails"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    expectedDisbursementDate = Column(DateTime)
    disbursementDate = Column(DateTime)
    firstRepaymentDate = Column(DateTime)

    def __repr__(self):
        return "<DisbursementDetails(disbursementDate=%s)>" % (self.disbursementDate)


class LoanAccount(Base):
    """LoanAccount table."""

    __tablename__ = "loanaccount"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    id = Column(String, index=True, unique=True)
    accountState = Column(String)
    accountSubstate = Column(String)  # not in API
    loanAmount = Column(Numeric(50, 10))
    notes = Column(String)
    principalBalance = Column(Numeric(50, 10))
    principalPaid = Column(Numeric(50, 10))
    principalDue = Column(Numeric(50, 10))
    interestBalance = Column(Numeric(50, 10))
    interestPaid = Column(Numeric(50, 10))
    interestDue = Column(Numeric(50, 10))
    interestRate = Column(Numeric(50, 10))
    interestCalculationMethod = Column(String)
    interestBalanceCalculationMethod = Column(String)
    repaymentInstallments = Column(Integer)
    repaymentPeriodUnit = Column(String)
    repaymentPeriodCount = Column(Integer)
    accountHolderType = Column(String)
    feesBalance = Column(Numeric(50, 10))
    feesPaid = Column(Numeric(50, 10))
    feesDue = Column(Numeric(50, 10))
    penaltyBalance = Column(Numeric(50, 10))
    penaltyPaid = Column(Numeric(50, 10))
    penaltyDue = Column(Numeric(50, 10))
    creationDate = Column(DateTime)
    approvedDate = Column(DateTime)
    closedDate = Column(DateTime)
    rescheduledAccountKey = Column(String)
    assignedCentreKey = Column(String)  # not in API
    lastSetToArrearsDate = Column(DateTime)  # not in API

    # Relationships
    productTypeKey = Column(String, ForeignKey(LoanProduct.encodedKey))
    product = relationship("LoanProduct", back_populates="loans")
    disbursementDetailsKey = Column(String, ForeignKey(DisbursementDetails.encodedKey))
    disbursementDetails = relationship("DisbursementDetails")
    assignedBranchKey = Column(String, ForeignKey(Branch.encodedKey))
    branch = relationship("Branch", back_populates="loans")
    assignedUserKey = Column(String, ForeignKey(User.encodedKey))
    user = relationship("User", back_populates="loans")
    accountHolderKey = Column(String)
    holder_group = relationship(
        "Group",
        back_populates="loans",
        foreign_keys="LoanAccount.accountHolderKey",
        primaryjoin="LoanAccount.accountHolderKey == Group.encodedKey",
    )
    holder_client = relationship(
        "Client",
        back_populates="loans",
        foreign_keys="LoanAccount.accountHolderKey",
        primaryjoin="LoanAccount.accountHolderKey == Client.encodedKey",
    )
    customInformation = relationship(
        "CustomFieldValue",
        back_populates="loan",
        foreign_keys="CustomFieldValue.parentKey",
        primaryjoin="CustomFieldValue.parentKey == LoanAccount.encodedKey",
    )
    tasks = relationship(
        "Task",
        back_populates="link_loan",
        foreign_keys="Task.taskLinkKey",
        primaryjoin="Task.taskLinkKey == LoanAccount.encodedKey",
    )
    activities = relationship("Activity", back_populates="loan")
    repayments = relationship("Repayment", back_populates="account")
    transactions = relationship("LoanTransaction", back_populates="account")

    def __repr__(self):
        return "<LoanAccount(id=%s, accountState=%s)>" % (self.id, self.accountState)


class Repayment(Base):
    """Repayment table."""

    __tablename__ = "repayment"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    dueDate = Column(DateTime, index=True)
    principalDue = Column(Numeric(50, 10))
    principalPaid = Column(Numeric(50, 10))
    interestDue = Column(Numeric(50, 10))
    interestPaid = Column(Numeric(50, 10))
    feesDue = Column(Numeric(50, 10))
    feesPaid = Column(Numeric(50, 10))
    penaltyDue = Column(Numeric(50, 10))
    penaltyPaid = Column(Numeric(50, 10))
    repaidDate = Column(DateTime)
    lastPaidDate = Column(DateTime)
    state = Column(String, index=True)

    # Relationships
    parentAccountKey = Column(String, ForeignKey(LoanAccount.encodedKey))
    account = relationship(
        "LoanAccount", back_populates="repayments", order_by="Repayment.dueDate"
    )

    def __repr__(self):
        return "<Repayment(dueDate=%s, state=%s,\naccount=%s)>" % (
            self.dueDate.strftime("%Y%m%d"),
            self.state,
            self.account,
        )


class TransactionChannel(Base):
    """TransactionChannel table."""

    __tablename__ = "transactionchannel"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    id = Column(String)
    name = Column(String)

    def __repr__(self):
        return "<TransactionChannel(name=%s)>" % (self.name)


class TransactionDetails(Base):
    """TransactionDetails table."""

    __tablename__ = "transactiondetails"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)

    # Relationships
    transactionChannelKey = Column(String, ForeignKey(TransactionChannel.encodedKey))
    transactionChannel = relationship("TransactionChannel")

    def __repr__(self):
        return "<TransactionDetails(TransactionChannel=%s)>" % (self.transactionChannel)


class LoanTransaction(Base):
    """LoanTransaction table."""

    __tablename__ = "loantransaction"
    __table_args__ = {"schema": dbname, "keep_existing": True}

    # Columns
    encodedKey = Column(String, primary_key=True)
    transactionId = Column(Integer, index=True)
    creationDate = Column(DateTime)
    entryDate = Column(DateTime)
    principalAmount = Column(Numeric(50, 10))
    interestAmount = Column(Numeric(50, 10))
    feesAmount = Column(Numeric(50, 10))
    penaltyAmount = Column(Numeric(50, 10))
    reversalTransactionKey = Column(String)
    amount = Column(Numeric(50, 10))
    type = Column(String)
    comment = Column(String)

    # Relationships
    parentAccountKey = Column(String, ForeignKey(LoanAccount.encodedKey))
    account = relationship(
        "LoanAccount",
        back_populates="transactions",
        order_by="LoanTransaction.transactionId",
    )
    details_encodedkey_oid = Column(String, ForeignKey(TransactionDetails.encodedKey))
    transactionDetails = relationship("TransactionDetails")

    def __repr__(self):
        return "<LoanTransaction(transactionId=%s, amount=%s, creationDate=%s, entryDate=%s, type=%s, comment='%s',\
 reversed=%s\naccount=%s)>" % (
            self.transactionId,
            self.amount,
            self.creationDate.strftime("%Y%m%d"),
            self.entryDate.strftime("%Y%m%d"),
            self.type,
            self.comment,
            "Yes" if self.reversalTransactionKey else "No",
            self.account,
        )
