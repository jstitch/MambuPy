"""Schema tables for Mambu Loan Accounts.

TODO: this are just very basic schemas for loan tables. A lot of fields
are missing.
"""

import schema_orm as orm

from schema_branches import Branch
from schema_users import User

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

dbname = orm.dbname
session = orm.session
Base = orm.Base

class LoanProduct(Base):
    """LoanProduct table.
    """
    __tablename__  = "loanproduct"
    __table_args__ = {'schema'        : dbname,
                      'keep_existing' : True
                     }

    # Columns
    encodedKey     = Column(String) # this MUST be declared before primary_key
    encodedkey     = Column(String, primary_key=True)
    id             = Column(String, index=True, unique=True)
    productname    = Column(String)
    productName    = Column(String) # redundant with same-as-RESTAPI-case
    activated      = Column(Integer)
    loans          = relationship('LoanAccount', back_populates='product')

    def __repr__(self):
        return "<LoanProduct(id=%s, name=%s)>" % (self.id, self.productname)


class DisbursementDetails(Base):
    """DisbursementDetails table.
    """
    __tablename__            = "disbursementdetails"
    __table_args__           = {'schema'        : dbname,
                                'keep_existing' : True
                               }

    # Columns
    encodedKey               = Column(String) # this MUST be declared before primary_key
    encodedkey               = Column(String, primary_key=True)
    expecteddisbursementdate = Column(DateTime)
    disbursementdate         = Column(DateTime)
    firstrepaymentdate       = Column(DateTime)

    # redundant with same-as-RESTAPI-case
    expectedDisbursementDate = Column(DateTime)
    disbursementDate         = Column(DateTime)
    firstRepaymentDate       = Column(DateTime)

    def __repr__(self):
        return "<DisbursementDetails(disbursementdate=%s)>" % (self.disbursementdate)


class LoanAccount(Base):
    """LoanAccount table.
    """
    __tablename__          = "loanaccount"
    __table_args__         = {'schema'        : dbname,
                              'keep_existing' : True
                             }

    # Columns
    encodedKey             = Column(String) # this MUST be declared before primary_key
    encodedkey             = Column(String, primary_key=True)
    id                     = Column(String, index=True, unique=True)
    accountstate           = Column(String)
    accountsubstate        = Column(String)
    loanamount             = Column(Numeric(50,10))
    notes                  = Column(String)
    principalbalance       = Column(Numeric(50,10))
    principalpaid          = Column(Numeric(50,10))
    principaldue           = Column(Numeric(50,10))
    interestbalance        = Column(Numeric(50,10))
    interestpaid           = Column(Numeric(50,10))
    interestdue            = Column(Numeric(50,10))
    interestrate           = Column(Numeric(50,10))
    interestcalculationmethod        = Column(String)
    interestbalancecalculationmethod = Column(String)
    repaymentinstallments  = Column(Integer)
    repaymentperiodunit    = Column(String)
    repaymentperiodcount   = Column(Integer)
    accountholdertype      = Column(String)
    feesbalance            = Column(Numeric(50,10))
    feespaid               = Column(Numeric(50,10))
    feesdue                = Column(Numeric(50,10))
    penaltybalance         = Column(Numeric(50,10))
    penaltypaid            = Column(Numeric(50,10))
    penaltydue             = Column(Numeric(50,10))
    creationdate           = Column(DateTime)
    approveddate           = Column(DateTime)
    closeddate             = Column(DateTime)
    assignedcentrekey      = Column(String)
    lastsettoarrearsdate   = Column(DateTime)

    # Relationships
    producttypekey         = Column(String, ForeignKey(LoanProduct.encodedkey))
    product                = relationship('LoanProduct', back_populates='loans')
    disbursementdetailskey = Column(String, ForeignKey(DisbursementDetails.encodedkey))
    disbursementdetails    = relationship('DisbursementDetails')
    assignedbranchkey      = Column(String, ForeignKey(Branch.encodedkey))
    branch                 = relationship('Branch', back_populates = 'loans')
    assigneduserkey        = Column(String, ForeignKey(User.encodedkey))
    user                   = relationship('User', back_populates = 'loans')
    accountholderkey       = Column(String)
    holder_group           = relationship('Group',
                                          back_populates = 'loans',
                                          foreign_keys   = 'LoanAccount.accountholderkey',
                                          primaryjoin    = 'LoanAccount.accountholderkey == Group.encodedkey')
    holder_client          = relationship('Client',
                                          back_populates = 'loans',
                                          foreign_keys   = 'LoanAccount.accountholderkey',
                                          primaryjoin    = 'LoanAccount.accountholderkey == Client.encodedkey')
    custominformation      = relationship('CustomFieldValue',
                                          back_populates = 'loan',
                                          foreign_keys   = 'CustomFieldValue.parentkey',
                                          primaryjoin    = 'CustomFieldValue.parentkey == LoanAccount.encodedkey')
    activities             = relationship('Activity', back_populates='loan')
    repayments             = relationship('Repayment', back_populates='account')
    transactions           = relationship('LoanTransaction', back_populates='account')

    # redundant with same-as-RESTAPI-case
    accountState           = Column(String)
    accountSubstate        = Column(String) # redundant camelCase not in API
    loanAmount             = Column(Numeric(50,10))
    principalBalance       = Column(Numeric(50,10))
    principalPaid          = Column(Numeric(50,10))
    principalDue           = Column(Numeric(50,10))
    interestBalance        = Column(Numeric(50,10))
    interestPaid           = Column(Numeric(50,10))
    interestDue            = Column(Numeric(50,10))
    interestRate           = Column(Numeric(50,10))
    interestCalculationMethod        = Column(String)
    interestBalanceCalculationMethod = Column(String)
    repaymentInstallments  = Column(Integer)
    repaymentPeriodUnit    = Column(String)
    repaymentPeriodCount   = Column(Integer)
    accountHolderType      = Column(String)
    feesBalance            = Column(Numeric(50,10))
    feesPaid               = Column(Numeric(50,10))
    feesDue                = Column(Numeric(50,10))
    penaltyBalance         = Column(Numeric(50,10))
    penaltyPaid            = Column(Numeric(50,10))
    penaltyDue             = Column(Numeric(50,10))
    creationDate           = Column(DateTime)
    approvedDate           = Column(DateTime)
    closedDate             = Column(DateTime)
    assignedCentreKey      = Column(String) # redundant camelCase not in API
    lastSetToArrearsDate   = Column(DateTime) # redundant camelCase not in API
    # redundant relationships camelCase
    productTypeKey         = Column(String)
    disbursementDetailsKey = Column(String)
    disbursementDetails    = relationship('DisbursementDetails')
    assignedBranchKey      = Column(String)
    assignedUserKey        = Column(String)
    accountHolderKey       = Column(String)
    customInformation      = relationship('CustomFieldValue',
                                          back_populates = 'loan',
                                          foreign_keys   = 'CustomFieldValue.parentkey',
                                          primaryjoin    = 'CustomFieldValue.parentkey == LoanAccount.encodedkey')

    def __repr__(self):
        return "<LoanAccount(id=%s, accountstate=%s)>" % (self.id, self.accountstate)


class Repayment(Base):
    """Repayment table.
    """
    __tablename__    = "repayment"
    __table_args__   = {'schema'        : dbname,
                        'keep_existing' : True
                       }

    # Columns
    # encodedKey MUST be declared before primary_key
    encodedKey       = Column(String)
    encodedkey       = Column(String, primary_key=True)
    duedate          = Column(DateTime, index=True)
    state            = Column(String, index=True)
    principaldue     = Column(Numeric(50,10))
    principalpaid    = Column(Numeric(50,10))
    interestdue      = Column(Numeric(50,10))
    interestpaid     = Column(Numeric(50,10))
    feesdue          = Column(Numeric(50,10))
    feespaid         = Column(Numeric(50,10))
    penaltydue       = Column(Numeric(50,10))
    penaltypaid      = Column(Numeric(50,10))

    # Relationships
    parentaccountkey = Column(String, ForeignKey(LoanAccount.encodedkey))
    account          = relationship('LoanAccount',
                                    back_populates='repayments',
                                    order_by='Repayment.duedate')
    # redundant with same-as-RESTAPI-case
    dueDate          = Column(DateTime, index=True)
    principalDue     = Column(Numeric(50,10))
    principalPaid    = Column(Numeric(50,10))
    interestDue      = Column(Numeric(50,10))
    interestPaid     = Column(Numeric(50,10))
    feesDue          = Column(Numeric(50,10))
    feesPaid         = Column(Numeric(50,10))
    penaltyDue       = Column(Numeric(50,10))
    penaltyPaid      = Column(Numeric(50,10))
    repaidDate       = Column(DateTime)
    # redundant relationships camelCase
    parentAccountKey = Column(String)

    def __repr__(self):
        return "<Repayment(duedate=%s, state=%s,\naccount=%s)>" % (self.duedate.strftime('%Y%m%d'), self.state, self.account)


class LoanTransaction(Base):
    """LoanTransaction table.
    """
    __tablename__          = "loantransaction"
    __table_args__         = {'schema'        : dbname,
                              'keep_existing' : True
                             }

    # Columns
    encodedKey             = Column(String) # this MUST be declared before primary_key
    encodedkey             = Column(String, primary_key=True)
    transactionid          = Column(Integer, index=True)
    amount                 = Column(Numeric(50,10))
    creationdate           = Column(DateTime)
    entrydate              = Column(DateTime)
    type                   = Column(String)
    principalamount        = Column(Numeric(50,10))
    interestamount         = Column(Numeric(50,10))
    feesamount             = Column(Numeric(50,10))
    penaltyamount          = Column(Numeric(50,10))
    reversaltransactionkey = Column(String)
    comment                = Column(String)

    # Relationships
    parentaccountkey       = Column(String, ForeignKey(LoanAccount.encodedkey))
    account                = relationship('LoanAccount',
                                          back_populates='transactions',
                                          order_by='LoanTransaction.transactionid')
    # redundant with same-as-RESTAPI-case
    transactionId          = Column(Integer, index=True)
    creationDate           = Column(DateTime)
    entryDate              = Column(DateTime)
    principalAmount        = Column(Numeric(50,10))
    interestAmount         = Column(Numeric(50,10))
    feesAmount             = Column(Numeric(50,10))
    penaltyAmount          = Column(Numeric(50,10))
    reversalTransactionKey = Column(String)
    # redundant relationships camelCase
    parentAccountKey       = Column(String)

    def __repr__(self):
        return "<LoanTransaction(transactionid=%s, amount=%s, creationdate=%s, entrydate=%s, type=%s, comment='%s', reversed=%s\naccount=%s)>" % (self.transactionid, self.amount, self.creationdate.strftime('%Y%m%d'), self.entrydate.strftime('%Y%m%d'), self.type, self.comment, "Yes" if self.reversaltransactionkey else "No", self.account)
