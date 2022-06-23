from mambupy.rest.mambutransaction import MambuTransaction as MambuTransaction1
from mambupy.rest.mambutransaction import MambuTransactions as MambuTransactions1
from mambupy.rest1to2.mambustruct import MambuStruct
from mambupy.rest.mambustruct import MambuStructIterator


class MambuTransaction(MambuStruct, MambuTransaction1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MambuTransactions(MambuStruct, MambuTransactions1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuTransaction"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuTransaction1
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
