from mambupy.rest.mambuloan import MambuLoan as MambuLoan1, MambuLoans as MambuLoans1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters
from mambupy.rest.mambustruct import MambuStructIterator
from mambupy.mambuutil import getgrouploansurl, MambuError


loan_filters = ["accountState", "branchId", "centreId", "creditOfficerUsername"]


class MambuLoan(MambuStruct, MambuLoan1):
    def __init__(self, *args, **kwargs):
        if "urlfunc" in kwargs and kwargs["urlfunc"] == getgrouploansurl:
            kwargs.pop("urlfunc")
            kwargs["accountHolderType"] = "GROUP"
            kwargs["accountHolderId"] = kwargs.pop("entid")
        process_filters(loan_filters, kwargs)
        super().__init__(*args, **kwargs)

    def getDebt(self):
        self.principalBalance = self.balances["principalBalance"]
        self.interestBalance = self.balances["interestBalance"]
        self.feesBalance = self.balances["feesBalance"]
        self.penaltyBalance = self.balances["penaltyBalance"]

        return MambuLoan1.getDebt(self)

    def setBranch(self, *args, **kwargs):
        from mambupy.rest1to2 import mambubranch
        self.branch = mambubranch.MambuBranch(
            entid=self.wrapped2.assignedBranchKey, *args, **kwargs)
        self.assignedBranchName = self.branch.name
        self.assignedBranch = self.branch

        return 1

    def setCentre(self, *args, **kwargs):
        from mambupy.rest1to2 import mambucentre
        self.centre = mambucentre.MambuCentre(
            entid=self.wrapped2.assignedCentreKey, *args, **kwargs)
        self.assignedCentreName = self.centre.name
        self.assignedCentre = self.centre

        return 1

    def setUser(self, *args, **kwargs):
        from mambupy.rest1to2 import mambuuser
        try:
            self.user = mambuuser.MambuUser(
                entid=self.wrapped2.assignedUserKey, *args, **kwargs)
        except AttributeError:
            err = MambuError("La cuenta %s no tiene asignado un usuario" % self.id)
            err.noUser = True
            raise err

        return 1

    def setProduct(self, *args, **kwargs):
        from mambupy.rest1to2 import mambuproduct
        self.product = mambuproduct.MambuProduct(
            entid=self.wrapped2.productTypeKey, *args, **kwargs)

        return 1

    def setActivities(self, *args, **kwargs):
        from mambupy.rest.mambuactivity import MambuActivities

        def activity_date(activity):
            try:
                return activity["activity"]["timestamp"]
            except KeyError:
                return None
        activities = MambuActivities(loanAccountId=self.encodedKey, *args, **kwargs)
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
