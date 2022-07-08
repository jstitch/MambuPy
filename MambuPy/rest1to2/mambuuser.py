from mambupy.rest.mambuuser import MambuUser as MambuUser1, MambuUsers as MambuUsers1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters
from mambupy.rest.mambustruct import MambuStructIterator


user_filters = ["branchId"]


class MambuUser(MambuStruct, MambuUser1):
    def __init__(self, *args, **kwargs):
        process_filters(user_filters, kwargs)
        super().__init__(*args, **kwargs)


class MambuUsers(MambuStruct, MambuUsers1):
    def __init__(self, *args, **kwargs):
        if "mambuclassname" in kwargs:
            mambuclassname = kwargs.pop("mambuclassname")
        else:
            mambuclassname = "MambuUser"
        if "mambuclass1" in kwargs:
            mambuclass1 = kwargs.pop("mambuclass1")
        else:
            mambuclass1 = MambuUser
        process_filters(user_filters, kwargs)
        super().__init__(
            mambuclassname=mambuclassname,
            mambuclass1=mambuclass1, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.wrapped2)

    def __repr__(self):
        return super().__repr__()
