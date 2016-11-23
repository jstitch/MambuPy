"""Schema tables for Mambu Repayments.

TODO: this is just a basic schema for repayment table. Some fields
are missing.
"""

from mambupy import schema_orm as orm
from mambupy.schema_loans import LoanAccount

from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, Numeric, Integer

dbname = orm.dbname
session = orm.session
Base = orm.Base


class Repayment(Base):
    """Repayment table.
    """
    __tablename__    = "repayment"
    __table_args__   = {'schema'        : dbname,
                        'keep_existing' : True
                       }

    # Columns
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
    account          = relationship(LoanAccount, 
									backref=backref('repayments', 
									order_by='Repayment.duedate'))

    def __repr__(self):
        return "<Repayment(duedate=%s, state=%s,\naccount=%s)>" % (self.duedate.strftime('%Y%m%d'), self.state, self.account)
