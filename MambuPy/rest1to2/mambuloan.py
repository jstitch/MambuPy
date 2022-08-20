from mambupy.rest.mambuloan import MambuLoan as MambuLoan1, MambuLoans as MambuLoans1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters
from mambupy.rest.mamburestutils import MambuStructIterator
from mambupy.mambugeturl import getgrouploansurl
from mambupy.mambuutil import MambuError


loan_filters = ["accountState", "branchId", "centreId", "creditOfficerUsername"]


class MambuLoan(MambuStruct, MambuLoan1):
    DEFAULTS = {"notes": ""}

    def __init__(self, *args, **kwargs):
        if "urlfunc" in kwargs and kwargs["urlfunc"] == getgrouploansurl:
            kwargs.pop("urlfunc")
            kwargs["accountHolderType"] = "GROUP"
            kwargs["accountHolderId"] = kwargs.pop("entid")
        process_filters(loan_filters, kwargs)
        super().__init__(*args, **kwargs)

    def preprocess(self):
        from mambupy.rest1to2 import mambubranch, mambucentre, mambuuser
        from mambupy.rest1to2 import mambuclient, mambugroup
        from mambupy.rest1to2 import mambuproduct
        from mambupy.rest1to2 import mamburepayment, mambutransaction

        self.mambutransactionsclass = mambutransaction.MambuTransactions
        self.mamburepaymentclass = mamburepayment.MambuRepayment
        self.mamburepaymentsclass = mamburepayment.MambuRepayments
        self.mambuproductclass = mambuproduct.MambuProduct
        self.mambubranchclass = mambubranch.MambuBranch
        self.mambucentreclass = mambucentre.MambuCentre
        self.mambuclientclass = mambuclient.MambuClient
        self.mambugroupclass = mambugroup.MambuGroup
        self.mambuuserclass = mambuuser.MambuUser

    @property
    def principalBalance(self):
        return self.wrapped2.balances["principalBalance"]

    @property
    def interestBalance(self):
        return self.wrapped2.balances["interestBalance"]

    @property
    def feesBalance(self):
        return self.wrapped2.balances["feesBalance"]

    @property
    def feesPaid(self):
        return self.wrapped2.balances["feesPaid"]

    @property
    def penaltyBalance(self):
        return self.wrapped2.balances["penaltyBalance"]

    @property
    def penaltyPaid(self):
        return self.wrapped2.balances["penaltyPaid"]

    @property
    def repaymentInstallments(self):
        return self.wrapped2.scheduleSettings["repaymentInstallments"]

    @property
    def repaymentPeriodCount(self):
        return self.wrapped2.scheduleSettings["repaymentPeriodCount"]

    @property
    def repaymentPeriodUnit(self):
        return self.wrapped2.scheduleSettings["repaymentPeriodUnit"]

    def _get_roles(self, fullDetails=True, *args, **kwargs):
        requests = 0
        self.holder.roles = []
        for c in [r for r in self.holder.groupMembers if r.roles]:
            try:
                self.mambuclientclass
            except AttributeError:
                from mambupy.rest1to2 import mambuclient
                self.mambuclientclass = mambuclient.MambuClient

            cli = self.mambuclientclass(
                entid=c.clientKey, fullDetails=fullDetails, *args, **kwargs
            )
            for role in c.roles:
                self.holder.roles.append(
                    {"role": role.roleName, "client": cli})
            requests += 1

        return requests

    def getDebt(self):
        return MambuLoan1.getDebt(self)

    def setUser(self, *args, **kwargs):
        try:
            self.mambuuserclass
        except AttributeError:
            from mambupy.rest1to2 import mambuuser
            self.mambuuserclass = mambuuser.MambuUser

        try:
            self.user = self.mambuuserclass(
                entid=self.wrapped2.assignedUserKey, *args, **kwargs)
        except AttributeError:
            err = MambuError("Loan account %s has no assigned user" % self.id)
            err.noUser = True
            raise err

        return 1

    def setProduct(self, *args, **kwargs):
        try:
            self.mambuproductclass
        except AttributeError:
            from mambupy.rest1to2 import mambuproduct
            self.mambuproductclass = mambuproduct.MambuProduct

        self.product = self.mambuproductclass(
            entid=self.wrapped2.productTypeKey, *args, **kwargs)

        return 1

    def setTransactions(self, *args, **kwargs):
        try:
            self.mambutransactionsclass
        except AttributeError:
            from mambupy.rest1to2 import mambutransaction
            self.mambutransactionsclass = mambutransaction.mambutransactions

        def transaction_id(transaction):
            try:
                return transaction.id
            except KeyError:
                return None

        transactions = sorted(self.mambutransactionsclass(
            loanAccountId=self.id, *args, **kwargs), key=transaction_id)
        self.transactions = transactions

        return 1

    def setRepayments(self, *args, **kwargs):
        from mambupy.api.entities import MambuInstallment
        try:
            self.mamburepaymentclass
        except AttributeError:
            from mambupy.rest1to2 import mamburepayment
            self.mamburepaymentclass = mamburepayment.MambuRepayment

        def duedate(repayment):
            try:
                return repayment.dueDate
            except AttributeError:
                from datetime import datetime

                return datetime.now()

        self.wrapped2.get_schedule()
        reps = []
        for installment in self.wrapped2.schedule:
            rep = self.mamburepaymentclass(
                mambuclass2=MambuInstallment, urlfunc=None)
            rep.wrapped2 = installment
            reps.append(rep)
        reps = sorted(reps, key=duedate)
        self["repayments"] = reps

        return 1

    def setActivities(self, *args, **kwargs):
        try:
            self.mambuactivitiesclass
        except AttributeError:
            from mambupy.rest1to2 import mambuactivity
            self.mambuactivitiesclass = mambuactivity.MambuActivities

        def activity_date(activity):
            try:
                return activity["activity"]["timestamp"]
            except KeyError:
                return None
        activities = self.mambuactivitiesclass(loanAccountId=self.encodedKey, *args, **kwargs)
        activities.attrs = sorted(activities.attrs, key=activity_date)
        self["activities"] = activities

        return 1


class MambuLoans(MambuStruct, MambuLoans1):
    def __init__(self, *args, **kwargs):
        if "urlfunc" in kwargs and kwargs["urlfunc"] == getgrouploansurl:
            kwargs.pop("urlfunc")
            kwargs["accountHolderType"] = "GROUP"
            kwargs["accountHolderId"] = kwargs.pop("entid")
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuLoan"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuLoan1
        process_filters(loan_filters, kwargs)
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
