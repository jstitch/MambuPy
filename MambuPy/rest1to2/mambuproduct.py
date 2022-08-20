from mambupy.rest.mambuproduct import MambuProduct as MambuProduct1
from mambupy.rest.mambuproduct import MambuProducts as MambuProducts1
from mambupy.rest1to2.mambustruct import MambuStruct
from mambupy.rest.mamburestutils import MambuStructIterator


class MambuProduct(MambuStruct, MambuProduct1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def productName(self):
        return self.wrapped2.name


class MambuProducts(MambuStruct, MambuProducts1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuProduct"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuProduct
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
