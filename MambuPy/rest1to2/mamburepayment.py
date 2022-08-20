from mambupy.api.entities import MambuInstallment
from mambupy.rest.mamburepayment import MambuRepayment as MambuRepayment1
from mambupy.rest.mamburepayment import MambuRepayments as MambuRepayments1
from mambupy.rest1to2.mambustruct import MambuStruct
from mambupy.rest.mamburestutils import MambuStructIterator


class MambuRepayment(MambuStruct, MambuRepayment1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        try:
            if self.wrapped1:
                _class = self.wrapped1
            else:
                _class = self
            return _class.__class__.__name__ + " - duedate: %s" % self.dueDate.strftime(
            "%Y-%m-%d"
            )
        except KeyError:
            if self.wrapped1:
                _class = self.wrapped1
            else:
                _class = self
            return _class.__class__.__name__ + " - " + str(self.attrs)
        except AttributeError:
            if self.wrapped1:
                _class = self.wrapped1
            else:
                _class = self
            return _class.__class__.__name__ + " - len: %s" % len(self.wrapped2)
        except TypeError:
            return self.mambuclass1.__name__ + " - len: %s" % len(self.wrapped2)

    @property
    def index(self):
        return self.wrapped2.number

    @property
    def feesDue(self):
        return self.wrapped2.fee["amount"]["due"]

    @property
    def feesPaid(self):
        return self.wrapped2.fee["amount"]["paid"]

    @property
    def interestDue(self):
        return self.wrapped2.interest["amount"]["due"]

    @property
    def interestPaid(self):
        return self.wrapped2.interest["amount"]["paid"]

    @property
    def principalDue(self):
        return self.wrapped2.principal["amount"]["due"]

    @property
    def principalPaid(self):
        return self.wrapped2.principal["amount"]["paid"]

    @property
    def penaltyDue(self):
        return self.wrapped2.penalty["amount"]["due"]

    @property
    def penaltyPaid(self):
        return self.wrapped2.penalty["amount"]["paid"]


class MambuRepayments(MambuStruct, MambuRepayments1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuRepayment"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuRepayment1
        if "mambuclass2" in kwargs:
            mambuclass2 = kwargs.pop("mambuclass2")
        else:
            mambuclass2 = MambuInstallment
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1,
            mambuclass2=mambuclass2,
            *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
