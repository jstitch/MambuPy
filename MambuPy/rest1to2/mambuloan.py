from mambupy.rest.mambuloan import MambuLoan as MambuLoan1, MambuLoans as MambuLoans1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters
from mambupy.rest.mambustruct import MambuStructIterator


loan_filters = ["accountState", "branchId", "centreId", "creditOfficerUsername"]


class MambuLoan(MambuStruct, MambuLoan1):
    def __init__(self, *args, **kwargs):
        process_filters(loan_filters, kwargs)
        super().__init__(*args, **kwargs)


class MambuLoans(MambuStruct, MambuLoans1):
    def __init__(self, *args, **kwargs):
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
