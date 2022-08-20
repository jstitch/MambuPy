from mambupy.rest.mambutransaction import MambuTransaction as MambuTransaction1
from mambupy.rest.mambutransaction import MambuTransactions as MambuTransactions1
from mambupy.rest1to2.mambustruct import MambuStruct
from mambupy.rest.mamburestutils import MambuStructIterator


class MambuTransaction(MambuStruct, MambuTransaction1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        if key=="transactionId":
            return self.wrapped2.id
        elif key=="entryDate":
            return self.wrapped2.valueDate
        else:
            return super().__getitem__(key)

    @property
    def transactionId(self):
        return self.wrapped2.id

    @property
    def entryDate(self):
        return self.wrapped2.valueDate


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
